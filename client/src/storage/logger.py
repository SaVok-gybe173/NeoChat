from datetime import datetime
from io import TextIOWrapper
from config import DEBUGGING, LOG_PATH
from typing import List

import os

ERROR = '[ERROR]'                   # ошибка
ERROR_LOGGER = "[ERROR LOGGER]"     # ошибка связана с работой логовой системой
INFO = "[INFO]"                     # лог инфо
INFO_LOGGER = "[INFO LOGGER]"       # лог инфо связан с работой логовой системой


_is_open_file: bool = False         # открыт ли фаил
_open_file: TextIOWrapper           # открытый текстовый фаил .log или другой с праметром 'a'
_file_log: str                      # путь к файлу
_log_list_not_file: List[str] = []  # все логи который не удалось записать в фаил

# устанавливает фаил лог
def setFileLog(file: str) -> bool:
    global _file_log
    global _is_open_file
    global _open_file

    updateLog()

    if _is_open_file:
        _open_file.close()
        _is_open_file = False
        
    if os.path.isfile(file):
        _file_log = file
        try:
            _open_file = open(file, 'a', encoding="utf-8")
            _is_open_file = True
        except Exception as e:
            printLog('logger.py > setFileLog:', e, types = ERROR_LOGGER)
    else:
        _file_log = None
        return False

    updateLog()
    return True

# принимает название файла и создает его, или создает свой фаил
def createFileLog(name: str | None = None) -> bool:
    if name is None:
        file = os.path.join(LOG_PATH, datetime.now().strftime("%Y-%m-%d %H-%M.log"))
        
    else:
        file = os.path.join(LOG_PATH, name)
    if not os.path.isfile(file):
        try:
            open(file, 'w', encoding="utf-8").close()
        except Exception as e:
            printLog('logger.py > createFileLog:', e, types = ERROR_LOGGER)
    return setFileLog(file)

def _print(data: str) -> None:
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

# отправляет в фаил лог
def printLog(*values, types: str | None = INFO, sep: str | None = " ",
            # заглушка
            end: None = None,
            file: None = None,
            flush: None = None) -> None:

    updateLog()

    global _is_open_file
    global _open_file
    global _log_list_not_file

    if sep is None: sep = ' '
    if types is None: types = INFO

    values = [i if isinstance(i, str) else str(i) for i in values]
    data = f"{types} [{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}] {sep.join(values)}".replace('\n', "<\\n>") + '\n'

    if DEBUGGING:
        print(data, end='')

    _print(data)
    


def updateLog() -> None:
    global _is_open_file
    global _log_list_not_file
    global _open_file

    if not _is_open_file:       return
    if not _log_list_not_file:  return

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

# возвращает bool значение открыт ли фаил или же нет
def isOpenLogFile() -> bool:
    global _is_open_file
    return _is_open_file

# возвращает список логов
def getLogList() -> list[str]:
    global _is_open_file
    global _open_file
    global _log_list_not_file

    if _is_open_file:
        return []
    else:
        return _log_list_not_file


createFileLog()
