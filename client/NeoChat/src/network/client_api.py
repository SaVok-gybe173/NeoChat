from storage.server import serverSet, serverGet, serverIsActiv, serverClose
from core.fingerprint import get_device_fingerprint
from .error import (RegistrationEmailError, RegistrationUsernameError, RegistrationError,
                    EntranceInvalidError, EntranceVerifiedError, EntranceError
                    )

def serverRegistration(username: str, password: str, email: str) -> bool:           # выполняет регестрацию, 
    data = serverGet().send_request("register", username=username, password=password, email=email)
    if data["status"] == "error":
        if data["reason"] == "email_taken":
            raise RegistrationUsernameError()
        elif data["reason"] == "username_taken":
            raise RegistrationEmailError()
        else:
            raise RegistrationError()
    elif data["status"] == "ok":
        return True
    else:
        return False

def serverEntrance(username, password):                                             # выполняеться вход и добвляеться токен
    data = serverGet().send_request("login", username=username, password=password, device=get_device_fingerprint())
    print(data)
    if data["status"] == "error":
            if data["reason"] == "invalid_credentials":
                raise EntranceInvalidError()
            elif data["reason"] == "device_not_verified":
                raise EntranceVerifiedError()
            else:
                raise EntranceError()
    elif data["status"] == "ok":
        return True
    else:
        return False