import sys
from PyQt5.QtWidgets import QWidget, QHBoxLayout


class MenuPage(QWidget):
    """Страница с меню"""
    def __init__(self, switch_to_main_callback):
        super().__init__()
        central = QWidget()

        self.layout: QHBoxLayout = QHBoxLayout(central)

        self.layout.setContentsMargins(0, 0, 0, 0)

    def resizeEvent(self, event):
        # Получаем текущие размеры центрального виджета
        width = self.centralWidget().width()
        height = self.centralWidget().height()

        # Задаём проценты: например, 10% слева и справа, 5% сверху и снизу
        left = int(width * 0.10)
        right = int(width * 0.10)
        top = int(height * 0.05)
        bottom = int(height * 0.05)

        # Применяем пересчитанные отступы
        self.layout.setContentsMargins(left, top, right, bottom)

        # Важно: вызываем родительский обработчик, чтобы не нарушить стандартное поведение
        super().resizeEvent(event)