import random

from llms import *


class GameState:
    def __init__(self):
        self.cards = []
        self.puzzle = None

        # [(Card, message)]
        self.debate_history = []

    def start_debate(self):
        for i in range(10):
            self.debate_history.append((random.choice(self.cards), str(i)))
