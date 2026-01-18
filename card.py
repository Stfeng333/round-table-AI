'''
See frontend/src/pages/CardSelect.jsx for lists of models, expertises, personalities and roles
'''


class Card:
    def __init__(self, model: str, expertise: str, personality: str, role: str):
        self.model = model
        self.expertise = expertise
        self.personality = personality
        self.role = role
