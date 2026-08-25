from language import LAN, getLan
from network.client_api import serverRegistration
from typing import Callable

import flet as ft

ACCENT = "#5b8cff"
PANEL = "#171a21"
PANEL_BORDER = "#262b35"
MUTED = "#8a91a3"
TEXT = "#eef1f6"
DANGER = "#ff6b6b"
SUCCESS = "#4caf50"


class RegistrationMenu:
    def __init__(self, setScene: Callable):
        self.setScene = setScene # для смены индекса сценны

    def __call__(self, page: ft.Page):
        self.page = page

        def on_login_click(e): # Переход на экран входа
            self.setScene("EntranceServer")
            
        def on_register_click(e): # запершение регестрации
            if not all([login_field.value, email_field.value, password_field.value, confirm_field.value]): # Проверка заполненности
                error_text.value = getLan("RegistrationMenu", "fill-fields")
                error_text.visible = True
                page.update()
                return
    
            if password_field.value != confirm_field.value: # Проверка совпадения паролей
                error_text.value = getLan("RegistrationMenu", "passwords-match")
                error_text.visible = True
                page.update()
                return
            try:
                if serverRegistration(username=login_field.value, password=password_field.value, email=email_field.value):
                    self.setScene("EntranceServer")
                    error_text.visible = False
            except Exception as e:
                error_text.value = str(e)
                error_text.visible = True
            

        # Поля ввода
        login_field = ft.TextField(
            label=getLan("RegistrationMenu", "login"),
            hint_text=getLan("RegistrationMenu", "come-login"),
            border_color=PANEL_BORDER,
            focused_border_color=ACCENT,
            color=TEXT,
            label_style=ft.TextStyle(color=MUTED),
            bgcolor="#11141a",
            border_radius=10,
        )
    
        email_field = ft.TextField(
            label=getLan("RegistrationMenu", "email"),
            hint_text=getLan("RegistrationMenu", "example-mail"),
            border_color=PANEL_BORDER,
            focused_border_color=ACCENT,
            color=TEXT,
            label_style=ft.TextStyle(color=MUTED),
            bgcolor="#11141a",
            border_radius=10,
        )
    
        password_field = ft.TextField(
            label=getLan("RegistrationMenu", "password"),
            hint_text="••••••••",
            password=True,
            can_reveal_password=True,
            border_color=PANEL_BORDER,
            focused_border_color=ACCENT,
            color=TEXT,
            label_style=ft.TextStyle(color=MUTED),
            bgcolor="#11141a",
            border_radius=10,
        )
    
        confirm_field = ft.TextField(
            label=getLan("RegistrationMenu", "confirm-password"),
            hint_text="••••••••",
            password=True,
            can_reveal_password=True,
            border_color=PANEL_BORDER,
            focused_border_color=ACCENT,
            color=TEXT,
            label_style=ft.TextStyle(color=MUTED),
            bgcolor="#11141a",
            border_radius=10,
        )
    
        error_text = ft.Text("", color=DANGER, size=13, visible=False)    
    
        # Кнопка регистрации
        register_button = ft.Button(
            content=ft.Text(
                getLan("RegistrationMenu", "register"),
                color="#ffffff",
                weight=ft.FontWeight.W_600,
                size=14.5,
            ),
            width=400,
            height=46,
            bgcolor=ACCENT,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=on_register_click,
        )
    
        # Ссылка "Войти"
        login_link = ft.TextButton(
            content=ft.Text(getLan("log-in")),
            style=ft.ButtonStyle(color=ACCENT),
            on_click=on_login_click,
        )
    
        # Основная карточка
        card = ft.Container(
            width=380,
            padding=ft.Padding(left=32, right=32, top=36, bottom=28),
            bgcolor=PANEL,
            border=ft.Border(
                left=ft.BorderSide(1, PANEL_BORDER),
                top=ft.BorderSide(1, PANEL_BORDER),
                right=ft.BorderSide(1, PANEL_BORDER),
                bottom=ft.BorderSide(1, PANEL_BORDER),
            ),
            border_radius=14,
            content=ft.Column(
                spacing=16,
                tight=True,
                controls=[
                    # Заголовок
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(getLan("RegistrationMenu", "create-account"), size=22, weight=ft.FontWeight.W_600, color=TEXT),
                            ft.Text(getLan("RegistrationMenu", "please-fill-registration-data"), size=14, color=MUTED),
                        ],
                    ),
                    login_field,
                    email_field,
                    password_field,
                    confirm_field,
                    error_text,
                    register_button,
                    ft.Divider(color=PANEL_BORDER, height=20),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text(getLan("RegistrationMenu", "there-already-account"), size=13.5, color=MUTED),
                            login_link,
                        ],
                    ),
                ],
            ),
        )
    
        page.add(
            ft.Container(
                expand=True,
                alignment=ft.Alignment(0, 0),
                content=card,
            )
        )