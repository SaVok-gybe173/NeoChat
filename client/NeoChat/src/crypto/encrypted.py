# взято с PyForge
import hashlib
import secrets
import base64
from itertools import cycle

# шифр по паролю
def derive_key(password: str, salt: bytes, key_length: int = 32) -> bytes:
    """Получить ключ из пароля через PBKDF2-HMAC-SHA256."""
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, dklen=key_length)

def encrypt(plaintext: str, password: str) -> str:
    """Шифрование XOR с солью и возврат закодированной строки base64."""
    salt = secrets.token_bytes(16) # Генерируем случайную соль (16 байт)
    return base64.b64encode(salt + bytes([b ^ k for b, k in zip(plaintext.encode('utf-8'), cycle(derive_key(password, salt)))])).decode('ascii')

def decrypt(encrypted_b64: str, password: str) -> str:
    """Расшифрование XOR-зашифрованной строки."""
    raw = base64.b64decode(encrypted_b64)
    return bytes([b ^ k for b, k in zip(raw[16:], cycle(derive_key(password, raw[:16])))]).decode('utf-8')


# Для демонстрации используем небольшое простое число и генератор.
# В реальности нужно брать 2048-битные числа из RFC 3526.
P = 9973      # простое число
G = 2         # первообразный корень по модулю P

def generate_dh_private_key() -> int:
    """Сгенерировать секретный ключ (число от 2 до P-2)."""
    return secrets.randbelow(P - 3) + 2  # 2 .. P-2

def compute_dh_public_key(private_key: int) -> int:
    """Вычислить открытый ключ: G^private_key mod P."""
    return pow(G, private_key, P)

def compute_shared_secret(private_key: int, other_public_key: int) -> int:
    """Вычислить общий секрет: other_public_key^private_key mod P."""
    return pow(other_public_key, private_key, P)

def derive_key_from_shared(shared_secret: int, salt: bytes = None) -> bytes:
    """
    Преобразовать общий секрет (int) в ключ фиксированной длины (32 байта)
    с помощью PBKDF2-HMAC-SHA256. Если соль не передана, генерируется новая.
    Возвращает (key, salt) — соль нужна для расшифровки.
    """
    if salt is None:
        salt = secrets.token_bytes(16)
    return hashlib.pbkdf2_hmac('sha256', shared_secret.to_bytes((shared_secret.bit_length() + 7) // 8, 'big'), salt, 100000, dklen=32), salt


def encrypt_with_shared(plaintext: str, shared_secret: int) -> str:
    """
    Шифрует текст с использованием общего секрета DH.
    Возвращает base64-строку: salt + зашифрованные данные.
    """
    key, salt = derive_key_from_shared(shared_secret)
    encrypted = bytes([b ^ k for b, k in zip(plaintext.encode('utf-8'), cycle(key))])
    return base64.b64encode(salt + encrypted).decode('ascii')

def decrypt_with_shared(encrypted_b64: str, shared_secret: int) -> str:
    """
    Расшифровывает данные, зашифрованные функцией encrypt_with_shared.
    """
    raw = base64.b64decode(encrypted_b64)
    salt = raw[:16]
    encrypted_data = raw[16:]
    key, _ = derive_key_from_shared(shared_secret, salt)  # передаём ту же соль
    decrypted = bytes([b ^ k for b, k in zip(encrypted_data, cycle(key))])
    return decrypted.decode('utf-8')


if __name__ == "__main__":
    salt = secrets.token_bytes(16)
    password = "мой_секретный_пароль"
    print(derive_key(password, salt))
    original = "Привет, мир! Это тестовое сообщение."
    
    encrypted = encrypt(original, password)
    print("Зашифровано (base64):", encrypted)
    
    decrypted = decrypt(encrypted, password)
    print("Расшифровано:", decrypted)

    print("-"*10)

    #Клиент А
    priv_a = generate_dh_private_key()
    pub_a = compute_dh_public_key(priv_a)
    print(f"Клиент А: приватный ключ = {priv_a}, публичный = {pub_a}")

    #Клиент Б
    priv_b = generate_dh_private_key()
    pub_b = compute_dh_public_key(priv_b)
    print(f"Клиент Б: приватный ключ = {priv_b}, публичный = {pub_b}")

    # Обмен открытыми ключами (по сети)
    # А вычисляет общий секрет на основе публичного ключа Б
    shared_a = compute_shared_secret(priv_a, pub_b)
    # Б вычисляет общий секрет на основе публичного ключа А
    shared_b = compute_shared_secret(priv_b, pub_a)

    # Секреты должны совпасть
    assert shared_a == shared_b, "Общий секрет не совпал!"
    print(f"Общий секрет (совпадает): {shared_a}")

    # А шифрует сообщение для Б
    msg = "Секретное сообщение для клиента Б!"
    ciphertext = encrypt_with_shared(msg, shared_a)
    print(f"Зашифрованное сообщение (base64): {ciphertext}")

    # Б расшифровывает
    decrypted_msg = decrypt_with_shared(ciphertext, shared_b)
    print(f"Расшифрованное сообщение: {decrypted_msg}")