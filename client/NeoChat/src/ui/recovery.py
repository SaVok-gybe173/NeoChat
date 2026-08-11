from typing import Callable
import flet as ft

ACCENT = "#5b8cff"
PANEL = "#171a21"
PANEL_BORDER = "#262b35"
MUTED = "#8a91a3"
TEXT = "#eef1f6"
DANGER = "#ff6b6b"
SUCCESS = "#4caf50"

class RecoveryMenu:
    def __init__(self, setScene: Callable):
        self.setScene = setScene

    def __call__(self, page: ft.Page):

        email_field = ft.TextField(
            label="Email",
            hint_text="example@mail.com",
            border_color=PANEL_BORDER,
            focused_border_color=ACCENT,
            color=TEXT,
            label_style=ft.TextStyle(color=MUTED),
            bgcolor="#11141a",
            border_radius=10,
        )
    
        error_text = ft.Text("", color=DANGER, size=13, visible=False)
    
        def on_send_click(e): # переход обратно на экран входа
            if not email_field.value:
                error_text.value = "Введите email"
                error_text.visible = True
                page.update()
                return
    
            # Простейшая проверка наличия @
            if "@" not in email_field.value:
                error_text.value = "Введите корректный email"
                error_text.visible = True
                page.update()
                return
    
            error_text.visible = False

    
        def on_back_to_login(e): # Переход на экран входа
            self.setScene(1)
    
        # Кнопка отправки
        send_button = ft.Button(
            content=ft.Text(
                "Отправить",
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
            on_click=on_send_click,
        )
    
        # Ссылка "Вернуться ко входу"
        back_link = ft.TextButton(
            content=ft.Text("Вернуться ко входу"),
            style=ft.ButtonStyle(color=ACCENT),
            on_click=on_back_to_login,
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
                            ft.Text("Восстановление пароля", size=22, weight=ft.FontWeight.W_600, color=TEXT),
                            ft.Text("Введите email, и мы пришлём код для сброса", size=14, color=MUTED),
                        ],
                    ),
                    email_field,
                    error_text,
                    send_button,
                    ft.Divider(color=PANEL_BORDER, height=20),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            back_link,
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
        
