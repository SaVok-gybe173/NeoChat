import sys
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel, QScrollArea
from PyQt5.QtCore import Qt
from core.storege import getListStorege  # предполагаем, что это функция

class MenuPage(QWidget):
    def __init__(self, switch_to_main_callback):
        super().__init__()
        self.layout: QHBoxLayout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        self.items_layout = QVBoxLayout(container)
        self.items_layout.setAlignment(Qt.AlignTop)
        self.items_layout.setSpacing(5)

        for name in getListStorege():
            item = QWidget()
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(5, 5, 0, 0)

            label = QLabel(name)
            pushe = QPushButton(">")
            pushe.setFixedSize(25, 25)
            delite = QPushButton("x")
            delite.setFixedSize(25, 25)
            delite.clicked.connect(lambda checked, w=item, n=name: self.remove_item(w, n))
            #pushe.clicked.connect(lambda checked, w=item, n=name: self.remove_item(w, n))
            item_layout.addWidget(label)
            item_layout.addStretch()
            item_layout.addWidget(delite)
            item_layout.addWidget(pushe)

            self.items_layout.addWidget(item)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)
        self.layout.addWidget(scroll)

    def remove_item(self, widget: QWidget, name: str):
        """Удаляет элемент из списка"""
        self.items_layout.removeWidget(widget)
        widget.deleteLater()


    def resizeEvent(self, event):
        width = self.width()
        height = self.height()

        left = int(width * 0.10)
        right = int(width * 0.10)
        top = int(height * 0.05)
        bottom = int(height * 0.15)

        self.layout.setContentsMargins(left, top, right, bottom)
        super().resizeEvent(event) 

