import configparser
import flet as ft

CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')

def save():
    pass

NAME = "Neo Chat"

THEME_MODS = [ft.ThemeMode.LIGHT, ft.ThemeMode.DARK]