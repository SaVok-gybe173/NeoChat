from storage.server import SERVERS, addServer, Server, updateServer, configStoregeServer, serverSet, isConectGet, isConectSet
from language import LAN, getLan
from typing import Callable

import asyncio
import flet as ft


class ServerMenu:
    def __init__(self, setScene: Callable):
        self.setScene = setScene # для смены индекса сценны

    def __call__(self, page: ft.Page):
        self.page = page

        state = {"query": "", "region": getLan("server", "all-regions"), "sort": getLan("server", "ping"), "servers": SERVERS}
        
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
            return {"online": getLan("server", "online"), "offline": getLan("server", "offline"), "maintenance": getLan("server", "maintenance")}.get(status, status)
    
        def toggle_favorite(srv): # звездочка
            def handler(e):
                srv.favorite = not srv.favorite
                configStoregeServer(srv)
                render_list()
            return handler
    
        async def connect(srv: Server): # подключение
            if isConectGet():
                page.show_dialog(
                                ft.SnackBar(ft.Text(f"{getLan('server',"busy-connecting")}..."), bgcolor="#c21010")
                            )
                page.update()
                return

            isConectSet(True)

            page.show_dialog(
                ft.SnackBar(ft.Text(f"{getLan('server','connecting-to')} «{srv.name}»..."), bgcolor="#1d9e75")
            )
            page.update()

            success = await asyncio.to_thread(srv.conect)

            if not success:
                page.show_dialog(
                    ft.SnackBar(ft.Text(f"{getLan('server',"error-connecting-to")} «{srv.name}»..."), bgcolor="#c21010")
                )
                page.update()
            isConectSet(False)
                

            
    
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
                                            f"{srv.mode} · {srv.region}",
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
                                            f"{srv.ping} {getLan("server", "ms")}" if srv.status == "online" else "—",
                                            size=13,
                                            weight=ft.FontWeight.W_500,
                                            color=ping_color(srv.ping, srv.status),
                                        ),
                                        ft.Text(status_label(srv.status), size=11, color=ft.Colors.GREY_500),
                                    ],
                                ),
                                ft.ElevatedButton(
                                    getLan("join"),
                                    disabled=disabled,
                                    on_click= lambda e, s=srv: page.run_task(connect, s),
                                    bgcolor=ft.Colors.WHITE if not disabled else None,
                                    color=ft.Colors.BLACK if not disabled else None,
                                ),
                            ],
                        ),
                    ],
                ),
            )
    
        def render_list(): # обновление списка
            filtered = [
                s for s in state["servers"]
                if state["query"].lower() in s.name.lower()
                and (state["region"] == getLan("server", "all-regions") or s.region == state["region"])
            ]

            if state["sort"] == getLan("server", "ping"):
                filtered.sort(key=lambda s: (s.status != "online", s.ping))
            #elif state["sort"] == getLan("server", "Popularity"):
                #filtered.sort(key=lambda s: -s.players)
            elif state["sort"] == getLan("server", "Alphabet"):
                filtered.sort(key=lambda s: s.name)
    
            # избранные всегда наверх
            filtered.sort(key=lambda s: not s.favorite)
    
            server_list.controls = [server_row(s) for s in filtered]
            if not filtered:
                server_list.controls = [
                    ft.Container(
                        padding=30,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Text(getLan("server", "Servers-not-found"), color=ft.Colors.GREY_500),
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
    
        def refresh(e): # обновление списка серверов
            updateServer()
            for s in state["servers"]:
                if s.status == "online":
                    s.ping = max(10, s.ping)
                    #s.players = min(s.max_players, max(0, s.players))
            page.show_dialog(ft.SnackBar(ft.Text(getLan("server", "list-servers-updated"))))
            render_list()
        
        def quick_connect(e): # автоподключение
            online = [s for s in state["servers"] if s.status == "online"]
            if online:
                best = min(online, key=lambda s: s.ping)
                page.run_task(connect, best)
                #page.show_dialog(ft.SnackBar(ft.Text(f"{getLan("server", "autoconnecting-to")} «{best.name}» ({best.ping} мс)"), bgcolor="#1d9e75"))
    
        def add_by_ip(e): # виджет поверх экрана для добаления сервера
            def close_dialog(ev): # закрытие
                page.pop_dialog()
    
            def confirm_add(ev): # добаление
                ip = ip_field.value.strip()
                page.pop_dialog()
                if ip:
                    try:
                        addServer(*ip.split(":"))
                    except Exception as e:
                        print("Ошибка:", e)
                    render_list()
                
            
            ip_field = ft.TextField(label=getLan("server", "server-IP-address"), hint_text="127.0.0.1:8080", autofocus=True)
            dlg = ft.AlertDialog(
                title=ft.Text(getLan("server", "server-by-IP-address")),
                content=ip_field,
                actions=[
                    ft.TextButton(getLan("Cancellation"), on_click=close_dialog),
                    #ft.FilledButton(getLan("Add"), on_click= (lambda e: threading.Thread(target=confirm_add, args=(e,), daemon=True).start()) ),
                    ft.FilledButton(getLan("Add"), on_click=confirm_add ),
                ],
            )
            page.show_dialog(dlg)
    
        # --- Панель фильтров ---
        search_field = ft.TextField(
            hint_text=getLan("server", "Server-search"),
            expand=True,
            prefix_icon=ft.Icons.SEARCH,
            on_change=on_search,
            border_radius=8,
            height=44,
        )
    
        region_dropdown = ft.Dropdown(
            value=getLan("server", "all-regions"),
            width=150,
            options=[ft.DropdownOption(key=r, text=r) for r in [getLan("server", "all-regions"), "EU", "RU", "null"]],
            on_select=on_region_change,
        )
    
        sort_dropdown = ft.Dropdown(
            value=getLan("server", "ping"),
            width=150,
            options=[ft.DropdownOption(key=s, text=s) for s in [getLan("server", "ping"), getLan("server", "Alphabet")]],
            on_select=on_sort_change,
        )
        
        #refresh_button = ft.IconButton(icon=ft.Icons.REFRESH, tooltip=getLan("server", "update-list"), on_click=lambda e: threading.Thread(target=refresh, daemon=True, args=(e,)).start() )
        refresh_button = ft.IconButton(icon=ft.Icons.REFRESH, tooltip=getLan("server", "update-list"), on_click=refresh )
    
        page.add(
            ft.Text(getLan("server", "Server-selection"), size=22, weight=ft.FontWeight.W_500),
            ft.Row([search_field, region_dropdown, sort_dropdown, refresh_button]),
            ft.Container(content=server_list, expand=True, padding=ft.Padding(top=8, left=0, right=0, bottom=0)),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.OutlinedButton(getLan("server", "add-ip"), icon=ft.Icons.ADD, on_click=add_by_ip),
                    ft.OutlinedButton(getLan("server", "fast-connection"), icon=ft.Icons.BOLT, on_click=quick_connect),
                ],
            ),
        )
    
        render_list()
