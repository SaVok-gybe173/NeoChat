from dataclasses import dataclass, field
from typing import List
import flet as ft

BUBBLE_USER = "#2a3550"
BUBBLE_ASSIST = "#1b1f26"
BORDER = "#262b33"

@dataclass
class Message:
    id: str                     # id сообщения
    sender: str                 # "me" | "them" | "system"
    time: str                   # время отправки
    sender_name: str = ""       # имя автора для групповых чатов (если sender == "them")

    type: str | None = None     #

    def draw(self, page: ft.Page) -> ft.Container:
        return

@dataclass
class Caption(Message):         # обычное изображение
    caption: str = ""           # путь к изображению
    id_caption: int = 0         # id изображения
    type: str | None = "image"  # 

@dataclass
class Text(Message):            # Текст
    text: str = ""              #
    type: str | None = "text"   #
    def draw(self, page):
        body = ft.Markdown(
                        self.text, selectable=True,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                        code_theme="atom-one-dark",
                    )
        return ft.Container(
                        content=body, bgcolor=BUBBLE_USER if self.sender == "me" else BUBBLE_ASSIST, border=ft.Border.all(1, BORDER),
                        border_radius=14, padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                    )
        

@dataclass
class CaptionText(Text, Caption):# текст с изображением
    type: str | None = "text"

@dataclass
class File(Message):            # фаил
    file: str | None = None     # путь к файлу если есть
    type: str | None = "file"   # 
    id_file: int = 0            # id файла

@dataclass
class Chat:
    id: str                                                                                         # id чата
    title: str                                                                                      # название
    is_group: bool = False                                                                          # чат это или же группа
    status: str = "в сети"                                                                          # текущий статус
    members: List[str] = field(default_factory=list)                                                # список учасников если группа
    messages: List[Message | Caption | Text | CaptionText | File] = field(default_factory=list)     # сообщния
    unread: bool = False                                                                            # есть ли новое сообщение