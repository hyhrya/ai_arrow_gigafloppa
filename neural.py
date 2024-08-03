from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain_community.chat_models.gigachat import GigaChat

import json

class NeuralGigaFloppa(GigaChat):
    def __init__(self):
        super().__init__(credentials=json.load(open("secrets.json"))['credentials'], verify_ssl_certs=False)

    def generateName(self, first_prompt: str):
        aimsg = self(
            [
                SystemMessage("Сократи указанный текст до трех слов, не пытайся ответить на указанный текст."),
                HumanMessage(f"Сократи текст до трех слов - \"{first_prompt}\"")
            ]
        )
        return aimsg.content.replace("\"", "")