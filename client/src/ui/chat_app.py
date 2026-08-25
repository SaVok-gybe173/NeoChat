from typing import Callable
from language import getLan
from storage import (getChats, getActiveChatId,
                    Chat, getMyProfile, 
                    getView, getIsNarrow, 
                    setIsNarrow, getProfileTarget, 
                    setActiveChatId, setView,
                    getChatId, setProfileTarget,
                    Message, Text)
from datetime import datetime
from config import CONFIG, getPage
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

def name_initials(name: str) -> str:
    parts = name.split()
    letters = "".join(p[0] for p in parts[:2] if p)
    return letters.upper() or "?"

def build_empty(): # рендр пустого окна
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

def render_message(m: Message, chat: Chat):
    page = getPage()
    if m.type == "system":
        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(m.text, size=11.5, color=TEXT_FAINT),
                    bgcolor=PANEL_2,
                    padding=ft.Padding.symmetric(horizontal=12, vertical=5),
                    border_radius=20,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    
    is_me = m.sender == "me"

    sender_label = None
    if chat.is_group and not is_me and m.sender_name:
        sender_label = ft.Text(m.sender_name, size=11.5, weight=ft.FontWeight.W_600, color=ACCENT)

    bubble = m.draw(page)

    meta = ft.Text(m.time, size=10.5, color=TEXT_FAINT)
    column_controls = ([sender_label] if sender_label else []) + [bubble, meta]
    return ft.Row(
        controls=[
            avatar(getMyProfile() if is_me else chat, size=28),
            ft.Column(
                controls=column_controls,
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.END if is_me else ft.CrossAxisAlignment.START,
            ),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.END if is_me else ft.MainAxisAlignment.START,
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
        def open_profile(kto: str | int):
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

        # рендер чатов
        def build_sidebar():
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
        

        def build_chat(chat_id):
            chat = getChatId(chat_id)
            if not(chat.render is None):
                page.run_task(chat.render.content.controls[1].content.scroll_to, offset=-1, duration=0)
                return chat.render
            elif not chat:
                return build_empty()
    
            header = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.IconButton(icon=ft.Icons.ARROW_BACK, icon_color=TEXT, #visible=getIsNarrow(),
                                       on_click=lambda e: go_back()),
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    avatar(chat, is_group=chat.is_group),
                                    ft.Column(
                                        controls=[
                                            ft.Text(chat.title, size=14.5, weight=ft.FontWeight.W_600, color=TEXT),
                                            ft.Text(
                                                f"{len(chat.members)} участников" if chat.is_group else chat.status,
                                                size=12, color=TEXT_FAINT,
                                            ),
                                        ],
                                        spacing=0,
                                    ),
                                ],
                                spacing=12,
                            ),
                            on_click=lambda e: open_profile(chat.id),
                            ink=True,
                            border_radius=8,
                            padding=ft.Padding.symmetric(horizontal=4, vertical=2),
                        ),
                    ],
                    spacing=4,
                ),
                padding=ft.Padding.symmetric(horizontal=16, vertical=14),
                border=ft.Border.only(bottom=ft.BorderSide(1, BORDER)),
            )
            
            messages_list = ft.ListView(
                controls=[render_message(m, chat) for m in chat.messages],
                spacing=16,
                auto_scroll=True,
                expand=True,
                
                
            )
            page.run_task(messages_list.scroll_to, offset=-1, duration=0)
            message_field = ft.TextField(
                hint_text="Написать сообщение…",
                border_color=BORDER,
                bgcolor=PANEL_2,
                color=TEXT,
                border_radius=12,
                content_padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                multiline=True,
                shift_enter=True,
                min_lines=1,
                max_lines=6,
                expand=True,
                autofocus=True,
            )
    
            def handle_send(e): # добавление сообщение
                value = (message_field.value or "").strip()
                if not value:
                    return
                text = Text(
                    id=f"m{len(chat.messages) + 1}",
                    sender="me",
                    time=datetime.now().strftime("%H:%M"),
                    type="text",
                    text=value,
                )
                chat.messages.append(text)
                message_field.value = ''
                messages_list.controls.append(render_message(text, chat))
                #page.run_task(messages_list.scroll_to, offset=-1, duration=0)
    
            message_field.on_submit = handle_send
    
            composer = ft.Container(
                content=ft.Row(
                    controls=[
                        message_field,
                        ft.IconButton(
                            icon=ft.Icons.SEND_ROUNDED,
                            icon_color="#ffffff",
                            bgcolor=ACCENT,
                            icon_size=18,
                            on_click=handle_send,
                        ),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                ),
                padding=ft.Padding.symmetric(horizontal=20, vertical=14),
                border=ft.Border.only(top=ft.BorderSide(1, BORDER)),
            )

            chat.render = ft.Container(
                content=ft.Column(
                    controls=[
                        header,
                        ft.Container(content=messages_list, padding=20, expand=True),
                        composer,
                    ],
                    spacing=0,
                    expand=True,
                ),
                expand=True,
                bgcolor=BG,
            )

            return chat.render

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
        refresh()
        on_resize()
        print(self.root_row)
        page.add(self.root_row)