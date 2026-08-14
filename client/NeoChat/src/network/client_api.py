from storage.server import serverSet, serverGet, serverIsActiv, serverClose
from core.fingerprint import get_device_fingerprint
from .error import (RegistrationEmailError, RegistrationUsernameError, RegistrationError,
                    EntranceInvalidError, EntranceVerifiedError, EntranceError
                    )

def serverRegistration(username: str, password: str, email: str) -> bool:           # выполняет регестрацию, 
<<<<<<< HEAD
    # {"action": "register", "username": "alice", "password": "secret123"}
    try:
        data = serverGet().send_request("register", username=username, password=password, email=email)
    except ConnectionError as e:
        print(e)
        raise RegistrationError()
    print(data)
    
    # {'message': 'Invalid username or password', 'reason': 'invalid_credentials', 'req_id': '', 'status': 'error'}
    if data["status"] == "error":
        if data['reason'] == 'invalid_credentials':    
            raise RegistrationUsernameError()       
        elif data['reason'] == "username_taken":
=======
    data = serverGet().send_request("register", username=username, password=password, email=email)
    if data["status"] == "error":
        if data["reason"] == "email_taken":
            raise RegistrationUsernameError()
        elif data["reason"] == "username_taken":
>>>>>>> parent of 528d91e (Bugs related to returns have been fixed.)
            raise RegistrationEmailError()
        else:
            raise RegistrationError()
    elif data["status"] == "ok":
        return True
    else:
        return False

<<<<<<< HEAD
def serverEntrance(username: str, password: str) -> bool:                     # выполняеться вход и добвляеться токен
    try:
        data = serverGet().send_request("login", username=username, password=password, device=get_device_fingerprint())
    except ConnectionError:
        raise EntranceError()
    print(data)
    if data["status"] == "error":
            if data['reason'] == 'invalid_credentials':    
                raise EntranceInvalidError()
            elif data['reason'] == "device_not_verified":
=======
def serverEntrance(username, password):                                             # выполняеться вход и добвляеться токен
    data = serverGet().send_request("login", username=username, password=password, device=get_device_fingerprint())
    print(data)
    if data["status"] == "error":
            if data["reason"] == "invalid_credentials":
                raise EntranceInvalidError()
            elif data["reason"] == "device_not_verified":
>>>>>>> parent of 528d91e (Bugs related to returns have been fixed.)
                raise EntranceVerifiedError()
            else:
                raise EntranceError()
    elif data["status"] == "ok":
<<<<<<< HEAD
        setToken(data['token'])
=======
>>>>>>> parent of 528d91e (Bugs related to returns have been fixed.)
        return True
    else:
        return False