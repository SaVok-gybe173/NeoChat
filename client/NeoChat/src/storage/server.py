from dataclasses import dataclass
from network.api import getActive, getName, getRegion, getMode, ping, EXCEPTIONS
from network.client_socket import ClientSocket
from config import HOME, setScene

import os
import json


@dataclass
class Server:
    ip: str                 # ip сервера
    port: int               # порт сервера
    name: str               # имя
    region: str             # регеон
    mode: str               # тип сервера
    ping: int = 20          # пинг
    status: str = "online"  # активность: online / offline / maintenance
    favorite: bool = False  # избранное
    locked: bool = False    # блокеровка

    def conect(self):
        soc = ClientSocket()
        is_ = soc.connect(self.ip, self.port)
        if is_:
            serverSet(soc)
        return is_
        
        
        
# список сервров
SERVERS: list[Server] = [
    Server("195.208.119.133", 8080, "Test Neo Chat RU #1", "RU", "Main", 92, locked=True, favorite=True),
    Server("127.0.0.1", 8080, "localhost", "null", "Main", 10, locked=True, favorite=True),
]

if not os.path.isdir(os.path.join(HOME, "storage")):    # проверка а наличии папки storage
    os.mkdir(os.path.join(HOME, "storage"))             # созадние папки storage

def getListStorege() -> list[str]: # возвращает список из путей в storage
    return [os.path.join(HOME, "storage", i) for i in os.listdir(os.path.join(HOME, "storage"))]

def addServer(ip: str, port: str) -> None:  # добавляет сервер
    port = int(port)
    if not port > 0 and port <= 65535:      # проверка на существующии порты
        raise ValueError("port слишком маленький или большой")
    status = "online" if getActive(ip, port) else "offline"
    ping = 0                    
    try:
        sed = ping(ser.ip)
        if isinstance(sed, float):
            ping = int(ping(ser.ip)*1_000)  # проверка пинга
        else:
            status = "offline"
    except Exception:
        status = "offline"

    ser = Server(ip, port , getName(ip, port ), getRegion(ip), getMode(ip, port), status=status, ping=ping)
    configStoregeServer(ser)
    SERVERS.append(ser)

def updateServer(isSave: bool = True) -> None:     # обновление пинга и мета данных
    for ser in SERVERS:
        #ser.name = getName(ser.ip, ser.port )
        ser.region = getRegion(ser.ip)
        ser.mode = getMode(ser.ip, ser.port)
        try:
            sed = ping(ser.ip)
            if isinstance(sed, float):
                ser.ping = int(ping(ser.ip)*1_000)
            else:
                ser.status = "offline"
        except Exception:
            ser.status = "offline"
        if isSave:
            configStoregeServer(ser)

def loadServer() -> None:       # загружает список серверов из getListStorege() -> list[str]
    for ser in getListStorege():
        try:
            with open(os.path.join(ser, "config.json"), "r", encoding="utf-8") as f:
                data = Server(**json.loads(f.read()))
        except Exception:
            continue
        for i in SERVERS:
            if i.ip == data.ip and i.port == data.port:
                break # не добовляем если сервер уже есть
        else:
            SERVERS.append(data)

def configStoregeServer(server: "Server") -> None: # сохраняет конфигурацию сервера
    path = os.path.join(HOME, "storage", f"{server.ip}-{server.port}") # структура 127.0.0.1-8080 
    if not os.path.isdir(path):
        os.mkdir(path)

    with open(os.path.join(path, "config.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps({"ip": server.ip,
                            "port": server.port,
                            "name": server.name, 
                            "region": server.region,
                            "mode": server.mode, 
                            "ping": server.ping,
                            "status": server.status, 
                            "favorite": server.favorite, 
                            "locked": server.locked}, 
                                indent=2))

# работа с активным сокетом

def serverIsActiv() -> bool:
    global _ClientSocket
    return _ClientSocket._closed

def serverGet() -> ClientSocket:
    global _ClientSocket
    return _ClientSocket

def serverSet(client_socket: ClientSocket):
    global _ClientSocket
    try:
        setScene("EntranceServer")
    except NameError: ...
    _ClientSocket = client_socket

def serverClose() -> None:
    global _ClientSocket
    _ClientSocket.close()

# происходит сейчас ли подключение
def isConectGet() -> bool:
    global _is_conect
    return _is_conect

def isConectSet(is_conect: bool) -> None:
    global _is_conect
    _is_conect = is_conect

isConectSet(False)
serverSet(ClientSocket())
loadServer() # загружает конфигурацию при страте