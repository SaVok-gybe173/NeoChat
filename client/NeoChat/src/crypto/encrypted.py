"""
End-to-End Encryption: X25519 ephemeral-static ECDH + HKDF-SHA256 + AES-256-GCM.
Каждое сообщение — уникальный ephemeral ключ (Forward Secrecy).
"""

import base64
import os
from typing import Tuple

from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey, X25519PublicKey
)
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class KeyManager:
    """Управление статической ключевой парой X25519 клиента."""

    def __init__(self):
        self._private_key: X25519PrivateKey = X25519PrivateKey.generate()
        self._public_key: X25519PublicKey = self._private_key.public_key()

    @property
    def public_key_b64(self) -> str:
        """Base64-публичный ключ для upload_key на сервер."""
        raw = self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return base64.b64encode(raw).decode("ascii")

    @property
    def private_key(self) -> X25519PrivateKey:
        """Приватный ключ для расшифровки входящих сообщений."""
        return self._private_key


class PublicKeyCache:
    """Кэш публичных ключей собеседников: username -> X25519PublicKey."""

    def __init__(self):
        self._cache: dict[str, X25519PublicKey] = {}

    def add(self, username: str, b64_key: str | None) -> None:
        """
        Добавить ключ в кэш. b64_key должен быть валидным base64 X25519 ключом.
        Перед вызовом убедитесь, что ответ сервера содержит status == "ok".
        """
        if not b64_key:
            raise ValueError(f"Empty public key for {username}")
        try:
            raw = base64.b64decode(b64_key)
            if len(raw) != 32:
                raise ValueError(f"Invalid X25519 key length: {len(raw)}")
            self._cache[username] = X25519PublicKey.from_public_bytes(raw)
        except Exception as e:
            raise ValueError(f"Invalid public key for {username}: {e}")

    def get(self, username: str) -> X25519PublicKey:
        if username not in self._cache:
            raise KeyError(f"No public key cached for {username}")
        return self._cache[username]


class E2EECipher:
    """Шифрование/расшифровка отдельных сообщений."""

    @staticmethod
    def encrypt(plaintext: str, peer_public_key: X25519PublicKey) -> Tuple[str, str, str, str]:
        """
        Генерирует ephemeral X25519, ECDH ephemeral->static, HKDF с salt, AES-256-GCM.
        Возвращает (ciphertext_b64, ephemeral_pub_b64, nonce_b64, salt_b64).
        """
        ephemeral_priv = X25519PrivateKey.generate()
        ephemeral_pub = ephemeral_priv.public_key()

        shared = ephemeral_priv.exchange(peer_public_key)
        salt = os.urandom(16)

        key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=b"messenger-e2ee-v1"
        ).derive(shared)

        nonce = os.urandom(12)
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)

        ephemeral_pub_b64 = base64.b64encode(
            ephemeral_pub.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
        ).decode("ascii")

        return (
            base64.b64encode(ciphertext).decode("ascii"),
            ephemeral_pub_b64,
            base64.b64encode(nonce).decode("ascii"),
            base64.b64encode(salt).decode("ascii")
        )

    @staticmethod
    def decrypt(
        ciphertext_b64: str,
        nonce_b64: str,
        ephemeral_pub_b64: str,
        salt_b64: str,
        static_private_key: X25519PrivateKey
    ) -> str:
        """Получатель: ECDH static_priv × ephemeral_pub, HKDF, AES-GCM decrypt."""
        ephemeral_pub = X25519PublicKey.from_public_bytes(
            base64.b64decode(ephemeral_pub_b64)
        )

        shared = static_private_key.exchange(ephemeral_pub)
        salt = base64.b64decode(salt_b64)
        key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=b"messenger-e2ee-v1"
        ).derive(shared)

        ciphertext = base64.b64decode(ciphertext_b64)
        nonce = base64.b64decode(nonce_b64)
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode("utf-8")


# --------------------------------------------------------------------------- #
# Утилиты для интеграции с ClientSocket
# --------------------------------------------------------------------------- #

def prepare_e2ee_message(
    plaintext: str,
    key_cache: PublicKeyCache,
    recipient_username: str
) -> dict:
    """
    Зашифровать сообщение для конкретного получателя.
    Возвращает payload для send_request("send_message", ...).
    """
    try:
        peer_key = key_cache.get(recipient_username)
    except KeyError as e:
        raise KeyError(f"Cannot encrypt: {e}")

    ciphertext_b64, ephemeral_pub_b64, nonce_b64, salt_b64 = E2EECipher.encrypt(
        plaintext, peer_key
    )
    return {
        "content": ciphertext_b64,
        "encrypted": True,
        "ephemeral_key": ephemeral_pub_b64,
        "nonce": nonce_b64,
        "salt": salt_b64
    }


def decrypt_incoming_message(msg: dict, key_manager: KeyManager) -> str:
    """
    Расшифровать входящее push-сообщение.
    msg должен содержать: content, ephemeral_key, nonce, salt.
    """
    return E2EECipher.decrypt(
        msg["content"],
        msg["nonce"],
        msg["ephemeral_key"],
        msg["salt"],
        key_manager.private_key
    )
