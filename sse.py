# filename: solace_sse_client.py

import requests
import json
import sseclient
from typing import Dict, Optional, Generator

# -------- CONFIGURATION -------- #
GATEWAY_URL = "http://localhost:8000"  # Change to your HTTP SSE Gateway URL
# ------------------------------- #

def create_session() -> str:
    """
    Create a new session with the SSE Gateway.
    Returns a session_id string.
    """
    url = f"{GATEWAY_URL}/session"
    resp = requests.post(url, headers={"Content-Type": "application/json"})
    resp.raise_for_status()
    data = resp.json()
    return data.get("session_id")


def send_task(
    session_id: str,
    prompt: str,
    target_agent: Optional[str] = None,
    meta: Optional[Dict] = None
) -> Dict:
    """
    Send a task to one or multiple agents.
    :param session_id: existing session ID
    :param prompt: task / instruction text
    :param target_agent: optional agent name; broadcast to multiple if using shared topic
    :param meta: optional metadata dict (turn, correlation_id, etc.)
    :return: response from gateway (status)
    """
    url = f"{GATEWAY_URL}/message"
    payload = {
        "session_id": session_id,
        "type": "task",
        "payload": {"text": prompt},
    }

    if target_agent:
        payload["target"] = target_agent
    if meta:
        payload["meta"] = meta

    resp = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
    resp.raise_for_status()
    return resp.json()


def stream_events(session_id: str) -> Generator[Dict, None, None]:
    """
    Open SSE stream for a session and yield agent events as dictionaries.
    :param session_id: session to listen to
    :yield: dict representing each event (agent_thought, agent_action, etc.)
    """
    url = f"{GATEWAY_URL}/events?session_id={session_id}"
    with requests.get(url, stream=True, headers={"Accept": "text/event-stream"}) as resp:
        resp.raise_for_status()
        client = sseclient.SSEClient(resp)
        for event in client.events():
            if event.data:
                try:
                    yield json.loads(event.data)
                except json.JSONDecodeError:
                    # fallback: return raw string if JSON parsing fails
                    yield {"raw": event.data, "event": event.event}


# -------- Example usage -------- #
if __name__ == "__main__":
    # Create a session
    session_id = create_session()
    print(f"Session created: {session_id}")

    # Send a task to all agents subscribed to 'agent/task/team'
    send_task(
        session_id=session_id,
        prompt="Analyze current game state and propose next moves for the team",
        target_agent="agent.team",
        meta={"turn": 1, "correlation_id": "task-001"}
    )
    print("Task sent.")

    # Stream events and print them as they come
    print("Streaming agent events:")
    for event in stream_events(session_id):
        agent = event.get("agent", "unknown")
        content = event.get("content") or event.get("result") or str(event)
        print(f"[{agent}] {content}")
