
LAN = {
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

def setLanguage(lan: str) -> None:
    global _lan
    _lan = lan

def getLanguage() -> str:
    global _lan
    return _lan

def getLan(*names):
    lan = LAN[getLanguage()]
    for i in names:
        lan = lan[i]
    return lan

setLanguage("ru")