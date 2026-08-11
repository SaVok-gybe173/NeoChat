from typing import Callable
from language import getLan
from storage import getChats, getActiveChatId, Chat, getMyProfile, getView
import flet as ft

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

def name_initials(name: str) -> str:
    parts = name.split()
    letters = "".join(p[0] for p in parts[:2] if p)
    return letters.upper() or "?"

class ChatMenu:
    visible_chat = False
    visible_chat_list = False

    def __init__(self, setScene: Callable):
        self.setScene = setScene

    def __call__(self, page: ft.Page):
        self.sidebar_holder = ft.Container(expand=False)
        self.main_holder = ft.Container(expand=True)
        self.root_row = ft.Row(controls=[self.sidebar_holder, self.main_holder], spacing=0, expand=True)

        def open_chat():
            pass

        def avatar(initials: Chat, size=36, is_group=False): # получение аватарки
            content = (
                ft.Icon(icon=ft.Icons.GROUPS, size=size * 0.5, color="#ffffff")
                if is_group else
                ft.Text(initials.title[0], size=size * 0.35, weight=ft.FontWeight.BOLD, color="#ffffff")
            )
            return ft.CircleAvatar(
                content=content,
                bgcolor=GROUP_COLOR if is_group else ACCENT,
                radius=size / 2,
            )
        
        def build_sidebar():
            items = []
            for c in getChats():
                last = c.messages[-1] if c.messages else None
                if not last:
                    preview = ""
                elif last.type == "image":
                    preview = "📷 Фото"
                elif last.type == "code":
                    preview = "💻 Код"
                elif last.type == "card":
                    preview = "📎 Файл"
                else:
                    preview = (last.text or "").replace("**", "").replace("`", "")
                if c.is_group and last and last.sender == "them" and last.sender_name:
                    preview = f"{last.sender_name.split()[0]}: {preview}"

                is_active = c.id == getActiveChatId() and getView() == "chat"

                row_content = ft.Row(
                    controls=[
                        avatar(c, is_group=c.is_group),
                        ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(c.title, size=13.5, weight=ft.FontWeight.W_600,
                                                color=TEXT, no_wrap=True, overflow=ft.TextOverflow.ELLIPSIS,
                                                expand=True),
                                        ft.Text(last.time if last else "", size=11, color=TEXT_FAINT),
                                    ],
                                    spacing=6,
                                ),
                                ft.Text(preview, size=12.5, color=TEXT_DIM, no_wrap=True,
                                        overflow=ft.TextOverflow.ELLIPSIS),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Container(width=8, height=8, border_radius=4, bgcolor=ACCENT, visible=c.unread),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                )

                items.append(ft.Container(
                    content=row_content,
                    padding=10,
                    border_radius=10,
                    bgcolor=ACCENT_DIM if is_active else None,
                    on_click=lambda e, cid=c.id: open_chat(cid),
                    ink=True,
                ))

            header = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("Чаты", size=15, weight=ft.FontWeight.W_600, color=TEXT),
                        ft.IconButton(icon=ft.Icons.ADD, icon_size=18, icon_color=TEXT_DIM,
                                      tooltip="Новый чат", bgcolor=PANEL_2),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=ft.Padding.only(left=16, right=16, top=18, bottom=12),
                border=ft.Border.only(bottom=ft.BorderSide(1, BORDER)),
            )

            # ---- футер сайдбара: переход в свой профиль ----
            me_row = ft.Container(
                content=ft.Row(
                    controls=[
                        avatar(getMyProfile()),
                        ft.Column(
                            controls=[
                                ft.Text(getMyProfile().title, size=13, weight=ft.FontWeight.W_600, color=TEXT),
                                ft.Text("Мой профиль", size=11.5, color=TEXT_FAINT),
                            ],
                            spacing=0,
                        ),
                    ],
                    spacing=10,
                ),
                padding=12,
                border=ft.Border.only(top=ft.BorderSide(1, BORDER)),
                on_click=lambda e: open_profile("me"),
                ink=True,
            )

            return ft.Container(
                content=ft.Column(
                    controls=[
                        header,
                        ft.Container(
                            content=ft.ListView(controls=items, spacing=2, expand=True),
                            padding=8,
                            expand=True,
                        ),
                        me_row,
                    ],
                    spacing=0,
                    expand=True,
                ),
                bgcolor=PANEL,
                border=ft.Border.only(right=ft.BorderSide(1, BORDER)) if not state["is_narrow"] else None,
                width=300 if not state["is_narrow"] else None,
                expand=True if state["is_narrow"] else False,
            )
        page.add(self.root_row)

        build_sidebar()