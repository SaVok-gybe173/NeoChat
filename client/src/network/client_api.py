from storage.server import serverSet, serverGet, serverIsActiv, serverClose
from storage.message.bd import setToken, getToken, getActiveChatId, getUsernameChatId, getChats, addChats, Chat
from storage.logger import printLog, ERROR
from config import setScene
from core.fingerprint import get_device_fingerprint
from typing import Callable, Dict, Any
from .error import (RegistrationEmailError, RegistrationUsernameError, RegistrationError,
                    EntranceInvalidError, EntranceVerifiedError, EntranceError,
                    SendMessageError
                    )

def new_message(data: Dict[str, str]) -> None:
    ...

PUSH_CALLABLE: Dict[str, Callable] = {"new_message": new_message}

def serverRegistration(username: str, password: str, email: str) -> bool:           # выполняет регестрацию
    printLog('регестрация >', username)
    try:
        data = serverGet().send_request("register", username=username, password=password, email=email)
    except ConnectionError as e:
        printLog("client api >", e, types=ERROR)
        raise RegistrationError()
    
    if data.get("status") == "error":
        if 'reason' in data: # есть ли reason в версии сервера
            if data.get('reason') == 'invalid_credentials':    
                raise RegistrationUsernameError()       
            elif data.get('reason') == "username_taken":
                raise RegistrationEmailError()
            else:
                raise RegistrationError()
        elif "message" in data:
            match data["message"]:
                case "Missing username, password or email":
                    raise RegistrationError()
                case ["Username must be 1-32 characters", "Username already exists"]:
                    raise RegistrationUsernameError()
                case ["Email must be 1-254 characters", "Invalid email format", "Email already registered"]:
                    raise RegistrationEmailError()
                case "Too many attempts. Try again in 5 minutes.": # лимиты запросов
                    raise RegistrationError()
                case "Password must be 1-128 characters": # не верный пароль
                    raise RegistrationError()
                case _:
                    raise RegistrationError()
        else:
                raise RegistrationError()
        
    elif data.get("status") == "ok":
        return True
    else:
        return False

def serverEntrance(username: str, password: str) -> bool:                     # выполняеться вход и добвляеться токен
    printLog('вход в аккаунт >', username)
    try:
        data = serverGet().send_request("login", username=username, password=password, device=get_device_fingerprint())
    except ConnectionError as e:
        printLog("client api >", e, types=ERROR)
        raise EntranceError()
    
    if data.get("status") == "error":
        if 'reason' in data:
            if data.get('reason') == 'invalid_credentials':    
                raise EntranceInvalidError()
            elif data.get('reason') == "device_not_verified":
                raise EntranceVerifiedError()
            else:
                raise EntranceError()
        elif "message" in data:
            match data["message"]:
                case "Missing username or password":
                    raise EntranceError()
                case "Username must be 1-32 characters":
                    raise EntranceInvalidError()
                case "Too many attempts. Try again in 5 minutes.": # Превышен лимит попыток
                    raise EntranceError()
                case "Invalid credentials":
                    raise EntranceVerifiedError()
                case _:
                    raise EntranceError()
        else:
            raise EntranceError()
    elif data.get("status") == "ok":
        setToken(data['token'])
        setPush()
        return True
    else:
        return False

# отправка сообщения
def serverSendMessage(mess: str) -> None:
    id = getActiveChatId()
    if id is None: raise SendMessageError()

    try:
        data = serverGet().send_request("send_message", token = getToken(), to = getUsernameChatId(id), content = mess)
    except ConnectionError as e:
        printLog("client api >", e, types=ERROR)
        raise SendMessageError()

    if data['status'] == "ok":
        return True
    else:
        return False

# обновление списка чатов
def updateListChats() -> bool:
    
    try:
        data: Dict[str, str | list] = serverGet().send_request("get_users", token = getToken())
    except ConnectionError as e:
        return False

    chats = getChats()
    usernames = [j.username for j in chats]
    
    if data["status"] == 'ok':
        for i in data["users"]:
            if not i in usernames:
                addChats(Chat(int.from_bytes(i.encode("ascii")),
                              i, i))

# обновление сообщений
type Data = Any
def updatePush(msg: Dict[str, Data]):
    try:
        PUSH_CALLABLE[msg["action"]](msg)
    except KeyError as e:
        printLog("Не найден \"action\" в PUSH_CALLABLE >", e, types=ERROR)
    except Exception as e:
        printLog(f"updatePush > {msg["action"]} >", e, types=ERROR)

# устанавливает пуш функциию
def setPush(fun: Callable[[Dict[str, Data]], None] | None = None) -> None:
    if fun is None:
        serverGet().on_push(updatePush)
    else:
        serverGet().on_push(fun)

# удаляет все функции
def delPush(fun: Callable[[Dict[str, Data]], None] | None = None) -> bool:
    if fun is None:
        for i, f in enumerate(serverGet().push_callbacks):
            if f is fun:
                serverGet().push_callbacks.pop(i)
                return True
        else:
            return False
    else:
        serverGet().push_callbacks.clear()
    return True