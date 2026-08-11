```
server/
├── src/
│   ├── main.cpp
│   ├── network/              (TCP-сервер, сессии)
|   |   ├── Session.hpp       (класс для создания сессии)
|   |   └── platform.hpp      (реализация кроссплатформенности для Windows и Linux)
│   ├── routing/              (маршрутизация)
|   |   ├── Router.hpp
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
├── main.py
├── network/
├── crypto/                   (CryptoAlgorithm, фабрика, реализации)
├── key_manager/
├── ui/                       (Tkinter/Qt/консоль)
├── storage/                  (локальное хранилище)
└── config.ini
```
