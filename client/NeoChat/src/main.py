from config import NAME, CONFIG, _setSceneLink, getPage, _setPage, THEME_MODS
from storage.logger import printLog
from ui.server import ServerMenu
from ui.entrance import EntranceServer
from ui.registration import RegistrationMenu
from ui.recovery import RecoveryMenu
from ui.email_cod import CodeMenu
from ui.chat_app import ChatMenu

import flet as ft
import sys
import os

class Main:
    scens: list = []  # сценны
    index = 0

    def __init__(self, page: ft.Page):
        self.page = page
        _setPage(page)
        page.title = NAME
        page.window.width = CONFIG.getint("WINDOW", "width")
        page.window.height = CONFIG.getint("WINDOW", "height")
        page.theme_mode = THEME_MODS[1]
        page.window.icon = "neochat-logo.png"

        printLog("start main")

        # загрузка
        self.scens.append(ServerMenu(self.setScene))            # меню для выбора сервера
        self.scens.append(EntranceServer(self.setScene))        # вход на сервер
        self.scens.append(RegistrationMenu(self.setScene))      # регестрация
        self.scens.append(RecoveryMenu(self.setScene))          # востановление пароля
        self.scens.append(CodeMenu(self.setScene))              # прием цифр из письма
        self.scens.append(ChatMenu(self.setScene))              # чаты

        self.scens[self.index](page)

        _setSceneLink(self.setScene)

    @classmethod
    def setScene(cls, index):               # смена сценны
        printLog("сценна сменилась >", index)               
        if isinstance(index, str):          # поиск по имени
            index = [type(i).__name__ for i in cls.scens].index(index)
        cls.index = index                   # установка индекса
        getPage().clean()                   # очистка экрана
        
        cls.scens[index](getPage().page)    # запуск

if __name__ == "__main__":
   ft.app(target=Main)