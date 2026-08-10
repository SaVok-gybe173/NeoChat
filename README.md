```
server/
├── src/
│   ├── main.cpp
│   ├── network/          (TCP-сервер, сессии)
│   ├── routing/          (маршрутизация)
│   ├── database/         (своя датабаза)
│   ├── crypto/           (интерфейс ICrypto, реализации для хешей)
│   └── config/           (парсер настроек)
├── CMakeLists.txt
└── config.ini

client/
├── main.py
├── network/
├── crypto/               (CryptoAlgorithm, фабрика, реализации)
├── key_manager/
├── ui/                   (Tkinter/Qt/консоль)
├── storage/              (локальное хранилище)
└── config.ini
```
