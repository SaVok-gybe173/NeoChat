from datetime import datetime
from io import TextIOWrapper
from config import DEBUGGING, LOG_PATH
from typing import List

import os

ERROR = '[ERROR]'
ERROR_LOGGER = "[ERROR LOGGER]"
INFO = "[INFO]"
INFO_LOGGER = "[INFO LOGGER]"


_is_open_file: bool = False
_open_file: TextIOWrapper
_file_log: str
_log_file: List[str] = []

# устанавливает фаил лог
def setFileLog(file: str) -> None:
    global _file_log
    global _is_open_file
    global _open_file

    if _is_open_file:
        _open_file.close()
        _is_open_file = False
        
    if os.path.isfile(file):
        _file_log = file
        try:
            _open_file = open(file, 'a', encoding="utf-8")
            _is_open_file = False
        except Exception as e:
            printLog('logger.py > setFileLog:', e, types = "[ERROR LOGGER]")
    else:
        _file_log = None
        raise ValueError("нет файла")

# принимает название файла и создает его, или создает свой фаил
def createFileLog(name: str | None = None) -> None:
    if name is None:
        file = os.path.join(LOG_PATH, datetime.now().strftime("%Y-%m-%d_%H-%M.log"))
    else:
        file = os.path.join(LOG_PATH, name)
        if not os.path.isfile(file):
            try:
                open(file, 'w', encoding="utf-8").close()
            except Exception as e:
                printLog('logger.py > createFileLog:', e, types = "[ERROR LOGGER]")
    setFileLog(file)

# отправляет в фаил лог
def printLog(*values, types: str | None = INFO, sep: str | None = " ",
            # заглушка
            end: None = None,
            file: None = None,
            flush: None = None) -> None:

    global _file_log
    global _is_open_file
    global _open_file

    if sep is None: sep = ' '
    if types is None: types = INFO

    values = [i if isinstance(i, str) else str(i) for i in values]
    data = f"{types} [{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}] {sep.join(values)}".replace('\n', "<\\n>") + '\n'

    if DEBUGGING:
        print(data)

try:
    createFileLog()
except ValueError:
    pass
