"""
Модуль логирования для отсчета об ошибках
"""

from datetime import datetime
from io import TextIOWrapper
from config import DEBUGGING, LOG_PATH
from typing import List

import os

[
    [],
    []
]

# КОНСТАНТЫ

ERROR           = "[ERROR]"             # тип ошибки
ERROR_LOGGER    = "[ERROR LOGGER]"      # ошибка связана с работой логовой системой (ошибки вызваны во время работы логера)
INFO            = "[INFO]"              # тип информации 
INFO_LOGGER     = "[INFO LOGGER]"       # лог инфо связан с работой логовой системой (информация в пработе логера)
REQUESTS_INFO   = "[REQUESTS INFO]"     # ошибка запросов на сервер и ответ


# глобальные переменные

_is_open_file: bool = False             # открыт ли фаил
_open_file: TextIOWrapper               # открытый текстовый фаил .log или другой с праметром 'a'
_file_log: str                          # путь к файлу
_log_list_not_file: List[str] = []      # все логи который не удалось записать в фаил


def setFileLog(file: str) -> bool:
    """
    Устанавливает фаил лог и делает запись в него.
    
    Обновляет все логи и делает проверку на действительнось файла.
    Если есть логи которые не записались в прошлый фаил, то они будут записаны в новый лог фаил.
    
    Args:
        file (str): Путь (относительный или полный путь) к файлу с расширением и названием файла
        
            Пример - /logs/log.txt
    
    Return:
        Возвращает bool значение, определяющие успешно ли открылся фаил. 
    
    """
    global _file_log
    global _is_open_file
    global _open_file

    updateLog() # сохраняет не сохраненые логи в старый фаил

    # зарытие старго файла есть он открыт
    if _is_open_file:
        _open_file.close()
        _is_open_file = False

    # проверка на существование файла, если он существут то открывает его и возвращает True
    if os.path.isfile(file):
        _file_log = file
        try:
            _open_file = open(file, 'a', encoding="utf-8")
            _is_open_file = True
        except Exception as e:
            printLog('logger.py > setFileLog:', e, types = ERROR_LOGGER) # лог об ошибки
    else:   # если файла не существет возвращает False
        _file_log = None
        return False

    updateLog() # записывает не сохраненые логи в новый фаил его его получилось открыть
    return True

def createFileLog(name: str | None = None) -> bool:
    """
    
    Принимает название файла и создает его, или создает свой фаил
    
    Args:
        name (str | None): Название файла (Например logs.log)
    Return:
        Возвращает bool значение, определяющие успешно ли открылся фаил. 

    """
    if name is None:
        # создает фаил есть в аргументах None
        file = os.path.join(LOG_PATH, datetime.now().strftime("%Y-%m-%d %H-%M.log"))
        
    else:
        file = os.path.join(LOG_PATH, name)
    if not os.path.isfile(file):
        try:
            open(file, 'w', encoding="utf-8").close()   # создает фаил
        except Exception as e:
            printLog('logger.py > createFileLog:', e, types = ERROR_LOGGER)
    return setFileLog(file)

def _print(data: str) -> None:
    """
    Запись в фаил и вывод в консоль при включеном DEBUGGING

    Args:
        data (data): текск котрый нужно добавить в логи
    """
    global _is_open_file
    global _open_file
    global _log_list_not_file

    if _is_open_file:
        try:
            _open_file.write(data)
        except Exception as e:
            if DEBUGGING:
                print(f"{ERROR_LOGGER} [{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}] {e} > не удалось записать лог в фаил.".replace('\n', "<\\n>"))
            _log_list_not_file.append(data)
            _open_file.close()
            _is_open_file = False
    else:
        _log_list_not_file.append(data)

# самое обычное логирование
def printLog(*values: object, types: str | None = None, sep: str | None = " ",
            # заглушка
            end: None = None,
            file: None = None,
            flush: None = None) -> None:
    """
    Обновляет список логов и переделывает все в формат логов.
    При включеным DEBUGGING выводит все логи в консоль.
    
    Args:
        *values (object): Обьекты которые отправляються в консоль.
        types (str): тип ошибки (пример: '[INFO]').

            константы: 
                ERROR = \"[ERROR]\"
                INFO = \"[INFO]\"
                REQUESTS_INFO = \"[REQUESTS INFO]\"
        sep (str): Разделитель текста (работает как в print)
    """
    updateLog()

    global _is_open_file
    global _open_file
    global _log_list_not_file

    # стандартные значение
    if sep is None: sep = ' '
    if types is None: types = INFO

    # преобразование
    values = [i if isinstance(i, str) else str(i) for i in values]
    data = f"{types} [{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}] {sep.join(values)}".replace('\n', "<\\n>") + '\n'

    # дебагер
    if DEBUGGING:
        print(data, end='')

    _print(data)    # запись в лог

def printInfo(*values, sep: str | None = " ",
            # заглушка
            end: None = None,
            file: None = None,
            flush: None = None):
    """
    Запись логов с типо [INFO]

    Args:
        *values (object): Обьекты которые отправляються в консоль.
        sep (str): Разделитель текста (работает как в print)
    """
    return printLog(*values, types=INFO, sep=sep)

def printError(*values, sep: str | None = " ",
            # заглушка
            end: None = None,
            file: None = None,
            flush: None = None):
    """
    Запись логов с типо [ERROR]

    Args:
        *values (object): Обьекты которые отправляються в консоль.
        sep (str): Разделитель текста (работает как в print)
    """
    return printLog(*values, types=ERROR, sep=sep)


def updateLog() -> None:
    """
    Обновление списка логов:

        Переберает список не записаных логов.
        Записывает несохраненые логи если они не были сохранены.
        Обновляет состояние работы записи в случае ошибки.
    """
    global _is_open_file
    global _log_list_not_file
    global _open_file

    # выход из фунции
    if not _is_open_file:       return
    if not _log_list_not_file:  return

    # перебор
    i = 0
    while i < len(_log_list_not_file):
        try:
            _open_file.write(_log_list_not_file[i])
            i += 1
        except Exception:
            # Ошибка записи. оставляем в списке только то, что не удалось
            _log_list_not_file = _log_list_not_file[i:]
            _is_open_file = False
            return
    _log_list_not_file.clear()


def isOpenLogFile() -> bool:
    """
    Состояние файла

    Return:
        Возвращает bool значение открыт ли фаил или же нет.
    """
    global _is_open_file
    return _is_open_file


def getLogList() -> list[str]:
    """
    Возвращает список логов
    """
    global _is_open_file
    global _open_file
    global _log_list_not_file

    if _is_open_file:
        return []
    else:
        return _log_list_not_file

# стандарт - создает фаил
createFileLog()
