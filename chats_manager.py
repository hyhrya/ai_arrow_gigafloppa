import json
import uuid

import chat_object

from langchain.schema import SystemMessage, HumanMessage

class ChatsManager:
    def __init__(self, floppa):
        self.floppa = floppa
        self.chats = json.load(open("chats.json"))

    def __call__(self): json.dump(self.chats, open("chats.json", 'w'))

    def getChats(self, u_id: str):
        u_id = str(u_id)
        if not u_id in self.chats.keys():
            self.chats[u_id] = []
            return False, []
        chats = list(map(chat_object.Chat.from_json, self.chats[u_id]))
        return True, chats
    
    def writeToAi(self, u_id: str, chat: chat_object.Chat, msg: str):
        answ = chat.writeToAi(msg, self.floppa)
        u_id = str(u_id)
        chats = self.getChats(u_id)[1]
        for i in range(len(chats)):
            if chats[i]._id == chat._id:
                self.chats[u_id][i] = chat.to_json()
        self()
        return answ
    
    def newChat(self, u_id: str, msg: str):
        u_id = str(u_id)
        chat = chat_object.Chat(
            [
                SystemMessage(open("null_prompt.txt", 'r', encoding="utf-8").read()),
            ],
            self.floppa.neural.generateName(msg),
            str(uuid.uuid4())
        )
        answ = chat.writeToAi(msg, self.floppa)
        if not u_id in self.chats.keys():
            self.chats[u_id] = []
        self.chats[u_id].append(chat.to_json())
        self()
        return answ, chat
    
    def findInChatsById(self, u_id: str, _id: str):
        if not u_id in self.chats.keys(): return False, None
        for cht in self.chats[u_id]:
            if _id == cht['_id']: return True, chat_object.Chat.from_json(cht)
        return False, None
        