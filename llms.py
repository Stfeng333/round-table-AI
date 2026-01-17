import os
from abc import ABC, abstractmethod
import google.generativeai as genai
import requests
import json
from openai import OpenAI


class Llm(ABC):
    def __init__(self, instructions):
        self.client = None

        # initial context given to models
        self.instructions = instructions

    @abstractmethod
    def init(self):
        ...

    @abstractmethod
    def get_response(self, prompt):
        ...

class Gpt4(Llm):
    def __init__(self, instructions=""):
        super().__init__(instructions)

        self.init()

    def init(self):
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def get_response(self, prompt):
        response = self.client.responses.create(
            model="gpt-4o",
            instructions=self.instructions,
            input=prompt
        )
        return response.output[0].content[0].text

class Gemini(Llm):
    def __init__(self, instructions=""):
        super().__init__(instructions)
        self.init()

    def init(self):
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instructions=self.instructions or None
        )
    def get_response(self, prompt):
        reponse = self.model.generate_content(prompt)
        return reponse.text

class DeepSeek(Llm):
    def __init__(self, instructions=""):
        super().__init__(instructions)
        self.init()

    def init(self):
        self.api_key = os.environ["DEEPSEEK_API_KEY"]
        self.url = "https://api.deepseek.com/chat/completions"
    
    def get_response(self, prompt):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer{self.api_key}"
        }

        messages = []
        if self.instructions:
            messages.append({"role": "system", "content": self.instructions})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "steam":False
        }

        response = requests.post(self.url, headers=headers, json=data)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


# for testing
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    client = Gpt4()
    print(client.get_response("hello"))
