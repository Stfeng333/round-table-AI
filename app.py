from flask import Flask, send_from_directory, request
from dotenv import load_dotenv
import pymongo


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
    print(request.get_json())

    return "hello world"

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)




if __name__ == "__main__":
    app.run(debug=True, port=5000)
