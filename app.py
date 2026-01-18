import random

from flask import Flask, send_from_directory, request, jsonify
from dotenv import load_dotenv
import pymongo

from card import Card


cards = []
puzzle = None

mongo_client = pymongo.MongoClient("mongo", 27017)

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
    try:
        agents = request.get_json()["agents"]
        for agent in agents:
            cards.append(Card(agent["model"],
                              agent["expertise"],
                              agent["personality"],
                              agent["role"]))
    except KeyError:
        return "", 400

    return "", 200

@app.route("/api/puzzle", methods=["POST"])
def get_puzzle():
    global puzzle

    try:
        puzzle = request.get_json()["puzzle"]
    except KeyError:
        return "", 400

    return "", 200

@app.route("/api/sync", methods=["GET"])
def sync():
    return jsonify({"text": str(random.randint(0, 100000))})

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
