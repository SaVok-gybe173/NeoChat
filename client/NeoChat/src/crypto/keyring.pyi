def set_password(account: str, password: str) -> None:
    """
    устанавливает ключ
    """
def get_password(account: str) -> str | None:
    """
    возвращает ключ
    """
def delete_password(account: str) -> None:
    """
    удаляет ключ
    """
__all__ = ['set_password', 'get_password', 'delete_password', 'is_available']