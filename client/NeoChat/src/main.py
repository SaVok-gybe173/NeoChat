from config import NAME, CONFIG
from ui.server import ServerMenu
from ui.entrance import EntranceServer
from ui.registration import RegistrationMenu
from ui.recovery import RecoveryMenu
from ui.email_cod import CodMenu

import flet as ft
import sys
import os

class Main:
    scens = []  # сценны

    def __init__(self, page: ft.Page):
        self.page = page
        page.title = NAME
        page.window.width = CONFIG.getint("WINDOW", "width")
        page.window.height = CONFIG.getint("WINDOW", "height")
        page.theme_mode = "dark"
        page.window.icon = "neochat-logo.png"
        self.index = 0

        # загрузка
        self.scens.append(ServerMenu(self.setScene))
        self.scens.append(EntranceServer(self.setScene))
        self.scens.append(RegistrationMenu(self.setScene))
        self.scens.append(RecoveryMenu(self.setScene))
        self.scens.append(CodMenu(self.setScene))

        self.scens[4](page)

    def setScene(self, index):          # смена сценны
        self.index = index              # 
        self.page.clean()               # 
        self.scens[index](self.page)    # запуск

if __name__ == "__main__":
   ft.app(target=Main)