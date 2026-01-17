import os
from abc import ABC, abstractmethod

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


# for testing
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    client = Gpt4()
    print(client.get_response("hello"))
