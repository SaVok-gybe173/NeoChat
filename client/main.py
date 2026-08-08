from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QHBoxLayout
)
from ui.server import MenuPage
from ui.themes import apply_theme

import sys, os

def main():
    app = QApplication(sys.argv)

    window = QMainWindow()

    window.setWindowTitle("Neo Chat")
    window.setGeometry(200, 200, 450, 650)

    stacked_widget = QStackedWidget()
    window.setCentralWidget(stacked_widget)
    
    #central_widget = QWidget()
    #window.setCentralWidget(central_widget)
    layout = QVBoxLayout(stacked_widget)

    menu_page = MenuPage(lambda: stacked_widget.setCurrentIndex(0))

    stacked_widget.addWidget(menu_page)
    stacked_widget.setCurrentIndex(0)

    apply_theme('dark')

    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()