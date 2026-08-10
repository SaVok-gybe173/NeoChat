from dataclasses import dataclass
from crypto.api import getActive, getName, getRegion, getMode, ping

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

SERVERS = [
    Server("0.0.0.0", 122, "Main Neo Chat RU #1", "RU", "Main", 20, favorite=True),
]

def addServer(ip: str, port: str):
    port = int(port)
    if not port > 0 and port <= 65535:
        raise
    ser = Server(ip, port , getName(ip, port ), getRegion(ip), getMode(ip, port), ping=int(ping(ip)*1_000), locked=getActive())
    