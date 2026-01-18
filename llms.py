import os
import re
from abc import ABC, abstractmethod

from groq import Groq
from google import genai
import requests
from openai import OpenAI


class Llm(ABC):
    """
    Each model has their own object. For example, Gpt41 for gpt-4.1

    ModelObject(instructions: str = "")

    parameters:
        instructions: context given to model in the beginning

    methods:
        init() -> None: call before use
        clear_context() -> None: wipe chat history
        get_response() -> str: send a message and receive a response, added to chat history (context)
    """

    def __init__(self, instructions):
        self.client = None

        # initial context given to models
        self.instructions = instructions

    @abstractmethod
    def clear_context(self):
        pass

    @abstractmethod
    def add_context(self, msg):
        pass

    @abstractmethod
    def init(self): ...

    @abstractmethod
    def get_response(self, prompt): ...


class Gpt41(Llm):
    def __init__(self, instructions=""):
        super().__init__(instructions)

        self._instructions = instructions
        self._messages = []

        self.init()

    def add_context(self, msg):
        self._messages.append(msg)

    def clear_context(self):
        self._messages.clear()

    def _construct_context(self):
        context = (
            [{"role": "developer", "content": self._instructions}]
            if self._instructions
            else []
        )
        context += [{"role": "user", "content": m} for m in self._messages]
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

    def add_context(self, msg):
        self._messages.append(msg)

    def clear_context(self):
        self._messages.clear()

    def _construct_context(self):
        context = (
            [{"role": "system", "content": self._instructions}]
            if self._instructions
            else []
        )
        context += [{"role": "user", "content": m} for m in self._messages]
        return context

    def get_response(self, prompt):
        self._messages.append(prompt)

        chat_completion = self.client.chat.completions.create(
            messages=self._construct_context(),
            model=self.groq_model,
        )

        # remove the thinking shit
        return re.sub(
            r"<think>[\s\S]*?</think>", "", chat_completion.choices[0].message.content
        )


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

        self._added_context = []

        self.init()

    def clear_context(self):
        self.chat = self.client.chats.create(model="gemini-3-flash-preview")

    def add_context(self, msg):
        self._added_context.append(msg)

    def init(self):
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

        # creates a new chat object, prevents duplication of code even
        # if it's semantically weird
        self.clear_context()

    def get_response(self, prompt):
        response = self.chat.send_message(
            "\n".join(self._added_context) + "\n" + prompt
        )
        self._added_context.clear()

        return response.text


# DeepSeek subclass
class DeepSeek(Llm):
    def __init__(self, instructions=""):
        super().__init__(instructions)

        self._instructions = instructions
        self._messages = []
        self.client = None

        self.init()

    def clear_context(self):
        self._messages.clear()

    def init(self):
        # Option 1: Using OpenAI SDK (recommended if it works)
        try:
            self.client = OpenAI(
                api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url="https://api.deepseek.com",
            )
        except:
            # If OpenAI SDK doesn't work with base_url, we'll use requests
            self.client = None

    def _construct_context(self):
        """Build the messages array in proper format"""
        messages = []
        if self._instructions:
            messages.append({"role": "system", "content": self._instructions})

        # Add conversation history
        # Note: We need to track both user and assistant messages
        for msg in self._messages:
            messages.append(msg)

        return messages

    def get_response(self, prompt):
        # Add user message to history
        self._messages.append({"role": "user", "content": prompt})

        # Try using OpenAI SDK first
        if self.client is not None:
            try:
                response = self.client.chat.completions.create(
                    model="deepseek-chat",
                    messages=self._construct_context(),
                    stream=False,
                )
                ai_response = response.choices[0].message.content
                self._messages.append({"role": "assistant", "content": ai_response})
                return ai_response
            except Exception as e:
                print(f"OpenAI SDK failed, falling back to requests: {e}")
                self.client = None

        # Fallback to requests
        return self._get_response_requests(prompt)

    def _get_response_requests(self, prompt):
        """Direct requests implementation"""
        URL = "https://api.deepseek.com/chat/completions"
        API_KEY = os.environ["DEEPSEEK_API_KEY"]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        }

        data = {
            "model": "deepseek-chat",
            "messages": self._construct_context(),
            "stream": False,
        }

        try:
            response = requests.post(URL, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()

            ai_response = result["choices"][0]["message"]["content"]
            self._messages.append({"role": "assistant", "content": ai_response})

            return ai_response

        except requests.exceptions.RequestException as e:
            return f"Error: {e}"
        except KeyError as e:
            return f"Unexpected API response format: {e}"
    def add_context(self, msg):
        return super().add_context(msg)


# Implementing OpenRouter subclass
OPENROUTER_MODELS = {
    "llama": [
        "meta-llama/llama-3.1-8b-instruct",
        "meta-llama/llama-3-8b-instruct",
    ],
    "mistral": [
        "mistralai/mistral-7b-instruct",
        "mistralai/mixtral-8x7b-instruct",
    ],
    "gpt": [
        "openai/gpt-4o-mini",
    ],
    "gemini": [
        "google/gemma-2-27b-it",
        "google/gemma-2-9b-it",
    ],
}

import random


class OpenRouter(Llm):
    def __init__(self, provider, instructions="", model=None):
        super().__init__(instructions)

        self.provider = provider

        if model:
            self.model = model
        else:
            if provider not in OPENROUTER_MODELS:
                raise ValueError(f"Unknown OpenRouter provider: {provider}")
            self.model = random.choice(OPENROUTER_MODELS[provider])

        self._instructions = instructions
        self._messages = []

        self.init()

    def init(self):
        self.client = OpenAI(
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "http://localhost",
                "X-Title": "AI Deck Builder",
            },
        )

    def clear_context(self):
        self._messages.clear()

    def _construct_context(self):
        messages = []
        if self._instructions:
            messages.append({"role": "system", "content": self._instructions})
        messages.extend(self._messages)
        return messages

    def get_response(self, prompt):
        self._messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self._construct_context(),
        )

        ai_response = response.choices[0].message.content
        self._messages.append({"role": "assistant", "content": ai_response})

        return ai_response

    def add_context(self, msg):
        return super().add_context(msg)


# for testing
if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    
    client = GptOss(instructions="It's opposite day")
    print(client.get_response("i love red"))
    print(client.get_response("what colour do I love"))

    # DeepSeek tests
    ds = DeepSeek(instructions="You are a helpful assistant")
    print("DeepSeek Test 1:", ds.get_response("Hello! What's 2+2?"))
    print("DeepSeek Test 2:", ds.get_response("Now what's 3+3? (Remember the context)"))
    ds.clear_context()
    print("DeepSeek Test 3 (after clear):", ds.get_response("What was 2+2?"))


    # OpenRouter provider-based tests
    or_llama = OpenRouter(provider="llama", instructions="It's opposite day")

    print("Llama 1:", or_llama.get_response("I love red"))
    print("Llama 2:", or_llama.get_response("What colour do I love?"))


    or_mistral = OpenRouter(provider="mistral", instructions="Answer very briefly")

    print("Mistral:", or_mistral.get_response("Explain gravity in one sentence"))


    or_gpt = OpenRouter(provider="gpt", instructions="Be very skeptical")

    print("GPT:", or_gpt.get_response("Is this argument logically valid?"))


    or_gemini = OpenRouter(provider="gemini", instructions="Track facts carefully")

    print(
        "Gemini:",
        or_gemini.get_response("Alice has 3 apples, gives 1 away. How many left?"),
    )
