from storage.server import serverSet, serverGet, serverIsActiv, serverClose
from storage.message.bd import setToken, getToken, getActiveChatId, getUsernameChatId, getChats, addChats, Chat
from storage.logger import printLog, ERROR, REQUESTS_INFO
from config import setScene, DEBUGGING_REQUESTS_LOG
from core.fingerprint import get_device_fingerprint
from typing import Callable, Dict, Any, Generator
from .error import (RegistrationEmailError, RegistrationUsernameError, RegistrationError,
                    EntranceInvalidError, EntranceVerifiedError, EntranceError,
                    SendMessageError
                    )


def new_message(data: Dict[str, str]) -> None: 
    ... # 
PUSH_CALLABLE: Dict[str, Callable] = {"new_message": new_message} # пуш типы

def coroutine(func: Callable) ->  Callable:
    def start(*args, **kargs) -> Generator:
        get = func(*args, **kargs)
        next(get)
        return get
    return start

# логгер запросов
@coroutine
def requests_log(name, logger: str = REQUESTS_INFO) -> Generator:
    if DEBUGGING_REQUESTS_LOG:
        data = yield
        printLog("start >", name, '>', data)
        data = yield
        printLog("finish >", name, '>', data)
        yield
    else:
        yield ; yield ; yield

def serverRegistration(username: str, password: str, email: str) -> bool:           # выполняет регестрацию
    printLog('регестрация >', username)
    requests:  Generator = requests_log("serverRegistration")
    requests.send(dict(username=username, password="*"*len(password), email=email))

    try:
        data = serverGet().send_request("register", username=username, password=password, email=email)
        requests.send(data )
        requests.close()
    except ConnectionError as e:
        printLog("client api >", e, types=ERROR)
        requests.close()
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
    requests:  Generator = requests_log("serverEntrance")
    requests.send(dict(username=username, password='*'*len(password), device=get_device_fingerprint()))

    try:
        data = serverGet().send_request("login", username=username, password=password, device=get_device_fingerprint())
        requests.send(str(data) )
        requests.close()
    except ConnectionError as e:
        printLog("client api >", e, types=ERROR)
        requests.close()
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
def serverSendMessage(mess: str) -> bool:
    requests:  Generator = requests_log("serverSendMessage")
    requests.send(dict(token = getToken(), to = getUsernameChatId(id), content = mess))

    id = getActiveChatId()
    if id is None: raise SendMessageError()

    try:
        data = serverGet().send_request("send_message", token = getToken(), to = getUsernameChatId(id), content = mess)
        requests.send(str(data) )
        requests.close()
    except ConnectionError as e:
        printLog("client api >", e, types=ERROR)
        requests.close()
        raise SendMessageError()

    if data['status'] == "ok":
        return True
    else:
        return False

# обновление списка чатов
def updateListChats() -> bool:
    requests:  Generator = requests_log("updateListChats")
    requests.send(f"{'{'}token: {getToken()}{'}'}")
    
    try:
        data: Dict[str, str | list] = serverGet().send_request("get_users", token = getToken())
        requests.send(str(data) )
        requests.close()
    except ConnectionError as e:
        requests.close()
        printLog("client api >", e, types=ERROR)
        return False

    chats = getChats()
    usernames = [j.username for j in chats]
    
    if data["status"] == 'ok':
        for i in data["users"]:
            if not i in usernames:
                addChats(Chat(int.from_bytes(i.encode("ascii")),
                              i, i))
# пущ сообщения
#
# updatePush - вызывает пуш функции
# delPush - удалет одно или все пуш сообщения
# setPush - добавляет пуш сообщение
#
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