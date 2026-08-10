import flet as ft
import random

# --- Модель данных сервера ---
class Server:
    def __init__(self, name, region, mode, players, max_players, ping, status="online", favorite=False, locked=False):
        self.name = name
        self.region = region
        self.mode = mode
        self.players = players
        self.max_players = max_players
        self.ping = ping
        self.status = status  # online / offline / maintenance
        self.favorite = favorite
        self.locked = locked


SERVERS = [
    Server("Vanilla EU #1", "EU", "PvE", 1450, 2000, 24, favorite=True),
    Server("Hardcore PvP Asia", "Asia", "PvP", 890, 1000, 112),
    Server("Private Clan Server", "NA", "Modded", 0, 100, 0, status="maintenance", locked=True),
    Server("Roleplay NA West", "NA", "RP", 340, 500, 78),
    Server("Vanilla EU #2", "EU", "PvE", 1980, 2000, 31),
    Server("Casual PvP EU", "EU", "PvP", 210, 800, 45),
]


def main(page: ft.Page):
    page.title = "Выбор сервера"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#141414"
    page.padding = 20
    page.window = ft.Window(width=720, height=640)

    # --- Состояние фильтров ---
    state = {"query": "", "region": "Все регионы", "sort": "Пинг", "servers": SERVERS}

    server_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    def ping_color(ping, status):
        if status != "online":
            return ft.Colors.RED_400
        if ping < 60:
            return ft.Colors.GREEN_400
        if ping < 120:
            return ft.Colors.AMBER_400
        return ft.Colors.RED_400

    def status_label(status):
        return {"online": "онлайн", "offline": "офлайн", "maintenance": "техработы"}.get(status, status)

    def toggle_favorite(srv):
        def handler(e):
            srv.favorite = not srv.favorite
            render_list()
        return handler

    def connect(srv):
        def handler(e):
            page.show_dialog(
                ft.SnackBar(ft.Text(f"Подключаемся к «{srv.name}»..."), bgcolor="#1d9e75")
            )
        return handler

    def server_row(srv: Server):
        disabled = srv.status != "online"
        return ft.Container(
            bgcolor="#1e1e1e",
            border_radius=10,
            padding=ft.Padding(top=10, bottom=10, left=16, right=16),
            opacity=0.55 if disabled else 1,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=10,
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.STAR if srv.favorite else ft.Icons.STAR_BORDER,
                                icon_color=ft.Colors.AMBER_400 if srv.favorite else ft.Colors.GREY_500,
                                icon_size=18,
                                on_click=toggle_favorite(srv),
                            ),
                            ft.Icon(ft.Icons.LOCK, size=16, color=ft.Colors.GREY_500) if srv.locked else ft.Container(width=16),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(srv.name, size=15, weight=ft.FontWeight.W_500),
                                    ft.Text(
                                        f"{srv.mode} · {srv.region} · {srv.players}/{srv.max_players} игроков",
                                        size=12,
                                        color=ft.Colors.GREY_400,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=16,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Column(
                                spacing=0,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                controls=[
                                    ft.Text(
                                        f"{srv.ping} мс" if srv.status == "online" else "—",
                                        size=13,
                                        weight=ft.FontWeight.W_500,
                                        color=ping_color(srv.ping, srv.status),
                                    ),
                                    ft.Text(status_label(srv.status), size=11, color=ft.Colors.GREY_500),
                                ],
                            ),
                            ft.ElevatedButton(
                                "Играть",
                                disabled=disabled,
                                on_click=connect(srv),
                                bgcolor=ft.Colors.WHITE if not disabled else None,
                                color=ft.Colors.BLACK if not disabled else None,
                            ),
                        ],
                    ),
                ],
            ),
        )

    def render_list():
        filtered = [
            s for s in state["servers"]
            if state["query"].lower() in s.name.lower()
            and (state["region"] == "Все регионы" or s.region == state["region"])
        ]

        if state["sort"] == "Пинг":
            filtered.sort(key=lambda s: (s.status != "online", s.ping))
        elif state["sort"] == "Популярность":
            filtered.sort(key=lambda s: -s.players)
        elif state["sort"] == "Алфавит":
            filtered.sort(key=lambda s: s.name)

        # избранные всегда наверх
        filtered.sort(key=lambda s: not s.favorite)

        server_list.controls = [server_row(s) for s in filtered]
        if not filtered:
            server_list.controls = [
                ft.Container(
                    padding=30,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Text("Серверы не найдены", color=ft.Colors.GREY_500),
                )
            ]
        page.update()

    def on_search(e):
        state["query"] = e.control.value
        render_list()

    def on_region_change(e):
        state["region"] = e.control.value
        render_list()

    def on_sort_change(e):
        state["sort"] = e.control.value
        render_list()

    def refresh(e):
        for s in state["servers"]:
            if s.status == "online":
                s.ping = max(10, s.ping + random.randint(-15, 15))
                s.players = min(s.max_players, max(0, s.players + random.randint(-40, 40)))
        page.show_dialog(ft.SnackBar(ft.Text("Список серверов обновлён")))
        render_list()

    def quick_connect(e):
        online = [s for s in state["servers"] if s.status == "online"]
        if online:
            best = min(online, key=lambda s: s.ping)
            page.show_dialog(ft.SnackBar(ft.Text(f"Автоподключение к «{best.name}» ({best.ping} мс)"), bgcolor="#1d9e75"))

    def add_by_ip(e):
        def close_dialog(ev):
            page.pop_dialog()

        def confirm_add(ev):
            ip = ip_field.value.strip()
            if ip:
                state["servers"].append(
                    Server(f"Custom ({ip})", "NA", "Custom", 0, 100, random.randint(20, 90))
                )
                render_list()
            page.pop_dialog()

        ip_field = ft.TextField(label="IP-адрес сервера", hint_text="192.168.0.1:27015", autofocus=True)
        dlg = ft.AlertDialog(
            title=ft.Text("Добавить сервер по IP"),
            content=ip_field,
            actions=[
                ft.TextButton("Отмена", on_click=close_dialog),
                ft.FilledButton("Добавить", on_click=confirm_add),
            ],
        )
        page.show_dialog(dlg)

    # --- Панель фильтров ---
    search_field = ft.TextField(
        hint_text="Поиск сервера...",
        expand=True,
        prefix_icon=ft.Icons.SEARCH,
        on_change=on_search,
        border_radius=8,
        height=44,
    )

    region_dropdown = ft.Dropdown(
        value="Все регионы",
        width=150,
        options=[ft.DropdownOption(key=r, text=r) for r in ["Все регионы", "EU", "NA", "Asia"]],
        on_select=on_region_change,
    )

    sort_dropdown = ft.Dropdown(
        value="Пинг",
        width=150,
        options=[ft.DropdownOption(key=s, text=s) for s in ["Пинг", "Популярность", "Алфавит"]],
        on_select=on_sort_change,
    )

    refresh_button = ft.IconButton(icon=ft.Icons.REFRESH, tooltip="Обновить список", on_click=refresh)

    page.add(
        ft.Text("Выбор сервера", size=22, weight=ft.FontWeight.W_500),
        ft.Row([search_field, region_dropdown, sort_dropdown, refresh_button]),
        ft.Container(content=server_list, expand=True, padding=ft.Padding(top=8, left=0, right=0, bottom=0)),
        ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.OutlinedButton("Добавить по IP", icon=ft.Icons.ADD, on_click=add_by_ip),
                ft.OutlinedButton("Быстрое подключение", icon=ft.Icons.BOLT, on_click=quick_connect),
            ],
        ),
    )

    render_list()


if __name__ == "__main__":
    ft.app(target=main)
