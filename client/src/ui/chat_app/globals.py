from typing import Callable

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

# глобальное обновление состояния
_refresh = lambda: None
def getRefresh() -> Callable:
    global _refresh
    return _refresh

def setRefresh(refresh: Callable) -> None:
    global _refresh
    _refresh = refresh

def refresh() -> None:
    global _refresh
    _refresh()