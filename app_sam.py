"""
Flask API for SAM-based Debate System
Bridges the React frontend with Solace Agent Mesh for multi-model debates.
"""

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
import requests
from threading import Thread
from queue import Queue
import time

load_dotenv()

app = Flask(
    __name__,
    static_folder="frontend/dist",
)

# Enable CORS for React frontend
CORS(app, origins=["http://localhost:5173", "http://localhost:5000", "http://127.0.0.1:5173", "http://127.0.0.1:5000"])

# SAM Gateway configuration (REST gateway on port 8080)
SAM_GATEWAY_URL = os.environ.get("SAM_GATEWAY_URL", "http://127.0.0.1:8080")

# State for tracking debates
class DebateState:
    def __init__(self):
        self.cards = []
        self.puzzle = None
        self.debate_history = Queue()
        self.debating = False
        self.current_session_id = None


debate_state = DebateState()


def _run_sam_debate(puzzle: str, cards: list):
    """Run debate through SAM gateway in background thread."""
    debate_state.debating = True
    
    try:
        # Build the prompt for the DebateOrchestrator
        cards_json = json.dumps(cards)
        
        prompt = f"""Please run a debate with the following configuration:

Puzzle: {puzzle}

Cards (participants):
{cards_json}

Run the debate and show me the full discussion."""

        # Call SAM Gateway API using /api/v1/invoke with form data
        response = requests.post(
            f"{SAM_GATEWAY_URL}/api/v1/invoke",
            data={
                "agent_name": "DebateOrchestrator",
                "prompt": prompt,
                "stream": "false"
            },
            headers={"Authorization": "Bearer None"},
            timeout=600  # 10 minute timeout for long debates
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Parse the debate result from SAM response
            status = result.get("status", {})
            message = status.get("message", {})
            parts = message.get("parts", [])
            
            for part in parts:
                if part.get("type") == "text" or part.get("kind") == "text":
                    text = part.get("text", "")
                    debate_state.debate_history.put({
                        "role": "system",
                        "message": text,
                        "colour": "#FFFFFF"
                    })
        else:
            debate_state.debate_history.put({
                "role": "error",
                "message": f"SAM Gateway error: {response.status_code} - {response.text}",
                "colour": "#FF0000"
            })
            
    except requests.exceptions.ConnectionError:
        # SAM not running - fall back to direct debate
        _run_direct_debate(puzzle, cards)
    except Exception as e:
        debate_state.debate_history.put({
            "role": "error", 
            "message": f"Error: {str(e)}",
            "colour": "#FF0000"
        })
    finally:
        debate_state.debating = False


def _run_direct_debate(puzzle: str, cards: list):
    """Run debate directly using debate_tools with real-time message streaming."""
    from src.debate_tools import run_debate_streaming
    
    colour_map = {
        "facilitator": "#DC143C",
        "critic": "#00ff00", 
        "reasoner": "#0000ff",
        "stateTracker": "#ffff00"
    }
    
    def on_message(role: str, message: str, model: str):
        """Callback for each debate message - pushes to queue immediately."""
        colour = colour_map.get(role, "#FFFFFF")
        debate_state.debate_history.put({
            "role": role,
            "message": message,
            "colour": colour,
            "model": model
        })
    
    try:
        result = run_debate_streaming(
            puzzle=puzzle, 
            cards=cards, 
            max_rounds=4,
            on_message=on_message
        )
        
        if result["status"] != "completed":
            debate_state.debate_history.put({
                "role": "error",
                "message": result.get("message", "Unknown error"),
                "colour": "#FF0000"
            })
    except Exception as e:
        debate_state.debate_history.put({
            "role": "error",
            "message": f"Direct debate error: {str(e)}",
            "colour": "#FF0000"
        })


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/deck", methods=["POST"])
def get_deck():
    """Receive the deck of cards (agent configurations) from the frontend."""
    try:
        agents = request.get_json()["agents"]
        debate_state.cards = []
        for agent in agents:
            debate_state.cards.append({
                "model": agent["model"],
                "expertise": agent["expertise"],
                "personality": agent["personality"],
                "role": agent["role"]
            })
        return "", 200
    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400


@app.route("/api/puzzle", methods=["POST"])
def get_puzzle():
    """Start a debate - tries SAM first, falls back to direct."""
    if debate_state.debating:
        return jsonify({"error": "Debate already in progress"}), 409

    try:
        puzzle = request.get_json()["puzzle"]
        debate_state.puzzle = puzzle
        
        if not debate_state.cards:
            return jsonify({"error": "No cards configured. Call /api/deck first."}), 400
        
        # Start debate in background thread - SAM with fallback to direct
        thread = Thread(
            target=_run_sam_debate,  # Try SAM first, falls back to direct if unavailable
            args=(puzzle, debate_state.cards)
        )
        thread.start()
        
        return "", 200
    except KeyError:
        return jsonify({"error": "Missing puzzle field"}), 400


@app.route("/api/puzzle/sam", methods=["POST"])
def get_puzzle_sam():
    """Start a debate through SAM gateway (requires SAM to be running)."""
    if debate_state.debating:
        return jsonify({"error": "Debate already in progress"}), 409

    try:
        puzzle = request.get_json()["puzzle"]
        debate_state.puzzle = puzzle
        
        if not debate_state.cards:
            return jsonify({"error": "No cards configured. Call /api/deck first."}), 400
        
        # Start SAM debate in background thread
        thread = Thread(
            target=_run_sam_debate,
            args=(puzzle, debate_state.cards)
        )
        thread.start()
        
        return "", 200
    except KeyError:
        return jsonify({"error": "Missing puzzle field"}), 400


@app.route("/api/sync", methods=["GET"])
def sync():
    """Poll for new messages in the debate."""
    msg = ""
    colour = ""
    role = ""

    try:
        entry = debate_state.debate_history.get_nowait()
        msg = entry.get("message", "")
        colour = entry.get("colour", "#FFFFFF")
        role = entry.get("role", "")
    except:
        pass

    return jsonify({
        "text": msg,
        "colour": colour,
        "role": role,
        "debating": debate_state.debating
    })


@app.route("/api/status", methods=["GET"])
def status():
    """Get current debate status."""
    return jsonify({
        "debating": debate_state.debating,
        "cards_configured": len(debate_state.cards),
        "puzzle": debate_state.puzzle,
        "sam_gateway_url": SAM_GATEWAY_URL
    })


@app.route("/api/reset", methods=["POST"])
def reset():
    """Reset the debate state."""
    debate_state.cards = []
    debate_state.puzzle = None
    # Clear the queue
    while not debate_state.debate_history.empty():
        try:
            debate_state.debate_history.get_nowait()
        except:
            break
    debate_state.debating = False
    return "", 200


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    print("=" * 60)
    print("SAM-Integrated Debate Server")
    print("=" * 60)
    print(f"Flask API: http://localhost:5000")
    print(f"SAM Gateway: {SAM_GATEWAY_URL}")
    print("")
    print("Endpoints:")
    print("  POST /api/deck   - Configure debate participants")
    print("  POST /api/puzzle - Start debate (direct, no SAM needed)")
    print("  POST /api/puzzle/sam - Start debate through SAM")
    print("  GET  /api/sync   - Poll for debate messages")
    print("  GET  /api/status - Get debate status")
    print("  POST /api/reset  - Reset debate state")
    print("=" * 60)
    
    app.run(debug=True, port=5000, host="0.0.0.0")
