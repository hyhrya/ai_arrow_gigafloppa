from telebot.async_telebot import AsyncTeleBot
import telebot.types as tbt

import json
import asyncio

import neural
import chats_manager
import chat_object

class MegaSuperGigaFloppa(AsyncTeleBot):
    def __init__(self):
        super().__init__(json.load(open("secrets.json"))['telebot'])
        self.neural = neural.NeuralGigaFloppa()
        self.chats_manager = chats_manager.ChatsManager(self)
        self.selected_chat = {}

    def genSelChat(self, u_id: str):
        u_id = str(u_id)
        if not u_id in self.selected_chat.keys():
            self.selected_chat[u_id] = "NEW"

bot = MegaSuperGigaFloppa()

@bot.message_handler(["start"])
async def c_start(msg: tbt.Message):
    await bot.send_message(msg.chat.id, "Привет! Я твой помощник! Воспользуйся командой /chats для того чтобы посмотреть список своих чатов, или просто напиши для нового чата")

@bot.message_handler(["chats"])
async def c_chats(msg: tbt.Message):
    bot.genSelChat(msg.chat.id)
    status, chats = bot.chats_manager.getChats(msg.chat.id)
    if not status:
        await bot.send_message(msg.chat.id, "У тебя еще нет чатов, ты можешь написать боту чтобы создать новый!")
        return
    await generateChatsList(msg.chat.id, 0, chats)

PER_PAGE = 8
async def generateChatsList(chat_id: str, page: int, chats: list | None = None, msgId: int | str | None = None):
    if not chats:
        status, chats = bot.chats_manager.getChats(chat_id)
        if not status:
            await bot.send_message(chat_id, "У тебя еще нет чатов, ты можешь написать боту чтобы создать новый!")
            return
    pages = (len(chats)//PER_PAGE)
    if page > pages: page = pages
    mk = tbt.InlineKeyboardMarkup()
    seq = chats[PER_PAGE*page : PER_PAGE*(page+1) if page != pages else len(chats)]
    for cht in seq:
        mk.add(tbt.InlineKeyboardButton(
            cht.name,
            callback_data=f"switch_chat.{cht._id}"
        ))
    nav_btns = []
    if not page == 0: nav_btns.append(tbt.InlineKeyboardButton("<<<", callback_data=f"chats_list.{page-1}"))
    if not page == pages: nav_btns.append(tbt.InlineKeyboardButton(">>>", callback_data=f"chats_list.{page+1}"))
    if nav_btns: mk.add(*nav_btns)
    mk.add(tbt.InlineKeyboardButton("> Новый чат <", callback_data="switch_chat.NEW"))
    if msgId is None: await bot.send_message(chat_id, "Ты можешь выбрать существующий чат или начать новый", reply_markup=mk)
    else: await bot.edit_message_text("Ты можешь выбрать существующий чат или начать новый", chat_id, msgId, reply_markup=mk)

@bot.callback_query_handler(lambda call: call.data.split(".")[0] == "chats_list")
async def call_chats_list(call: tbt.CallbackQuery):
    data = call.data.split(".")
    await generateChatsList(call.message.chat.id, int(data[1]), msgId=call.message.id)

@bot.callback_query_handler(lambda call: call.data.split(".")[0] == "switch_chat")
async def call_switch_chat(call: tbt.CallbackQuery):
    data = call.data.split(".")
    if data[1] == "NEW":
        bot.selected_chat[str(call.message.chat.id)] = "NEW"
        await bot.edit_message_text("Выбран новый чат", call.message.chat.id, call.message.id)
        return
    status, chat = bot.chats_manager.findInChatsById(str(call.message.chat.id), data[1])
    if not status:
        await bot.edit_message_text("Произошла неизвестная ошибка, и новый чат не был выбран", call.message.chat.id, call.message.id)
        return
    bot.selected_chat[str(call.message.chat.id)] = chat
    await bot.edit_message_text(f"Выбран чат с коротким названием {chat.name}", call.message.chat.id, call.message.id)

@bot.message_handler(content_types=["text"])
async def types_text(msg: tbt.Message):
    u_id = str(msg.chat.id)
    bot.genSelChat(u_id)
    if bot.selected_chat[u_id] == "NEW":
        answ, chat = bot.chats_manager.newChat(u_id, msg.text)
        bot.selected_chat[u_id] = chat
        await bot.send_message(u_id, answ)
    else:
        answ = bot.chats_manager.writeToAi(u_id, bot.selected_chat[u_id], msg.text)
        await bot.send_message(u_id, answ)

asyncio.run(bot.polling(non_stop=True))
