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
if not os.path.isdir(LAN_PATH): os.makedirs(LAN_PATH)
    


THEME_MODS = [ft.ThemeMode.LIGHT, ft.ThemeMode.DARK]