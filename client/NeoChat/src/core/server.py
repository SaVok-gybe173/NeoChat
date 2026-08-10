from dataclasses import dataclass
from crypto.api import getActive, getName, getRegion, getMode, ping, EXCEPTIONS
import os, json
from config import HOME

@dataclass
class Server:
    ip: str
    port: int
    name: str # имя
    region: str # регеон
    mode: str # тип сервера
    ping: int = 20 # пинг
    status: str = "online"  # активность: online / offline / maintenance
    favorite: bool = False # избранное
    locked: bool = False # блокеровка

SERVERS: list[Server] = [
    Server("195.208.119.133", 8080, "Main Neo Chat RU #1", "RU", "Main", 40, locked=True, favorite=True),
    Server("127.0.0.1", 8080, "localhost", "null", "Main", 10, locked=True, favorite=True),
]

if not os.path.isdir(os.path.join(HOME, "storage")):
    os.mkdir(os.path.join(HOME, "storage"))

def getListStorege() -> list[str]:
    return [os.path.join(HOME, "storage", i) for i in os.listdir(os.path.join(HOME, "storage"))]

def addServer(ip: str, port: str):
    port = int(port)
    if not port > 0 and port <= 65535:
        raise ValueError("port слишком маленький или большой")
    status = "online" if getActive(ip, port) else "offline"
    ping = 0
    try:
        sed = ping(ser.ip)
        if isinstance(sed, float):
            ping = int(ping(ser.ip)*1_000)
        else:
            status = "offline"
    except Exception:
        status = "offline"

    ser = Server(ip, port , getName(ip, port ), getRegion(ip), getMode(ip, port), status=status, ping=ping)
    configStoregeServer(ser)
    SERVERS.append(ser)

def updateServer():
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

def loadServer():
    for ser in getListStorege():
        try:
            with open(os.path.join(ser, "config.json"), "r", encoding="utf-8") as f:
                data = Server(**json.loads(f.read()))
        except Exception:
            continue
        for i in SERVERS:
            if i.ip == data.ip and i.port == data.port:
                break
        else:
            SERVERS.append(data)

def configStoregeServer(server: "Server"):
    path = os.path.join(HOME, "storage", f"{server.ip}-{server.port}")
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


loadServer()