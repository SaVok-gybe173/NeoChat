def set_password(account: str, password: str) -> None:
    """
    Сохраняет пароль для аккаунта с использованием мастер-пароля.
    """
def get_password(account: str) -> str | None:
    """
    Возвращает пароль или None, если не найден.
    """
def delete_password(account: str) -> None | bool:
    """
    Удаляет запись. Возвращает True при успехе.
    """
    
__all__ = ['set_password', 'get_password', 'delete_password', 'is_available']