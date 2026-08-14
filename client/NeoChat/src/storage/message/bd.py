from dataclasses import dataclass, field
from .structure import Chat, Message, Text
import json

def load(path):
    global _path_bd
    _path_bd = path

def _getPathBd():
    global _path_bd
    return _path_bd

# высота > ширины -> узкий/портретный режим
def getIsNarrow() -> bool:
    global _is_narrow
    return _is_narrow

def setIsNarrow(is_narrow: bool) -> None:
    global _is_narrow
    _is_narrow = is_narrow

# данные о профиле
def getMyProfile() -> Chat:
    global _my_profile
    return _my_profile

def setMyProfile(profile: Chat) -> None:
    global _my_profile
    _my_profile = profile

def loadMyProfile(profile: Chat) -> None:
    global _my_profile
    pass # дописать

# какое действие сейчас активно
def getView() -> str:   # "empty" - ничего | "chat" - чаты | "profile" - профиль
    global _view
    return _view

def setView(view: str):
    global _view
    _view = view

def loadView():
    global _profile_target
    pass # дописать

# id чата, чей профиль открыт, или "me", если не открыт то None
def getProfileTarget() -> int | str | None:
    global _profile_target
    return _profile_target

def setProfileTarget(profile_target: int | str | None) -> None:
    global _profile_target
    _profile_target = profile_target

def loadProfileTarget():
    global _profile_target
    pass # дописать

# id открытого чата
def getActiveChatId() -> int | None:
    global _active_chat_id
    return _active_chat_id

def setActiveChatId(id:  int | None) -> None:
    global _active_chat_id
    _active_chat_id = id

def loadActiveChatId():
    global _active_chat_id
    pass # дописать

# список чатов
def delChat(chat: Chat):
    global _chats
    _chats.pop([i.id for i in _chats].index(chat.id))

def clearChats() -> None:
    global _chats
    _chats.clear()

def addChats(chat: Chat) -> None:
    global _chats
    _chats.append(chat)

def getChatId(id: int) -> Chat:
    global _chats
    return _chats[[i.id for i in _chats].index(id)]

def getChats() -> list[Chat]:
    global _chats
    return _chats

def _createChats() -> None:
    global _chats
    _chats = []

def loadChats():
    global _chats
    pass # дописать

# токен клиента

def setToken(tok: str) -> None:
    global _token
    _token = tok

def getToken() -> str:
    global _token
    return _token

# базовые значения
setView("empty")
setMyProfile(Chat(0, "null"))
setIsNarrow(False)
setActiveChatId(None)
_createChats()

addChats(Chat(1, "null", messages=[Text(0, "them", "21/23", text="```Нет ничего классного```")]))
addChats(Chat(2, "null1", messages=[Text(0, "them", "21/23", text="Ты чего?")]))