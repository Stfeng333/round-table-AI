from flask import Flask, send_from_directory, request, jsonify
from dotenv import load_dotenv

from reasoning import GameState
from card import Card

game_state = GameState()

load_dotenv()


app = Flask(
    __name__,
    static_folder="frontend/dist",
)

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/deck", methods=["POST"])
def get_deck():
    data = request.get_json(silent=True)
    if not data or "agents" not in data:
        return jsonify({"error": "missing 'agents' in JSON body"}), 400

    agents = data["agents"]
    if not isinstance(agents, list):
        return jsonify({"error": "'agents' must be a list"}), 400

    for agent in agents:
        if not isinstance(agent, dict):
            return jsonify({"error": "each agent must be an object"}), 400

        model = agent.get("model")
        expertise = agent.get("expertise")
        personality = agent.get("personality")
        role = agent.get("role")

        if not all([model, expertise, personality, role]):
            return jsonify({"error": "agent missing required fields"}), 400

        game_state.cards.append(Card(model, expertise, personality, role))

    return "", 200

@app.route("/api/puzzle", methods=["POST"])
def get_puzzle():
    if game_state.debating:
        return "", 301

    try:
        game_state.puzzle = request.get_json()["puzzle"]
        game_state.start_debate()
    except KeyError:
        return "", 400

    return "", 200
# this endpoint will get polled by frontend to pull new messages in the debate
@app.route("/api/sync", methods=["GET"])
def sync():
    # if msg is empty frontend will ignore it
    msg = ""
    colour = ""

    try:
        card, msg = game_state.debate_history.pop(0)
        colour = {"facilitator": "#DC143C",
                  "critic": "#00ff00",
                  "reasoner": "#0000ff",
                  "stateTracker": "#ffff00"}[card.role]
    except IndexError:
        pass

    return jsonify({
        "text": msg,
        "colour": colour,
    })

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
