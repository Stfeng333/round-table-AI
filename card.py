'''
See frontend/src/pages/CardSelect.jsx for lists of models, expertises, personalities and roles
'''

from llms import *

class Card:
    def __init__(self, model: str, expertise: str, personality: str, role: str):
        self.model = model
        self.expertise = expertise
        self.personality = personality
        self.role = role

        clients = {"Gemini": Gemini3Flash,
                   "Llama": Llama33,
                   "Qwen" :Qwen3,
                   "ChatGPT": GptOss,
                   "Kimi": KimiK2}

        roles = {"critic": "Be critical and analytical of your teammates' contributions. Your goal is to achieve the team's objective of solving the puzzle by pushing your team to think of new ideas and challenging current ones.",
                 "facilitator": "You are making the final decision - the solution that will solve the puzzle. That is your main focus. Listen to your teammates, but be decisive. VERY IMPORTANT: whenever you speak, end with one of the following: 'We need more discussion' or 'That is the answer.'. This is EXTREMELY important. Whatever you do, do not end with something other than this.",
                 "reasoner": "Provide input on what you think the solution is. In all situations, contribute the most logical ideas that will help your team solve the puzzle.",
                 "stateTracker": "Your job is not to reason, but to keep your teammates in check. Pay close attention to everything that's being discussed to make sure none of your teammates are fabricating facts. If that happens, remind them of the facts to guide them back on track."
                 }

        self.client = clients[self.model](
            f'''
            You are part of an elite reasoning team whose objective is to solve puzzles.
            You will all take turns adding to the discussion. Work together to solve the problem. Once everyone has gone,
            the facilitator will decide if there should be another round of discussion.
            Your role is {self.role}. {roles[self.role]} Your personality is {self.personality}. Your expertise is {self.expertise}.
            During discussion, act as someone with your personality and expertise would act. Be super concise in your speech. Try your best to go under 600 chars.
            Everytime you speak, let everyone know your role in the following format : 'I am the <role>', where role is one of the following: state tracker, facilitator, reasoner, or critic. And remember, don't break character.
            Follow the rules, work together, and support the facilitator until they can deliver the solution.
            Before you are told to speak, you will be given the conversation that is currently unfolding. Don't hallucinate please.
            '''
        )