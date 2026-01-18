import os
from abc import ABC, abstractmethod

from groq import Groq
from google import genai
import requests
from openai import OpenAI


class Llm(ABC):
    '''
    Each model has their own object. For example, Gpt41 for gpt-4.1

    ModelObject(instructions: str = "")

    parameters:
        instructions: context given to model in the beginning

    methods:
        init() -> None: call before use
        clear_context() -> None: wipe chat history
        get_response() -> str: send a message and receive a response, added to chat history (context)
    '''

    def __init__(self, instructions):
        self.client = None

        # initial context given to models
        self.instructions = instructions

    @abstractmethod
    def clear_context(self):
        pass

    @abstractmethod
    def init(self):
        ...

    @abstractmethod
    def get_response(self, prompt):
        ...

class Gpt41(Llm):
    def __init__(self, instructions=""):
        super().__init__(instructions)

        self._instructions = instructions
        self._messages = []

        self.init()

    def clear_context(self):
        self._messages.clear()

    def _construct_context(self):
        context = [{"role":"developer", "content":self._instructions}] if self._instructions else []
        context += [{"role":"user", "content":m} for m in self._messages]
        return context

    def init(self):
        self.client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def get_response(self, prompt):
        self._messages.append(prompt)

        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=self._construct_context(),
        )
        return response.choices[0].message.content

class GroqModel(Llm, ABC):
    def __init__(self, model, instructions):
        super().__init__(instructions)

        self._messages = []
        self._instructions = instructions
        self.groq_model = model

        self.init()

    def init(self):
        self.client = Groq(api_key=os.environ["GROQ_API_KEY"])

    def clear_context(self):
        self._messages.clear()

    def _construct_context(self):
        context = [{"role":"system", "content":self._instructions}] if self._instructions else []
        context += [{"role":"user", "content":m} for m in self._messages]
        return context

    def get_response(self, prompt):
        self._messages.append(prompt)

        chat_completion = self.client.chat.completions.create(
            messages=self._construct_context(),
            model=self.groq_model,
        )
        return chat_completion.choices[0].message.content

class KimiK2(GroqModel):
    def __init__(self, instructions=""):
        super().__init__("moonshotai/kimi-k2-instruct-0905", instructions)

        self.init()

class GptOss(GroqModel):
    def __init__(self, instructions=""):
        super().__init__("openai/gpt-oss-120b", instructions)

        self.init()

class Qwen3(GroqModel):
    def __init__(self, instructions=""):
        super().__init__("qwen/qwen3-32b", instructions)

        self.init()

class Llama33(GroqModel):
    def __init__(self, instructions=""):
        super().__init__("llama-3.3-70b-versatile", instructions)

        self.init()

class Gemini3Flash(Llm):
    def __init__(self, instructions=""):
        super().__init__(instructions)

        self.chat = None

        self.init()

    def clear_context(self):
        self.chat = self.client.chats.create(model="gemini-3-flash-preview")

    def init(self):
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

        # creates a new chat object, prevents duplication of code even
        # if it's semantically weird
        self.clear_context()

    def get_response(self, prompt):
        response = self.chat.send_message(prompt)

        return response.text


# does not work properly
class DeepSeek(Llm):
    def __init__(self, instructions=""):
        super().__init__(instructions)

        self.init()

    # must be implemented
    def init(self):
        pass

    def get_response(self, prompt):
        URL = "https://api.deepseek.com/chat/completions"
        API_KEY = os.environ["DEEPSEEK_API_KEY"]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer{API_KEY}"
        }

        messages = []
        if self.instructions:
            messages.append({"role": "system", "content": self.instructions})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "steam": False
        }

        response = requests.post(URL, headers=headers, json=data)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]


# for testing
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    client = GptOss(instructions="It's opposite day")
    print(client.get_response("i love red"))
    print(client.get_response("what colour do I love"))
