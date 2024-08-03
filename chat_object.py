from langchain.schema import HumanMessage, SystemMessage, AIMessage

class TypedMessage:
    def __init__(self, content: str, type_: str):
        self.content = content
        self.type_ = type_
    
    @classmethod
    def from_json(self, json_dict: dict):
        return TypedMessage(json_dict['content'], json_dict['type'])
    
    def to_langchain_schema(self):
        match self.type_.lower():
            case "human":
                return HumanMessage(self.content)
            case "system":
                return SystemMessage(self.content)
            case "ai":
                return AIMessage(self.content)
        return SystemMessage(self.content)
    
    @classmethod
    def for_map_to_langchain_schema(self, obj):
        return obj.to_langchain_schema()

class Chat(list):
    def __init__(self, messages: list, name: str, _id: str):
        super().__init__()
        self += messages
        self.name = name
        self._id = _id

    @classmethod
    def from_json(self, json_dict: dict):
        messages = list(map(TypedMessage.for_map_to_langchain_schema, list(map(TypedMessage.from_json, json_dict['messages']))))
        return Chat(messages, json_dict['name'], json_dict['_id'])

    def to_json(self):
        msgs = []
        for msg in self:
            if isinstance(msg, HumanMessage):
                msgs.append({"content": msg.content, "type": "human"})
            elif isinstance(msg, SystemMessage):
                msgs.append({"content": msg.content, "type": "system"})
            elif isinstance(msg, AIMessage):
                msgs.append({"content": msg.content, "type": "ai"})
            else:
                msgs.append({"content": msg.content, "type": "system"})
        return {"name": self.name, "messages": msgs, "_id": self._id}
    
    def writeToAi(self, msg: str, floppa):
        self.append(HumanMessage(msg))
        aim = floppa.neural(self)
        self.append(aim)
        return aim.content