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
    except ConnectionError as e:
        print(e)
        raise RegistrationError()
    
    # {'message': 'Invalid username or password', 'reason': 'invalid_credentials', 'req_id': '', 'status': 'error'}
    if data["status"] == "error":
        if data.get('reason') == 'invalid_credentials':    
            raise RegistrationUsernameError()       
        elif data.get('reason') == "username_taken":
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
            if data.get('reason') == 'invalid_credentials':    
                raise EntranceInvalidError()
            elif data.get('reason') == "device_not_verified":
                raise EntranceVerifiedError()
            else:
                raise EntranceError()
    elif data["status"] == "ok":
        setToken(data['token'])
        return True
    else:
        return False

