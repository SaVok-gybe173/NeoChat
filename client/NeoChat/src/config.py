from core.server import SERVERS, Server
import configparser
import flet as ft
import os

CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')

def save():
    pass

NAME = "Neo Chat"
HOME = os.path.expanduser("~")

THEME_MODS = [ft.ThemeMode.LIGHT, ft.ThemeMode.DARK]