from typing import Callable
from language import getLan
import flet as ft

ACCENT = "#5b8cff"
PANEL = "#171a21"
PANEL_BORDER = "#262b35"
MUTED = "#8a91a3"
TEXT = "#eef1f6"
DANGER = "#ff6b6b"
SUCCESS = "#4caf59"

class CodeMenu:
    def __init__(self, setScene: Callable):
        self.setScene = setScene

    def __call__(self, page: ft.Page):

        # поле для ввода кода
        code_field = ft.TextField(
            label=getLan("CodMenu", "code-from-letter"),
            hint_text=getLan("CodMenu", "enter-6-digits"),
            max_length=6,
            keyboard_type=ft.KeyboardType.NUMBER,
            border_color=PANEL_BORDER,
            focused_border_color=ACCENT,
            color=TEXT,
            label_style=ft.TextStyle(color=MUTED),
            bgcolor="#11141a",
            border_radius=10,
            text_align=ft.TextAlign.CENTER,
            width=200,
            height=56,
        )
    
        error_text = ft.Text("", color=DANGER, size=13, visible=False)
    
        
    
        def on_verify_click(e): # переход на экран смены пароля
            code = code_field.value 
            if not code:
                error_text.value = getLan("CodMenu", "enter-code")
                error_text.visible = True
                page.update()
                return
    
            if len(code) != 6 or not code.isdigit():
                error_text.value = getLan("CodMenu", "code-must-contain-exactly-6-digits")
                error_text.visible = True
                page.update()
                return
    
            error_text.visible = False
            
    
        def on_resend_click(e): # новый код
            pass
    
        def on_back_to_login(e): # возврат на экран входа
            pass
    
        # кнопка подтверждения
        verify_button = ft.Button(
            content=ft.Text(
                getLan("confirm"),
                color="#0f0404",
                weight=ft.FontWeight.W_600,
                size=14.5,
            ),
            width=400,
            height=46,
            bgcolor=ACCENT,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            ),
            on_click=on_verify_click,
        )
    
        # ссылки
        resend_link = ft.TextButton(
            content=ft.Text(getLan("CodMenu", "send-code-again")),
            style=ft.ButtonStyle(color=ACCENT),
            on_click=on_resend_click,
        )
    
        back_link = ft.TextButton(
            content=ft.Text(getLan("RecoveryMenu", "return-entrance")),
            style=ft.ButtonStyle(color=MUTED),
            on_click=on_back_to_login,
        )
    
        # основная карточка
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
                            ft.Text(getLan("CodMenu", "confirmation"), size=22, weight=ft.FontWeight.W_600, color=TEXT),
                            ft.Text(getLan("CodMenu", "enter-6-digit-code-sent-emai"), size=14, color=MUTED),
                        ],
                    ),

                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[code_field],
                    ),
                    error_text,
                    verify_button,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[resend_link],
                    ),
                    ft.Divider(color=PANEL_BORDER, height=20),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[back_link],
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