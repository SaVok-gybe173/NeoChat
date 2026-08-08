1. Базовый класс QWidget и его основные методы
QWidget — это фундамент для создания любого элемента интерфейса. Классы-наследники (кнопки, поля ввода, окна) расширяют его функциональность.

Вот самые часто используемые методы, унаследованные от QWidget:

Метод	Назначение	Пример
show()	Отображает виджет на экране.	button.show()
hide()	Скрывает виджет.	button.hide()
setEnabled(bool)	Включает/отключает виджет (становится серым и не реагирует на действия).	button.setEnabled(False)
setVisible(bool)	Управляет видимостью виджета.	button.setVisible(True)
setGeometry(x, y, w, h)	Устанавливает абсолютную позицию (x, y) и размер (w, h) виджета.	widget.setGeometry(50, 50, 200, 100)
setStyleSheet(css)	Применяет CSS-подобные стили для изменения внешнего вида.	button.setStyleSheet('background: blue;')
setToolTip(text)	Устанавливает всплывающую подсказку, которая появляется при наведении мыши.	button.setToolTip('Нажми меня')
setLayout(layout)	Назначает менеджер компоновки для автоматического управления дочерними виджетами.	widget.setLayout(QVBoxLayout())
parent()	Возвращает родительский виджет.	parent_widget = widget.parent()
2. Основные модули PyQt5
Классы в PyQt5 сгруппированы по модулям в зависимости от их функциональности. Вот ключевые из них:

Модуль	Назначение	Примеры классов
QtCore	Ядро фреймворка. Содержит классы, не связанные с GUI: работа с файлами, временем, потоками, сигналы/слоты.	QObject, QTimer, QFile, QThread, QDate, QPoint
QtGui	Графические основы. Классы для работы со шрифтами, иконками, цветами, рисованием (QPainter).	QFont, QIcon, QColor, QPixmap, QPainter
QtWidgets	Основные элементы интерфейса. Все стандартные виджеты: окна, кнопки, поля ввода и т.д.	QApplication, QWidget, QPushButton, QLabel, QMainWindow
QtMultimedia	Для работы с аудио и видео.	QMediaPlayer, QAudioOutput
QtNetwork	Для сетевого программирования (HTTP, TCP/IP, UDP).	QTcpSocket, QNetworkRequest
QtSql	Для интеграции с базами данных (SQL).	QSqlDatabase, QSqlQuery
QtXml	Для парсинга и обработки XML-файлов.	QDomDocument, QXmlStreamReader
3. Ключевые классы модуля QtWidgets
Это те классы, с которыми вы будете работать чаще всего, создавая интерфейс.

Класс	Назначение	Ключевые методы / Сигналы
QApplication	Управляет жизненным циклом GUI-приложения, главным циклом обработки событий и глобальными настройками.	Методы: exec_() (запуск цикла), setStyleSheet() (глобальный стиль).
QMainWindow	Главное окно приложения. Предоставляет готовую структуру со строкой меню, панелями инструментов, статус-баром и центральной областью.	Методы: setCentralWidget(), menuBar(), addToolBar(), statusBar().
QDialog	Базовый класс для диалоговых окон (модальных и немодальных).	Методы: exec_() (для модального показа), accept(), reject().
QLabel	Используется для отображения текста или изображения.	Методы: setText(), text(), setPixmap().
QPushButton	Стандартная кнопка для выполнения действий по команде пользователя.	Сигналы: clicked(), pressed(), released().
Методы: setText(), text().
QLineEdit	Поле для ввода одной строки текста.	Сигналы: textChanged(), returnPressed().
Методы: setText(), text(), setPlaceholderText().
QTextEdit	Поле для ввода и отображения многострочного текста.	Сигналы: textChanged().
Методы: setPlainText(), toPlainText(), setHtml().
QCheckBox	Флажок для множественного выбора (может быть включен или выключен).	Сигналы: stateChanged(), toggled().
Методы: setChecked(), isChecked().
QRadioButton	Переключатель для выбора одного варианта из группы.	Сигналы: toggled().
Методы: setChecked(), isChecked().
QComboBox	Выпадающий список для выбора одного элемента из нескольких.	Сигналы: currentIndexChanged(), currentTextChanged().
Методы: addItem(), addItems(), currentText().
QSpinBox / QSlider	Позволяют пользователю выбирать числовое значение (SpinBox — вводом, Slider — перемещением ползунка).	Сигналы: valueChanged().
Методы: setValue(), value().
QTableWidget	Мощный виджет для отображения и редактирования табличных данных.	Методы: setRowCount(), setColumnCount(), setItem(), item().
QMenuBar	Горизонтальная панель, содержащая выпадающие меню (QMenu).	Методы: addMenu().
QStatusBar	Обычно располагается внизу главного окна и показывает статусную информацию.	Методы: showMessage(), addWidget().
QToolBar	Панель с кнопками быстрого доступа. Может быть перемещена или плавать поверх окна.