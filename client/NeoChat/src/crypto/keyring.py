#
# Хранение не было протестино так как не было возможности
# Для каждого устройства своя библеотека для хранения ключей
#
# Если библеотека будет не найдена или устройство не определено 
# то будет использована стандартное решение
#

from core.platform import is_android, is_ios, is_linux, is_macos, is_window
from .logger import printLog, ERROR
from .server import serverGet, STORAGE, serverInfoGet
from config import NAME, HOME
import os
import json
import hashlib
import base64

# Мастер-пароль можно запросить у пользователя или задать жёстко (но тогда это бессмысленно)
# В примере мы его запрашиваем при первом вызове — но это неудобно.
# Для простоты будем использовать фиксированный "секретный" ключ, но это НЕБЕЗОПАСНО.
# Лучше запрашивать у пользователя, но тогда нужен ввод.

MASTER_PASSWORD = "my_master_password_123"   # ЗАМЕНИТЕ НА СВОЙ!
KEYRING_FILE = os.path.join(HOME, "keyring.json")
if not os.path.isfile(KEYRING_FILE):
    with open(KEYRING_FILE, 'w', encoding="utf-8") as f:
        f.write('{\n}')
# Криптопримитивы (самодельные)

def _derive_key(password: str, salt: bytes = b"") -> bytes:
    """Вырабатывает 32-байтовый ключ из пароля с помощью SHA-256."""
    key = password.encode('utf-8')                  # Используем PBKDF2-подобный подход с многократным хешированием
    for _ in range(10000):                          # итерации для замедления
        key = hashlib.sha256(key + salt).digest()
    return key[:32]                                 # 256 бит

def _xor_encrypt(data: bytes, key: bytes) -> bytes:
    """Шифрует/дешифрует данные с помощью XOR (симметрично)."""
    # Повторяем ключ до длины данных
    key_repeated = (key * (len(data) // len(key) + 1))[:len(data)]
    return bytes(a ^ b for a, b in zip(data, key_repeated))

def _encrypt_text(text: str, master_password: str) -> str:
    """Шифрует текст и возвращает строку base64."""
    salt = os.urandom(16)
    key = _derive_key(master_password, salt)
    data = text.encode('utf-8')
    encrypted = _xor_encrypt(data, key)
    # Сохраняем соль вместе с зашифрованными данными
    combined = salt + encrypted
    return base64.b64encode(combined).decode('ascii')

def _decrypt_text(encrypted_b64: str, master_password: str) -> str:
    """Расшифровывает текст из base64."""
    combined = base64.b64decode(encrypted_b64.encode('ascii'))
    salt = combined[:16]
    encrypted = combined[16:]
    key = _derive_key(master_password, salt)
    decrypted = _xor_encrypt(encrypted, key)
    return decrypted.decode('utf-8')

# Работа с хранилищем
def _load_storage() -> dict:
    """Загружает JSON-файл с зашифрованными данными."""
    
    try:
        with open(KEYRING_FILE, 'r') as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, IOError):
        return {}

def _save_storage(data: dict) -> None:
    """Сохраняет словарь в JSON-файл."""
    with open(KEYRING_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# Публичное API
def set_password(account: str, password: str, master_password: str = MASTER_PASSWORD) -> None:
    """Сохраняет пароль для аккаунта с использованием мастер-пароля."""
    data = _load_storage()
    # Шифруем пароль
    encrypted = _encrypt_text(password, master_password)
    data[account] = encrypted
    _save_storage(data)

def get_password(account: str, master_password: str = MASTER_PASSWORD) -> str | None:
    """Возвращает пароль или None, если не найден."""
    data = _load_storage()
    encrypted = data.get(account)
    if encrypted is None:
        return None
    try:
        return _decrypt_text(encrypted, master_password)
    except Exception:
        return None  # неверный мастер-пароль или повреждённые данные

def delete_password(account: str) -> bool:
    """Удаляет запись. Возвращает True при успехе."""
    data = _load_storage()
    if account in data:
        del data[account]
        _save_storage(data)
        return True
    return False

if is_ios():
    try:
        import keychain as _keychain_py
        def set_password(account: str, password: str) -> None:
            _keychain_py.set_password(NAME, account, password)
        def get_password(account: str) -> str:
            return _keychain_py.get_password(NAME, account)
        def delete_password(account: str) -> None:
            _keychain_py.delete_password(NAME, account)
    except ImportError:
        try:
            from juno import keychain as _keychain_juno
            def set_password(account, password):
                _keychain_juno.set_password(NAME, account, password)
            def get_password(account):
                try:
                    return _keychain_juno.get_password(NAME, account)
                except Exception as e:
                    printLog(e, types=ERROR)
            def delete_password(account):
                _keychain_juno.delete_password(NAME, account)
        except Exception as e:
            printLog("Ошибка в user.py (не удалось импортировать juno) >", e, types=ERROR)
    except Exception as e:
        printLog("Ошибка в user.py (не удалось импортировать keychain) >", e, types=ERROR)

elif is_macos() or is_linux():
    
    try:
        # macOS / Linux (через keyring)
        import keyring as _keyring
        def set_password(account, password):
            _keyring.set_password(NAME, account, password)
        def get_password(account):
            try:
                return _keyring.get_password(NAME, account)
            except Exception as e:
                printLog(e, types=ERROR)
        def delete_password(account):
            _keyring.delete_password(NAME, account)
    except ImportError as e:
        printLog("Не удалось импортировать модуль keyring >", e, types=ERROR)
elif is_window():
    try:
        import win32crypt
        def set_password(account: str, password: str) -> None:
            server = serverInfoGet()
            path = os.path.join(STORAGE, f"{server.ip}-{server.port}")
            encrypted = win32crypt.CryptProtectData(
                password.encode('utf-16-le'), None, None, None, None, 0
            )
            # Храним в файле с именем service_account.dat
            with open(os.path.join(path, f"{NAME}_{account}.dat"), "wb") as f:
                f.write(encrypted)
        def get_password(account: str) -> str:
            try:
                server = serverInfoGet()
                path = os.path.join(STORAGE, f"{server.ip}-{server.port}")
                with open(os.path.join(path, f"{NAME}_{account}.dat"), "rb") as f:
                    encrypted = f.read()
                decrypted = win32crypt.CryptUnprotectData(
                    encrypted, None, None, None, None, 0
                )
                return decrypted.decode('utf-16-le')
            except FileNotFoundError as e:
                printLog(e, types=ERROR)
                return None
        def delete_password(account: str) -> None:
            try:
                server = serverInfoGet()
                os.remove(os.path.join(STORAGE, f"{server.ip}-{server.port}"))    
            except FileNotFoundError as e:
                printLog(e, types=ERROR)
            
    except Exception as e:
        printLog("Не удалось импортировать модуль win32crypt >", e, types=ERROR)
else:
    printLog("Использование стандартное хранение ключей")

__all__ = ['set_password', 'get_password', 'delete_password']