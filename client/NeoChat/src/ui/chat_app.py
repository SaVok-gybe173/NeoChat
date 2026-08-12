from typing import Callable
from language import getLan
from storage import (getChats, getActiveChatId,
                    Chat, getMyProfile, 
                    getView, getIsNarrow, 
                    setIsNarrow, getProfileTarget, 
                    setActiveChatId, setView,
                    getChatId, setProfileTarget)
from config import CONFIG
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

def build_empty():
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text("💬", size=24),
                    width=56, height=56, border_radius=16,
                    border=ft.Border.all(1, BORDER),
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Text("Выберите чат", size=15, weight=ft.FontWeight.W_600, color=TEXT_DIM),
                ft.Text(
                    "Откройте диалог слева, чтобы увидеть переписку. Пока ничего не выбрано.",
                    size=13, color=TEXT_FAINT, text_align=ft.TextAlign.CENTER, width=260,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        ),
        alignment=ft.Alignment.CENTER,
        expand=True,
        bgcolor=BG,
    )


class ChatMenu:
    visible_chat = False
    visible_chat_list = False

    def __init__(self, setScene: Callable):
        self.setScene = setScene

    def __call__(self, page: ft.Page):
        self.sidebar_holder = ft.Container(expand=False)
        self.main_holder = ft.Container(expand=True)
        self.root_row = ft.Row(controls=[self.sidebar_holder, self.main_holder], spacing=0, expand=True)

        # открытие чата
        def open_chat(chat_id):
            setActiveChatId(chat_id)
            setView("chat")
            chat: Chat = getChatId(chat_id)
            if chat:
                chat.unread = False
            refresh()

        # открытие профиля
        def open_profile(kto: str):
            setProfileTarget(kto)
            setView("profile")
            refresh()

        # возвращение обратно к чатам
        def go_back(): 
            if getView() == "profile":
                setView("chat" if isinstance(getActiveChatId(), int) else "empty")
            else:
                setActiveChatId(None)
                setView("empty")
            refresh()
        
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
        
        def build_sidebar():        # рендер чатов
            items = []
            for c in getChats():
                last = c.messages[-1] if c.messages else None

                try:
                    preview = "" if not last.type else getLan("Message", last.type)
                except Exception:
                    if last.type == "text":
                        preview = last.text
                    else: preview = ''

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

            # футер сайдбара: переход в свой профиль
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
                            content=ft.ListView(controls=items, spacing=2, expand=True) if items else ft.Row([ft.Text("Здесь ничего нет", size=13, color=TEXT_FAINT, text_align=ft.TextAlign.CENTER)],
                                                                                                              alignment=ft.CrossAxisAlignment.CENTER),
                            padding=8,
                            expand=True,
                            
                        ),
                        me_row,
                    ],
                    spacing=0,
                    expand=True,
                ),
                bgcolor=PANEL,
                border=ft.Border.only(right=ft.BorderSide(1, BORDER)) if not getIsNarrow() else None,
                width=300 if not getIsNarrow() else None,
                expand=True if getIsNarrow() else False,
            )
        

        def refresh():          # обновление состояние
            self.sidebar_holder.content = build_sidebar()
            self.main_holder.content = build_main()
    
            showing_main_only = getView() in ("chat", "profile")
            if getIsNarrow():
                self.sidebar_holder.visible = not showing_main_only
                self.sidebar_holder.expand = not showing_main_only
                self.main_holder.visible = showing_main_only
                self.main_holder.expand = showing_main_only
            else:
                self.sidebar_holder.visible = True
                self.sidebar_holder.expand = False
                self.main_holder.visible = True
                self.main_holder.expand = True

        def on_resize(e=None):          # ПЕРЕСТРОЙКА ЭКРАНА
            w = page.width or CONFIG.getint("WINDOW", "width")
            h = page.height or CONFIG.getint("WINDOW", "height")
            narrow = h > w
            if narrow != getIsNarrow():
                setIsNarrow(narrow)
                refresh()

            page.update()

        def build_main():               # ДИСПЕТЧЕР ОСНОВНОЙ ОБЛАСТИ
            if getView() == "profile":
                return build_profile(getProfileTarget())
            if getView() == "chat" and isinstance(getActiveChatId(), int):
                return build_chat(getActiveChatId())
            return build_empty()

        page.on_resize = on_resize
        page.add(self.root_row)

        on_resize()