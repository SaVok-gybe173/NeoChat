from language import getLan

# ошибки регестрации
class RegistrationUsernameError(Exception):
    def __init__(self):
        super().__init__(getLan("error", "RegistrationUsernameError"))

class RegistrationEmailError(Exception):
    def __init__(self):
        super().__init__(getLan("error", "RegistrationEmailError"))

class RegistrationError(Exception):
    def __init__(self):
        super().__init__(getLan("error", "RegistrationError"))

# ошибки входа
class EntranceInvalidError(Exception):
    def __init__(self):
        super().__init__(getLan("error", "EntranceInvalidError"))

class EntranceVerifiedError(Exception):
    def __init__(self):
        super().__init__(getLan("error", "EntranceVerifiedError"))

class EntranceError(Exception):
    def __init__(self):
        super().__init__(getLan("error", "EntranceError"))

# ошибка отправкии сообщений
class SendMessageError(Exception):
    def __init__(self):
        super().__init__()