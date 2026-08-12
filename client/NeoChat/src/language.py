from typing import Dict
from config import LAN_PATH
import json
import os

LAN: Dict[str, Dict[str, Dict[str, str] | str]] = {
    "ru":{
        "Cancellation": "Отмена",
        "Add": "Добавить",
        "join": "join",
        "log-in": "Войти",
        "send": "Отправить",
        "confirm": "Подтвердить",

        "Message": {
            "image": "📷 Фото",
            "code": "💻 Код",
            "file": "📎 Файл"
        },

        "server":{
            "all-regions": "Все регионы",
            "ping": "Пинг",
            "online": "онлайн", "offline": "офлайн", "maintenance": "техработы",
            "connecting-to": "Подключаемся к",
            "autoconnecting-to": "Подключаемся к",
            "ms": "мс",
            "Popularity": "Популярность",
            "Alphabet": "Алфавит",
            "Servers-not-found": "Серверы не найдены",
            "list-servers-updated": "Список серверов обновлён",
            "server-IP-address": "IP-адрес сервера",
            "server-by-IP-address": "Добавить сервер по IP",
            "Server-search": "Поиск сервера...",
            "update-list": "Обновить список",
            "Server-selection": "Выбор сервера",
            "add-ip": "Добавить по IP",
            "fast-connection": "Быстрое подключение",
            
        },
        "RegistrationMenu":{
            "fill-fields": "Заполните все поля",
            "passwords-match": "Пароли не совпадают",
            "login": "Логин",
            "come-login": "Придумайте логин",
            "email": "Email",
            "example-mail": "example@mail.com",
            "password": "Пароль",
            "confirm-password": "Подтвердите пароль",
            "register": "Зарегистрироваться",
            "create-account": "Создайте аккаунт",
            "please-fill-registration-data": "Заполните данные для регистрации",
            "there-already-account": "Уже есть аккаунт?",

        },
        "RecoveryMenu": {
            "enter-email": "Введите email",
            "enter-valid-email": "Введите корректный email",
            "return-entrance": "Вернуться ко входу",
            "password-recovery": "Восстановление пароля",
            "enter-email-send-code-reset": "Введите email, и мы пришлём код для сброса"

        },
        "EntranceServer": {
            "login-email": "email",
            "fill-login-password": "Заполните логин и пароль",
            "forgot-password": "Забыли пароль?",
            "account-login": "Вход в аккаунт",
            "enter-login-password-continue": "Введите логин и пароль, чтобы продолжить",
            "no-account": "Нет аккаунта?",

        },
        "CodMenu": {
            "code-from-letter": "Код из письма",
            "enter-6-digits": "Введите 6 цифр",
            "enter-code": "Введите код",
            "code-must-contain-exactly-6-digits": "Код должен содержать ровно 6 цифр",
            "send-code-again": "Отправить код повторно",
            "confirmation": "Подтверждение",
            "enter-6-digit-code-sent-emai": "Введите 6-значный код, отправленный на вашу почту"

            }
    }
}

# функция которая устанавливает глабальный язык
def setLanguage(lan: str) -> None:
    global _lan
    _lan = lan

# функция которая возвращает глобальный язык
def getLanguage() -> str:
    global _lan
    return _lan

# функция которая пинимает путь к переводу и возвращает этот перевод
def getLan(*names: tuple[str]) -> str | Dict[str, str]:
    lan = LAN[getLanguage()]
    for i in names:
        lan = lan[i]
    return lan

# функция которая загружает язык из json
def loadLan(file: str) -> None:
    with open(file, "r", encoding="utf-8") as f:
        data: Dict = json.loads(f.read())
    lan = data.get("language") or data.get('lan')
    LAN[lan] = data[lan]

# функция для загрузки всех языков из спика файлов
def loadLans(path: str) -> None:
    for i in os.listdir(path):
        loadLan(os.path.join(path, i))

loadLans(LAN_PATH)
setLanguage("ru") # стандартный язык