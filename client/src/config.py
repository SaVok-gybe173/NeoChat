DEBUGGING = True                # отладка (выводит в консоль сообщения об ошибках)
DEBUGGING_REQUESTS_LOG = True   # добавляет все запросы и ответы в лог фаил

from core.platform import is_android, is_ios
import configparser
import flet as ft
import os

def setScene(index: int|str) -> None:
    global _setScene
    return _setScene(index)

def _setSceneLink(setScene):
    global _setScene
    _setScene = setScene

def _setPage(page: ft.Page):
    global _page
    _page = page

def getPage() -> ft.Page:
    global _page
    return _page

def saveConfig():
    with open(CONFIG_PATH, 'w', encoding="utf-8") as f:
        CONFIG.write(f)

NAME = "Neo Chat"

# FLET_APP_STORAGE_DATA - директория, куда приложению разрешено писать
# на Android/iOS/desktop. Локально (flet run) тоже работает и указывает
# на <project>/.flet/storage/data. Фолбэк на "." на случай, если
if (is_android() or is_ios()) or DEBUGGING:
    _APP_STORAGE = os.getenv("FLET_APP_STORAGE_DATA", ".")  # можно заменить на os.path.join(os.path.expanduser('~'), "NeoChat"), но на телефонах не будет работать
else:
    _APP_STORAGE = os.path.expanduser('~')

HOME = os.path.join(_APP_STORAGE, "NeoChat")  # путь к корневой папке
LOG_PATH = os.path.join(HOME, "logs") 
CONFIG_PATH = os.path.join(HOME, "config.ini")
LAN_PATH = os.path.join(HOME, "langes")  # путь к списку языков

if not os.path.isdir(HOME):         os.makedirs(HOME)
if not os.path.isdir(LAN_PATH):     os.makedirs(LAN_PATH)
if not os.path.isdir(LOG_PATH):     os.makedirs(LOG_PATH)
if not os.path.isfile(CONFIG_PATH):
    with open(CONFIG_PATH, 'w', encoding="utf-8") as f:
        f.write("""
[DATABASE]
host = 127.0.0.1
port = 8080

[WINDOW]
mode = 0

width = 1000
height = 700
""")


THEME_MODS = [ft.ThemeMode.LIGHT, ft.ThemeMode.DARK, ft.ThemeMode.SYSTEM]

CONFIG = configparser.ConfigParser()
CONFIG.read(CONFIG_PATH)  # раньше тут было "config.ini" - неверный относительный путь