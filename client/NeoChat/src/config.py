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

CONFIG = configparser.ConfigParser()
CONFIG.read("config.ini")

def saveConfig():
    pass

NAME = "Neo Chat"
HOME = os.path.join(os.path.expanduser('~'), "NeoChat") # путь к корневой папки
LAN_PATH = os.path.join(HOME, "langes") # путь к списку языков

if not os.path.isdir(HOME): os.makedirs(HOME)
if not os.path.isdir(LAN_PATH):
    os.makedirs(LAN_PATH)
    with open(os.path.join(LAN_PATH, "us.json"), 'w', encoding="utf-8") as f:
        f.write(

"""
{
    "lan": "us",
    "us": {
        "Cancellation": "Cancel",
        "Add": "Add",
        "join": "Join",

        "server": {
            "all-regions": "All regions",
            "ping": "Ping",
            "online": "Online",
            "offline": "Offline",
            "maintenance": "Maintenance",
            "connecting-to": "Connecting to",
            "autoconnecting-to": "Auto-connecting to",
            "ms": "ms",
            "Popularity": "Popularity",
            "Alphabet": "Alphabet",
            "Servers-not-found": "Servers not found",
            "list-servers-updated": "Server list updated",
            "server-IP-address": "Server IP address",
            "server-by-IP-address": "Add server by IP",
            "Server-search": "Search server...",
            "update-list": "Update list",
            "Server-selection": "Server selection",
            "add-ip": "Add by IP",
            "fast-connection": "Quick connect"
        }
    }
}
""")


THEME_MODS = [ft.ThemeMode.LIGHT, ft.ThemeMode.DARK]