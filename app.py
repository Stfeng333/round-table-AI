from flask import Flask, send_from_directory, request, jsonify
from dotenv import load_dotenv
import pymongo
import traceback

from card import Card
from llms import Qwen3, Llama33, Gpt41, Gemini3Flash, KimiK2


cards = []

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

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)


@app.route("/llm/qwen3/chat/completions", methods=["POST"])
def llm_qwen3():
    try:
        data = request.get_json()
        messages = data.get("messages", [])
        
        # Extract system instructions if present
        instructions = ""
        user_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                instructions = msg.get("content", "")
            elif msg.get("role") == "user":
                user_messages.append(msg.get("content", ""))
        
        llm = Qwen3(instructions=instructions)
        
        # Get response for the last user message
        if user_messages:
            response_text = llm.get_response(user_messages[-1])
        else:
            response_text = ""
        
        # Return OpenAI-style response format
        return jsonify({
            "id": "chatcmpl-qwen3",
            "object": "chat.completion",
            "model": "qwen/qwen3-32b",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }]
        })
    except Exception as e:
        print(f"LLM Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/llm/llama/chat/completions", methods=["POST"])
def llm_llama():
    try:
        data = request.get_json()
        messages = data.get("messages", [])
        
        # Extract system instructions if present
        instructions = ""
        user_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                instructions = msg.get("content", "")
            elif msg.get("role") == "user":
                user_messages.append(msg.get("content", ""))
        
        llm = Llama33(instructions=instructions)
        
        # Get response for the last user message
        if user_messages:
            response_text = llm.get_response(user_messages[-1])
        else:
            response_text = ""
        
        # Return OpenAI-style response format
        return jsonify({
            "id": "chatcmpl-Llama33",
            "object": "chat.completion",
            "model": "Llama33",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }]
        })
    except Exception as e:
        print(f"LLM Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500



@app.route("/llm/gpt41/chat/completions", methods=["POST"])
def llm_gpt41():
    try:
        data = request.get_json()
        messages = data.get("messages", [])
        
        # Extract system instructions if present
        instructions = ""
        user_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                instructions = msg.get("content", "")
            elif msg.get("role") == "user":
                user_messages.append(msg.get("content", ""))
        
        llm = Gpt41(instructions=instructions)
        
        # Get response for the last user message
        if user_messages:
            response_text = llm.get_response(user_messages[-1])
        else:
            response_text = ""
        
        # Return OpenAI-style response format
        return jsonify({
            "id": "Gpt41",
            "object": "chat.completion",
            "model": "Gpt41",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }]
        })
    except Exception as e:
        print(f"LLM Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500 
    
    
    
    
    
@app.route("/llm/gemini/chat/completions", methods=["POST"])
def llm_gemini():
    try:
        data = request.get_json()
        messages = data.get("messages", [])
        
        # Extract system instructions if present
        instructions = ""
        user_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                instructions = msg.get("content", "")
            elif msg.get("role") == "user":
                user_messages.append(msg.get("content", ""))
        
        llm = Gemini3Flash(instructions=instructions)
        
        # Get response for the last user message
        if user_messages:
            response_text = llm.get_response(user_messages[-1])
        else:
            response_text = ""
        
        # Return OpenAI-style response format
        return jsonify({
            "id": "chatcmpl-gemini",
            "object": "chat.completion",
            "model": "gemini",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }]
        })
    except Exception as e:
        print(f"LLM Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
    

@app.route("/llm/kimi/chat/completions", methods=["POST"])
def llm_kimi():
    try:
        data = request.get_json()
        messages = data.get("messages", [])
        
        # Extract system instructions if present
        instructions = ""
        user_messages = []
        for msg in messages:
            if msg.get("role") == "system":
                instructions = msg.get("content", "")
            elif msg.get("role") == "user":
                user_messages.append(msg.get("content", ""))
        
        llm = KimiK2(instructions=instructions)
        
        # Get response for the last user message
        if user_messages:
            response_text = llm.get_response(user_messages[-1])
        else:
            response_text = ""
        
        # Return OpenAI-style response format
        return jsonify({
            "id": "chatcmpl-KimiK2",
            "object": "chat.completion",
            "model": "qwen/KimiK2-32b",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }]
        })
    except Exception as e:
        print(f"LLM Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
