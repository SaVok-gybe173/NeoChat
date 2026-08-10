```
server/
├── src/
│   ├── main.cpp
│   ├── network/              (TCP-сервер, сессии)
|   |   ├── Session.hpp       (класс для создания сессии)
|   |   └── platform.hpp      (реализация кроссплатформенности для Wingows и Linux)
│   ├── routing/              (маршрутизация)
│   ├── database/             (своя БД)
|   |   ├── IDatabase.hpp     (класс кастомной БД)
|   |   ├── JsonDatabase.hpp  (класс БД для хранения в JSON-формате из файла Json.hpp)
|   |   └── JsonDatabase.cpp  (реализация функция хранения и загрузки в БД)
│   ├── crypto/               (интерфейс ICrypto, реализации для хешей)
|   ├── utils/                (вспомогательные методы, функции, классы)
|   |   └── Json.hpp          (полноценная реализация парсера для JSON-файлов и для полноценного хранения данных)
│   └── config/
|       ├── Config.cpp        (реализация функций)
|       └── Config.hpp        (класс с функцией загрузки данных)    
├── CMakeLists.txt
└── config.ini

client/
├── main.py
├── network/
├── crypto/                   (CryptoAlgorithm, фабрика, реализации)
├── key_manager/
├── ui/                       (Tkinter/Qt/консоль)
├── storage/                  (локальное хранилище)
└── config.ini
```
