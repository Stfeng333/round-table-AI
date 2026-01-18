import random
import time


class GameState:
    def __init__(self):
        self.cards = []
        self.puzzle = None

        # [(Card, message)]
        self.debate_history = []

        self.debating = False

    def start_debate(self):
        self.debating = True

        for card in self.cards:
           print(f"{card.role}, {card.model}, {card.personality}, {card.expertise}")

        index = -1
        for i, card in enumerate(self.cards):
            if card.role == "facilitator":
                index = i
                break
        facilitator = self.cards.pop(index)

        for card in self.cards:
            card.client.add_context("The puzzle is: " + self.puzzle)

        # set a limit of 10 round robins
        for i in range(4):
            random.shuffle(self.cards)
            for card in self.cards:
                print("requesting " + card.model)

                try:
                    response = card.client.get_response("It is now your turn to speak.")
                except Exception as e:
                   print("something went wrong" + str(e))
                else:
                    self._share_context(response, card)
                    facilitator.client.add_context(response)

                time.sleep(0.5)

                print(card.model + " responded")

            try:
                response = facilitator.client.get_response("It is now your turn to speak.")
            except Exception as e:
                print("something went wrong " + str(e))
            else:
                self._share_context(response, facilitator)

                if "that is the answer" in response.lower():
                    print("done, breaking")
                    break

            time.sleep(0.5)

        self.debating = False

    def _share_context(self, msg: str, card):
        for other_card in self.cards:
            if card is not other_card:
                other_card.client.add_context(msg)

        self.debate_history.append((card, msg))