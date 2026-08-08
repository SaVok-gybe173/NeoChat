from PyQt5.QtWidgets import QApplication


LIGHT_THEME = """
    QWidget {
        background-color: #f0f0f0;
        color: #000000;
    }

    QPushButton {
        background-color: #e0e0e0;
        border: 1px solid #a0a0a0;
        border-radius: 5px;
        padding: 5px 5px;
    }
    QPushButton:hover {
        background-color: #d0d0d0;
    }
    QPushButton:pressed {
        background-color: #c0c0c0;
    }
    QPushButton:disabled {
        background-color: #eeeeee;
        color: #a0a0a0;
        border: 1px solid #cccccc;
    }
    QPushButton:default {
        border: 1px solid #4a90d9;
    }

    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: white;
        border: 1px solid #a0a0a0;
        border-radius: 3px;
        padding: 3px;
        selection-background-color: #4a90d9;
        selection-color: white;
    }
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border: 1px solid #4a90d9;
    }
    QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
        background-color: #f5f5f5;
        color: #a0a0a0;
    }

    QComboBox {
        background-color: white;
        border: 1px solid #a0a0a0;
        border-radius: 3px;
        padding: 3px 6px;
        min-height: 20px;
    }
    QComboBox:hover {
        border: 1px solid #808080;
    }
    QComboBox:on {
        border: 1px solid #4a90d9;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox QAbstractItemView {
        background-color: white;
        border: 1px solid #a0a0a0;
        selection-background-color: #4a90d9;
        selection-color: white;
        outline: none;
    }

    QCheckBox, QRadioButton {
        spacing: 6px;
        background-color: transparent;
    }
    QCheckBox::indicator, QRadioButton::indicator {
        width: 15px;
        height: 15px;
        background-color: white;
        border: 1px solid #a0a0a0;
    }
    QCheckBox::indicator {
        border-radius: 3px;
    }
    QRadioButton::indicator {
        border-radius: 8px;
    }
    QCheckBox::indicator:hover, QRadioButton::indicator:hover {
        border: 1px solid #4a90d9;
    }
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {
        background-color: #4a90d9;
        border: 1px solid #4a90d9;
    }
    QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {
        background-color: #eeeeee;
        border: 1px solid #cccccc;
    }

    QTabWidget::pane {
        border: 1px solid #a0a0a0;
        background-color: #f0f0f0;
    }
    QTabBar::tab {
        background-color: #e0e0e0;
        border: 1px solid #a0a0a0;
        border-bottom: none;
        padding: 5px 12px;
        margin-right: 2px;
    }
    QTabBar::tab:selected {
        background-color: #f0f0f0;
        font-weight: bold;
    }
    QTabBar::tab:hover:!selected {
        background-color: #d0d0d0;
    }

    QMenuBar {
        background-color: #f0f0f0;
        border-bottom: 1px solid #a0a0a0;
    }
    QMenuBar::item:selected {
        background-color: #d0d0d0;
    }
    QMenu {
        background-color: white;
        border: 1px solid #a0a0a0;
    }
    QMenu::item:selected {
        background-color: #4a90d9;
        color: white;
    }
    QMenu::separator {
        height: 1px;
        background-color: #cccccc;
        margin: 4px 8px;
    }

    QScrollBar:vertical {
        background-color: #f0f0f0;
        width: 12px;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background-color: #c0c0c0;
        border-radius: 5px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #a0a0a0;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
    QScrollBar:horizontal {
        background-color: #f0f0f0;
        height: 12px;
        margin: 0;
    }
    QScrollBar::handle:horizontal {
        background-color: #c0c0c0;
        border-radius: 5px;
        min-width: 20px;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: #a0a0a0;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0;
    }

    QSlider::groove:horizontal {
        border: 1px solid #a0a0a0;
        height: 4px;
        background-color: #d0d0d0;
        border-radius: 2px;
    } 
    QSlider::handle:horizontal {
        background-color: #4a90d9;
        border: 1px solid #3a7bc0;
        width: 14px;
        margin: -6px 0;
        border-radius: 7px;
    }

    QProgressBar {
        background-color: white;
        border: 1px solid #a0a0a0;
        border-radius: 3px;
        text-align: center;
    }
    QProgressBar::chunk {
        background-color: #4a90d9;
        border-radius: 2px;
    }

    QGroupBox {
        border: 1px solid #a0a0a0;
        border-radius: 5px;
        margin-top: 10px;
        padding-top: 10px;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }

    QSpinBox, QDoubleSpinBox {
        background-color: white;
        border: 1px solid #a0a0a0;
        border-radius: 3px;
        padding: 3px;
    }

    QTableWidget, QListWidget, QTreeWidget {
        background-color: white;
        border: 1px solid #a0a0a0;
        gridline-color: #dddddd;
        selection-background-color: #4a90d9;
        selection-color: white;
    }
    QHeaderView::section {
        background-color: #e0e0e0;
        border: 1px solid #a0a0a0;
        padding: 4px;
    }

    QStatusBar {
        background-color: #e8e8e8;
        border-top: 1px solid #a0a0a0;
    }
    QToolBar {
        background-color: #e8e8e8;
        border: none;
        spacing: 3px;
    }
    QToolTip {
        background-color: #ffffe0;
        color: #000000;
        border: 1px solid #a0a0a0;
        padding: 3px;
    }
"""

DARK_THEME = """
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
    }

    QPushButton {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        border-radius: 5px;
        padding: 5px 5px;
        color: #ffffff;
    }
    QPushButton:hover {
        background-color: #4a4a4a;
    }
    QPushButton:pressed {
        background-color: #565656;
    }
    QPushButton:disabled {
        background-color: #333333;
        color: #777777;
        border: 1px solid #444444;
    }
    QPushButton:default {
        border: 1px solid #5c9fe0;
    }

    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        border-radius: 3px;
        padding: 3px;
        color: #ffffff;
        selection-background-color: #5c9fe0;
        selection-color: #ffffff;
    }
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border: 1px solid #5c9fe0;
    }
    QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
        background-color: #333333;
        color: #777777;
    }

    QComboBox {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        border-radius: 3px;
        padding: 3px 6px;
        color: #ffffff;
        min-height: 20px;
    }
    QComboBox:hover {
        border: 1px solid #666666;
    }
    QComboBox:on {
        border: 1px solid #5c9fe0;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox QAbstractItemView {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        color: #ffffff;
        selection-background-color: #5c9fe0;
        selection-color: #ffffff;
        outline: none;
    }

    QCheckBox, QRadioButton {
        spacing: 6px;
        background-color: transparent;
    }
    QCheckBox::indicator, QRadioButton::indicator {
        width: 15px;
        height: 15px;
        background-color: #3c3c3c;
        border: 1px solid #555555;
    }
    QCheckBox::indicator {
        border-radius: 3px;
    }
    QRadioButton::indicator {
        border-radius: 8px;
    }
    QCheckBox::indicator:hover, QRadioButton::indicator:hover {
        border: 1px solid #5c9fe0;
    }
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {
        background-color: #5c9fe0;
        border: 1px solid #5c9fe0;
    }
    QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {
        background-color: #333333;
        border: 1px solid #444444;
    }

    QTabWidget::pane {
        border: 1px solid #555555;
        background-color: #2b2b2b;
    }
    QTabBar::tab {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        border-bottom: none;
        padding: 5px 12px;
        margin-right: 2px;
        color: #ffffff;
    }
    QTabBar::tab:selected {
        background-color: #2b2b2b;
        font-weight: bold;
    }
    QTabBar::tab:hover:!selected {
        background-color: #4a4a4a;
    }

    QMenuBar {
        background-color: #2b2b2b;
        border-bottom: 1px solid #555555;
    }
    QMenuBar::item:selected {
        background-color: #4a4a4a;
    }
    QMenu {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        color: #ffffff;
    }
    QMenu::item:selected {
        background-color: #5c9fe0;
        color: #ffffff;
    }
    QMenu::separator {
        height: 1px;
        background-color: #555555;
        margin: 4px 8px;
    }

    QScrollBar:vertical {
        background-color: #2b2b2b;
        width: 12px;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background-color: #555555;
        border-radius: 5px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #666666;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
    QScrollBar:horizontal {
        background-color: #2b2b2b;
        height: 12px;
        margin: 0;
    }
    QScrollBar::handle:horizontal {
        background-color: #555555;
        border-radius: 5px;
        min-width: 20px;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: #666666;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0;
    }

    QSlider::groove:horizontal {
        border: 1px solid #555555;
        height: 4px;
        background-color: #3c3c3c;
        border-radius: 2px;
    }
    QSlider::handle:horizontal {
        background-color: #5c9fe0;
        border: 1px solid #4a8bcf;
        width: 14px;
        margin: -6px 0;
        border-radius: 7px;
    }

    QProgressBar {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        border-radius: 3px;
        text-align: center;
        color: #ffffff;
    }
    QProgressBar::chunk {
        background-color: #5c9fe0;
        border-radius: 2px;
    }

    QGroupBox {
        border: 1px solid #555555;
        border-radius: 5px;
        margin-top: 10px;
        padding-top: 10px;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }

    QSpinBox, QDoubleSpinBox {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        border-radius: 3px;
        padding: 3px;
        color: #ffffff;
    }

    QTableWidget, QListWidget, QTreeWidget {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        gridline-color: #4a4a4a;
        color: #ffffff;
        selection-background-color: #5c9fe0;
        selection-color: #ffffff;
    }
    QHeaderView::section {
        background-color: #3c3c3c;
        border: 1px solid #555555;
        padding: 4px;
        color: #ffffff;
    }

    QStatusBar {
        background-color: #262626;
        border-top: 1px solid #555555;
    }
    QToolBar {
        background-color: #262626;
        border: none;
        spacing: 3px;
    }
    QToolTip {
        background-color: #3c3c3c;
        color: #ffffff;
        border: 1px solid #555555;
        padding: 3px;
    }
"""

GREEN_THEME = """
    QWidget {
        background-color: #e8f5e9;
        color: #1b5e20;
    }

    QPushButton {
        background-color: #a5d6a7;
        border: 1px solid #388e3c;
        border-radius: 5px;
        padding: 5px 5px;
        color: #1b5e20;
    }
    QPushButton:hover {
        background-color: #81c784;
    }
    QPushButton:pressed {
        background-color: #66bb6a;
    }
    QPushButton:disabled {
        background-color: #d5e8d6;
        color: #8fae90;
        border: 1px solid #b8d4b9;
    }
    QPushButton:default {
        border: 1px solid #2e7d32;
    }

    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #ffffff;
        border: 1px solid #388e3c;
        border-radius: 3px;
        padding: 3px;
        color: #1b5e20;
        selection-background-color: #66bb6a;
        selection-color: #ffffff;
    }
    QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
        border: 1px solid #2e7d32;
    }
    QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {
        background-color: #eef7ee;
        color: #8fae90;
    }

    QComboBox {
        background-color: #ffffff;
        border: 1px solid #388e3c;
        border-radius: 3px;
        padding: 3px 6px;
        min-height: 20px;
    }
    QComboBox:hover {
        border: 1px solid #2e7d32;
    }
    QComboBox:on {
        border: 1px solid #1b5e20;
    }
    QComboBox::drop-down {
        border: none;
        width: 20px;
    }
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        border: 1px solid #388e3c;
        selection-background-color: #66bb6a;
        selection-color: #ffffff;
        outline: none;
    }

    QCheckBox, QRadioButton {
        spacing: 6px;
        background-color: transparent;
    }
    QCheckBox::indicator, QRadioButton::indicator {
        width: 15px;
        height: 15px;
        background-color: #ffffff;
        border: 1px solid #388e3c;
    }
    QCheckBox::indicator {
        border-radius: 3px;
    }
    QRadioButton::indicator {
        border-radius: 8px;
    }
    QCheckBox::indicator:hover, QRadioButton::indicator:hover {
        border: 1px solid #2e7d32;
    }
    QCheckBox::indicator:checked, QRadioButton::indicator:checked {
        background-color: #388e3c;
        border: 1px solid #2e7d32;
    }
    QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {
        background-color: #eef7ee;
        border: 1px solid #b8d4b9;
    }

    QTabWidget::pane {
        border: 1px solid #388e3c;
        background-color: #e8f5e9;
    }
    QTabBar::tab {
        background-color: #a5d6a7;
        border: 1px solid #388e3c;
        border-bottom: none;
        padding: 5px 12px;
        margin-right: 2px;
        color: #1b5e20;
    }
    QTabBar::tab:selected {
        background-color: #e8f5e9;
        font-weight: bold;
    }
    QTabBar::tab:hover:!selected {
        background-color: #81c784;
    }

    QMenuBar {
        background-color: #e8f5e9;
        border-bottom: 1px solid #388e3c;
    }
    QMenuBar::item:selected {
        background-color: #81c784;
    }
    QMenu {
        background-color: #ffffff;
        border: 1px solid #388e3c;
    }
    QMenu::item:selected {
        background-color: #66bb6a;
        color: #ffffff;
    }
    QMenu::separator {
        height: 1px;
        background-color: #b8d4b9;
        margin: 4px 8px;
    }

    QScrollBar:vertical {
        background-color: #e8f5e9;
        width: 12px;
        margin: 0;
    }
    QScrollBar::handle:vertical {
        background-color: #a5d6a7;
        border-radius: 5px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #81c784;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
    QScrollBar:horizontal {
        background-color: #e8f5e9;
        height: 12px;
        margin: 0;
    }
    QScrollBar::handle:horizontal {
        background-color: #a5d6a7;
        border-radius: 5px;
        min-width: 20px;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: #81c784;
    }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        width: 0;
    }

    QSlider::groove:horizontal {
        border: 1px solid #388e3c;
        height: 4px;
        background-color: #c8e6c9;
        border-radius: 2px;
    }
    QSlider::handle:horizontal {
        background-color: #388e3c;
        border: 1px solid #2e7d32;
        width: 14px;
        margin: -6px 0;
        border-radius: 7px;
    }

    QProgressBar {
        background-color: #ffffff;
        border: 1px solid #388e3c;
        border-radius: 3px;
        text-align: center;
        color: #1b5e20;
    }
    QProgressBar::chunk {
        background-color: #388e3c;
        border-radius: 2px;
    }

    QGroupBox {
        border: 1px solid #388e3c;
        border-radius: 5px;
        margin-top: 10px;
        padding-top: 10px;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px;
    }

    QSpinBox, QDoubleSpinBox {
        background-color: #ffffff;
        border: 1px solid #388e3c;
        border-radius: 3px;
        padding: 3px;
    }

    QTableWidget, QListWidget, QTreeWidget {
        background-color: #ffffff;
        border: 1px solid #388e3c;
        gridline-color: #c8e6c9;
        selection-background-color: #66bb6a;
        selection-color: #ffffff;
    }
    QHeaderView::section {
        background-color: #a5d6a7;
        border: 1px solid #388e3c;
        padding: 4px;
        color: #1b5e20;
    }

    QStatusBar {
        background-color: #c8e6c9;
        border-top: 1px solid #388e3c;
    }
    QToolBar {
        background-color: #c8e6c9;
        border: none;
        spacing: 3px;
    }
    QToolTip {
        background-color: #ffffe0;
        color: #1b5e20;
        border: 1px solid #388e3c;
        padding: 3px;
    }
"""

def apply_theme(theme_name):
    """Применяет тему по её имени."""
    themes = {
        'light': LIGHT_THEME,
        'dark': DARK_THEME,
        'green': GREEN_THEME
    }
    # Получаем экземпляр QApplication
    app = QApplication.instance()
    if app and theme_name in themes:
        app.setStyleSheet(themes[theme_name])
    else:
        print(f"Тема '{theme_name}' не найдена")