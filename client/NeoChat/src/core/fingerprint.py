from .__info__ import __version__
import platform
import uuid
import hashlib
import json
import requests
import os
import socket

def get_device_fingerprint():
    """
    Собирает информацию об устройстве и возвращает словарь с данными.
    """
    info = {
        "app_version": __version__,
        'os': platform.system(),
        'os_release': platform.release(),
        'os_version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'hostname': socket.gethostname(),
        'cpu_count': os.cpu_count(),
        # MAC-адрес (может быть нестабильным)
        'mac': ':'.join(['%02x' % ((uuid.getnode() >> i) & 0xff) for i in range(40, -1, -8)]),
    }
    # Добавим уникальный идентификатор, который можно сохранять локально
    # Создаём хеш из объединения данных (для стабильности лучше сохранять отдельный UUID)
    combined = ''.join(str(v) for v in info.values())
    device_id = hashlib.sha256(combined.encode()).hexdigest()
    info['device_id'] = device_id
    return info

def send_device_info(server_url, device_info=None):
    """
    Отправляет информацию об устройстве на сервер по указанному URL.
    """
    if device_info is None:
        device_info = get_device_fingerprint()
    try:
        response = requests.post(server_url, json=device_info, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки данных: {e}")
        return None

# Пример использования:
if __name__ == "__main__":
    data = get_device_fingerprint()
    print(json.dumps(data, indent=2))
    # send_device_info('https://your-server.com/api/device', data)