```
server/
├── src/
│   ├── main.cpp
|   ├── platform.hpp          (реализация кроссплатформенности для Windows и Linux)
│   ├── network/              (TCP-сервер, сессии)
|   |   ├── Server.cpp        (реализация функций из Server.hpp)
|   |   ├── Server.hpp        (класс сервера)
|   |   ├── Session.cpp       (реализация функций из Session.hpp)
|   |   └── Session.hpp       (класс для создания сессии)
│   ├── routing/              (маршрутизация)
|   |   ├── Router.hpp
|   |   ├── Router.cpp
|   |   ├── Handlers.hpp
|   |   └── Handlers.cpp
│   ├── database/             (своя БД)
|   |   ├── IDatabase.hpp     (класс кастомной БД)
|   |   ├── JsonDatabase.hpp  (класс БД для хранения в JSON-формате из файла Json.hpp)
|   |   └── JsonDatabase.cpp  (реализация функция хранения и загрузки в БД)
│   ├── crypto/               (интерфейс ICrypto, реализации для хешей, хеширование)
|   |   ├── ICrypto.hpp
|   |   ├── Sha256Hasher.hpp
|   |   └── Sha256Hasher.cpp
|   ├── utils/                (вспомогательные методы, функции, классы)
|   |   └── Json.hpp          (полноценная реализация парсера для JSON-файлов и для полноценного хранения данных)
│   └── config/
|       ├── Config.cpp        (реализация функций)
|       └── Config.hpp        (класс с функцией загрузки данных)    
├── CMakeLists.txt
└── config.ini

client/
├── NeoChat/
|   |   src/
|   |   ├── assets/
|   |   |   ├── icon.png
|   |   |   └── splash_android.png
|   |   ├── core/
|   |   |   └── __info__.py
|   |   ├── crypto/
|   |   |   └── encrypted.py
|   |   ├── network/
|   |   |   ├── api.py
|   |   |   └── socet.py
|   |   ├── storege/
|   |   |   ├── message/
|   |   |   |   ├── bd.py
|   |   |   |   └── structure.py
|   |   |   └── server.py
|   |   ├── ui/
|   |   |   ├── add_server.py
|   |   |   ├── entrance.py
|   |   |   ├── registration.py
|   |   |   └── server.py
|   |   ├── config.ini
|   |   ├── config.py
|   |   ├── language.py
|   |   └── main.py
|   ├── tests/
|   |   └── test_main.py
|   ├── .gitignore
|   ├── pyproject.toml
|   └── README.md
├── neochat-logo.ico
├── neochat-logo.jpg
└── neochat-logo.png
```
