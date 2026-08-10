import configparser
import flet as ft
import os

CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')

def save():
    pass

NAME = "Neo Chat"
HOME = os.path.join(os.path.expanduser("~"), "NeoChat")

if not os.path.isdir(HOME):
    os.makedirs(HOME)

THEME_MODS = [ft.ThemeMode.LIGHT, ft.ThemeMode.DARK]