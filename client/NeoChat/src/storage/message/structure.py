from dataclasses import dataclass, field
from typing import List
from PIL import ImageFont
import flet as ft
import os


def get_flet_font_path() -> str:
    """
    Возвращает путь к файлу шрифта, который Flet использует по умолчанию (Roboto).
    Если файл не найден — возвращает путь к системному шрифту как fallback.
    """
    # Директория, где установлен пакет flet
    flet_dir = os.path.dirname(ft.__file__)

    # Возможные пути внутри пакета flet (разные версии хранят по-разному)
    candidates = [
        os.path.join(flet_dir, "assets", "fonts", "Roboto-Regular.ttf"),
        os.path.join(flet_dir, "assets", "Roboto-Regular.ttf"),
        os.path.join(flet_dir, "core", "assets", "fonts", "Roboto-Regular.ttf"),
        os.path.join(flet_dir, "controls", "assets", "fonts", "Roboto-Regular.ttf"),
        os.path.join(flet_dir, "_internal", "assets", "fonts", "Roboto-Regular.ttf"),
    ]

    # Ищем шрифт в директории пакета flet
    for path in candidates:
        if os.path.isfile(path):
            return path

    # Если не нашли по известным путям — ищем рекурсивно
    for root, dirs, files in os.walk(flet_dir):
        for f in files:
            if f.lower() in ("roboto-regular.ttf", "roboto.ttf", "notosans-regular.ttf"):
                return os.path.join(root, f)

    # Fallback: системные шрифты
    fallbacks = [
        "arial.ttf",                              # Windows
        "C:/Windows/Fonts/arial.ttf",             # Windows абсолютный
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
        "/System/Library/Fonts/Helvetica.ttc",    # macOS
    ]
    for fb in fallbacks:
        if os.path.isfile(fb):
            return fb

    raise FileNotFoundError("Шрифт Flet не найден. Проверьте установку пакета.")

BG = "#0e1013"
PANEL = "#15181d"
PANEL_2 = "#1b1f26"
BORDER = "#262b33"
TEXT = "#e7e9ec"
TEXT_DIM = "#8b929e"
TEXT_FAINT = "#565c66"
ACCENT = "#5b8cff"
ACCENT_DIM = "#2a3a5c"
GROUP_COLOR = "#8f6bff"
BUBBLE_USER = "#2a3550"
BUBBLE_ASSIST = "#1b1f26"

# Загружаем тот же шрифт, что использует приложение
# (путь к .ttf/.otf — обычный шрифт системы или тот, что задан в Theme)

try:
    _font = ImageFont.truetype(get_flet_font_path(), size=14)
except:
    try:
        _font = ImageFont.truetype("arial.ttf", size=14)
    except: pass

    
def measure_width(text: str) -> int:
    return int(_font.getlength(text))

@dataclass
class Message:
    id: str                     # id сообщения
    sender: str                 # "me" | "them" | "system"
    time: str                   # время отправки
    sender_name: str = ""       # имя автора для групповых чатов (если sender == "them")

    type: str | None = None     #

    def draw(self, page: ft.Page) -> ft.Container:
        return ft.Container()

@dataclass
class Caption(Message):         # обычное изображение
    caption: str = ""           # подпись
    id_caption: int = 0         # id изображения
    src: str | None = None      # путь к изображению
    type: str | None = "image"  # тип

    def draw(self, page):
        bubble_color = BUBBLE_USER if self.sender == "me" else BUBBLE_ASSIST

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Image(src=self.src, width=240,
                             border_radius=ft.BorderRadius.only(top_left=10, top_right=10)),
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(self.caption, size=11.5, color=TEXT_DIM, expand=True),
                                ft.IconButton(icon=ft.Icons.DOWNLOAD, icon_size=15, icon_color=TEXT_DIM,
                                              tooltip="Скачать",
                                              on_click=lambda e: self.download_file()),
                            ],
                        ),
                        padding=ft.Padding.only(left=10, right=4, top=6, bottom=4),
                    ) if self.caption else ft.Container(),
                ],
                spacing=0,
            ),
            border=ft.Border.all(1, BORDER), bgcolor=bubble_color,
            border_radius=10,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            ink=True,
            on_click=lambda e: self.open_image_viewer(),
        )

    def open_image_viewer():    # открытие изображения
        pass

    def download_file():        # установка изображения
        pass


@dataclass
class Text(Message):            # Текст
    text: str = ""              # главный текст
    type: str | None = "text"   # тип

    def draw(self, page):
        bubble_color = BUBBLE_USER if self.sender == "me" else BUBBLE_ASSIST

        body = ft.Markdown(
            self.text.replace('\n', '  \n'),
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            code_theme="atom-one-dark",
        )

        max_width = 300
        padding_extra = 40  # отступы контейнера

        lines = self.text.split('\n')
        longest_line = max(lines, key=len)
        #content_width = 8 * len(longest_line) + 30
        content_width = measure_width(longest_line) + padding_extra
        width = min(content_width, max_width)

        return ft.Container(
            ft.Container(
                content=body,
                border=ft.Border.all(1, BORDER),
                bgcolor=bubble_color,
                border_radius=8,
                padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            ),
            width=width,
        )

@dataclass
class File(Message):            # фаил
    file: str | None = None     # путь к файлу если есть
    type: str | None = "file"   # тип
    title: str = ''             # имя
    sub = str = ''              # "3.1 KB · Python"
    id_file: int = 0            # id файла

    def draw(self, page):
        bubble_color = BUBBLE_USER if self.sender == "me" else BUBBLE_ASSIST
        body = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon=ft.Icons.INSERT_DRIVE_FILE, color=ACCENT, size=22),
                    ft.Column(
                        controls=[
                            ft.Text(self.title, size=13, weight=ft.FontWeight.W_600, color=TEXT),
                            ft.Text(self.sub, size=12, color=TEXT_DIM),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Icon(icon=ft.Icons.DOWNLOAD, color=TEXT_DIM, size=18),
                ],
                spacing=10,
            ),
            bgcolor=PANEL_2, border=ft.Border.all(1, BORDER),
            border_radius=10, padding=12,
            ink=True,
            on_click=lambda e: self.download_file(),
        )
        return ft.Container(
            content=body, bgcolor=bubble_color, border=ft.Border.all(1, BORDER),
            border_radius=14, padding=10,
        )
    
    def download_file():    # установка файла
        pass

@dataclass
class Code(Text):
    lang: str = 'python'        # язык для подсветки
    type: str = "code"          # тип
    
    def draw(self, page):
        body = ft.Markdown(
            f"```{self.lang}\n{self.text}\n```", selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            code_theme="atom-one-dark",
        )
        return ft.Container(
            content=body, bgcolor="#0a0c0f", border=ft.Border.all(1, BORDER),
            border_radius=10, padding=8,
        )

@dataclass
class Chat:
    id: str                                                                                         # id чата
    title: str                                                                                      # название
    is_group: bool = False                                                                          # чат это или же группа
    status: str = "в сети"                                                                          # текущий статус
    members: List[str] = field(default_factory=list)                                                # список учасников если группа
    messages: List[Message | Caption | Text | Code | File] = field(default_factory=list)            # сообщния
    unread: bool = False                                                                            # есть ли новое сообщение
    render: ft.Container | None = None