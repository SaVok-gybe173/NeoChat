from storage.server import serverSet, serverGet, serverIsActiv, serverClose
from storage.message.bd import setToken, getToken
from config import setScene
from core.fingerprint import get_device_fingerprint
from .error import (RegistrationEmailError, RegistrationUsernameError, RegistrationError,
                    EntranceInvalidError, EntranceVerifiedError, EntranceError
                    )

def serverRegistration(username: str, password: str, email: str) -> bool:           # выполняет регестрацию, 
    # {"action": "register", "username": "alice", "password": "secret123"}
    try:
        data = serverGet().send_request("register", username=username, password=password, email=email)
    except ConnectionError:
        raise RegistrationError()
    
    # {"status": "error", "message": "Username already exists"}
    if data["status"] == "error":
        if data["message"] == "Invalid credentials":    # так как ответ отличаеться то вместо reason будем использоваь message (потом помеяем)
            raise RegistrationUsernameError()       
        elif data["message"] == "username_taken":       # на данный момент не активно
            raise RegistrationEmailError()
        else:
            raise RegistrationError()
    elif data["status"] == "ok":
        return True
    else:
        return False

def serverEntrance(username: str, password: str) -> bool:                     # выполняеться вход и добвляеться токен
    try:
        data = serverGet().send_request("login", username=username, password=password, device=get_device_fingerprint())
    except ConnectionError:
        raise EntranceError()
    if data["status"] == "error":
            if data["message"] == 'Invalid credentials':    # 
                raise EntranceInvalidError()
            elif data["message"] == "device_not_verified":  # на данный момент не активно
                raise EntranceVerifiedError()
            else:
                raise EntranceError()
    elif data["status"] == "ok":
        setToken()
        return True
    else:
        return False

