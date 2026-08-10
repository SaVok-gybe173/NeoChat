from config import NAME
from ui.server import ServerMenu

import flet as ft
import sys, os

class Main:
    scens = []
    def __init__(self, page: ft.Page):
        self.page = page
        page.title = NAME
        page.theme_mode = "dark"
        page.window.icon = "neochat-logo.png"

        self.scens.append(ServerMenu())

        self.scens[0](page)


if __name__ == "__main__":
   ft.app(target=Main)