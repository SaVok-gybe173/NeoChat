from typing import Dict
from config import LAN_PATH
import json
import os

LAN: Dict[str, Dict[str, Dict[str, str] | str]] = {
    "ru":{
        "Cancellation": "Отмена",
        "Add": "Добавить",
        "join": "join",

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
setLanguage("us") # стандартный язык