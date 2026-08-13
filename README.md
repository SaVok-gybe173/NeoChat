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
|   |   ├── Logger.hpp        (логирование)
|   |   ├── Logger.cpp
|   |   ├── RateLimiter.hpp   (защита от брутфорса)
|   |   ├── RateLimiter.cpp
|   |   └── Json.hpp          (полноценная реализация парсера для JSON-файлов и для полноценного хранения данных)
│   └── config/
|       ├── Config.cpp        (реализация функций)
|       └── Config.hpp        (класс с функцией загрузки данных)    
├── CMakeLists.txt
└── config.ini

client/
├── .venv/                          (python 3.13.7)
├── NeoChat/                        
|   |   src/
|   |   ├── assets/                 (иконки для сборки)
|   |   |   ├── icon.png
|   |   |   └── splash_android.png
|   |   ├── core/                   (ядро)
|   |   |   └── __info__.py
|   |   ├── crypto/                 (шифрование)
|   |   |   ├── __init__.py
|   |   |   └── encrypted.py
|   |   ├── network/                (вся сетевая инфроструктура)
|   |   |   ├── __init__.py
|   |   |   ├── api.py
|   |   |   └── client_socket.py
|   |   ├── storage/                (структера всего локального хранилища)
|   |   |   ├── message/
|   |   |   |   ├── bd.py
|   |   |   |   └── structure.py
|   |   |   └── server.py
|   |   ├── ui/                     (графический интерфейс)
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
|   ├── pyproject.toml              (конфигурация сдля сборки)
|   └── README.md
├── requirements.txt                (библеотеки)
├── neochat-logo.ico
├── neochat-logo.jpg
└── neochat-logo.png
```


# Протокол мессенджера

Формат: JSON-запрос → JSON-ответ. Успех: `"status":"ok"`. Ошибка: `"status":"error"` + `"reason"` (код ошибки) + `"message"` (человекочитаемое описание).

---

## 1. Регистрация

**Запрос**
```json
{"action":"register","username":"alice","password":"secret","email":"example@mail.com"}
```

**Ответ (успех — письмо с кодом отправлено)**
```json
{"status":"ok","message":"confirmation_sent"}
```

**Ответ (ошибка — email уже занят)**
```json
{"status":"error","reason":"email_taken","message":"Account with this email already exists"}
```

**Ответ (ошибка — username уже занят)**
```json
{"status":"error","reason":"username_taken","message":"Username already exists"}
```

---

## 2. Запрос кода подтверждения почты

**Запрос**
```json
{"action":"confirmation_request","email":"example@mail.com"}
```

**Ответ (успех)**
```json
{"status":"ok","message":"confirmation_sent"}
```

**Ответ (ошибка — аккаунт не найден)**
```json
{"status":"error","reason":"account_not_found","message":"No account with this email"}
```

---

## 3. Подтверждение почты кодом

**Запрос**
```json
{"action":"confirmation_code","email":"example@mail.com","code":"123456"}
```

**Ответ (успех)**
```json
{"status":"ok","message":"email_confirmed"}
```

**Ответ (ошибка — неверный код)**
```json
{"status":"error","reason":"invalid_code","message":"Confirmation code is incorrect"}
```

**Ответ (ошибка — код истёк)**
```json
{"status":"error","reason":"code_expired","message":"Confirmation code has expired"}
```

---

## 4. Вход

Клиент сам собирает и отправляет метаданные своего устройства вместе с логином/паролем. Сервер сверяет их с тем, что сохранено для этого аккаунта.

**Запрос**
```json
{
  "action":"login",
  "username":"alice",
  "password":"secret",
  "device": {
    "app_version": "0.0.1",
    "os":"Linux",
    "os_release":"5.15.0",
    "os_version":"#1 SMP ...",
    "machine":"x86_64",
    "processor":"x86_64",
    "hostname":"alice-pc",
    "cpu_count":8,
    "device_id":"9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
    "mac":"00:1a:2b:3c:4d:5e"
  }
}
```

**Ответ (успех — метаданные совпали с сохранёнными)**
```json
{"status":"ok","token":"a1b2c3...","email":"example@mail.com"}
```

**Ответ (метаданные не совпали — сервер запросил подтверждение почты)**
```json
{"status":"error","reason":"device_not_verified","message":"New device detected, email confirmation required"}
```
→ сервер сам инициирует отправку кода на почту (либо клиент затем вызывает `confirmation_request`), после чего клиент вызывает `confirmation_code`. После успешного подтверждения сервер сохраняет присланные метаданные как доверенные для этого аккаунта.

**Ответ (ошибка — неверный логин/пароль)**
```json
{"status":"error","reason":"invalid_credentials","message":"Invalid username or password"}
```

---

## 5. Отправка сообщения

**Запрос**
```json
{"action":"send_message","token":"...","to":"bob","content":"hi"}
```

**Ответ (успех)**
```json
{"status":"ok","message":"message_sent"}
```

**Ответ (ошибка — токен невалиден/истёк)**
```json
{"status":"error","reason":"invalid_token","message":"Session expired, please log in again"}
```

**Ответ (ошибка — получатель не найден)**
```json
{"status":"error","reason":"user_not_found","message":"Recipient does not exist"}
```

---

## 6. История сообщений

**Запрос**
```json
{"action":"get_messages","token":"...","peer":"bob"}
```

**Ответ (успех)**
```json
{"status":"ok","messages":[
  {"from":"alice","to":"bob","content":"hi","timestamp":"2026-08-13T10:00:00Z"}
]}
```

**Ответ (ошибка)**
```json
{"status":"error","reason":"invalid_token","message":"Session expired, please log in again"}
```

---

## 7. Список пользователей

**Запрос**
```json
{"action":"get_users","token":"..."}
```

**Ответ (успех)**
```json
{"status":"ok","users":["alice","bob"]}
```

**Ответ (ошибка)**
```json
{"status":"error","reason":"invalid_token","message":"Session expired, please log in again"}
```

---

## 8. Выход

**Запрос**
```json
{"action":"logout","token":"..."}
```

**Ответ (успех)**
```json
{"status":"ok","message":"logged_out"}
```

**Ответ (ошибка)**
```json
{"status":"error","reason":"invalid_token","message":"Token not found or already invalidated"}
```
