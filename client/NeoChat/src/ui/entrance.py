from typing import Callable
from network.client_api import serverEntrance
from language import LAN, getLan
import flet as ft

ACCENT = "#5b8cff"
PANEL = "#171a21"
PANEL_BORDER = "#262b35"
MUTED = "#8a91a3"
TEXT = "#eef1f6"
DANGER = "#ff6b6b"

class EntranceServer:
    def __init__(self, setScene: Callable):
        self.setScene = setScene

    def __call__(self, page: ft.Page):
        login_field = ft.TextField(
                label=getLan("EntranceServer", "login"),
                hint_text=getLan("EntranceServer", "login-email"),
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

        error_text = ft.Text("", color=DANGER, size=13, visible=False)

        def on_login_click(e): # вход
            if not login_field.value or not password_field.value:
                error_text.value = getLan("EntranceServer", "fill-login-password")
                error_text.visible = True
                page.update()
                return
            try:
                serverEntrance(login_field.value, password_field.value)
                error_text.visible = False
                self.setScene("ChatMenu")
            except Exception as e:
                print(e, type(e))
                error_text.visible = True
                error_text.value = str(e)

    
        def on_forgot_click(e): # сброс пароля
            self.setScene("RecoveryMenu")
    
        def on_register_click(e): # регестрация
            self.setScene("RegistrationMenu")

        login_button = ft.Button(
                content=ft.Text(
                    getLan("log-in"),
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
                on_click=on_login_click,
            )

        forgot_button = ft.TextButton(
                content=ft.Text(getLan("EntranceServer", "forgot-password")),
                style=ft.ButtonStyle(color=ACCENT),
                on_click=on_forgot_click,
            )
        
        register_button = ft.TextButton(
                content=ft.Text(getLan("RegistrationMenu", "register")),
                style=ft.ButtonStyle(color=ACCENT),
                on_click=on_register_click,
            )

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
                        ft.Column(
                            spacing=4,
                            controls=[
                                ft.Text(getLan("EntranceServer", "account-login"), size=22, weight=ft.FontWeight.W_600, color=TEXT),
                                ft.Text(getLan("EntranceServer", "enter-login-password-continue"), size=14, color=MUTED),
                            ],
                        ),
                        login_field,
                        password_field,
                        error_text,
                        ft.Row(alignment=ft.MainAxisAlignment.END, controls=[forgot_button]),
                        login_button,
                        ft.Divider(color=PANEL_BORDER, height=20),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text(getLan("EntranceServer", "no-account"), size=13.5, color=MUTED),
                                register_button,
                            ],
                        ),
                    ],
                ),
            )

        page.add(
            ft.Container(
                expand=True,
                alignment=ft.Alignment(0, 0),  # center
                content=card,
            )
        )