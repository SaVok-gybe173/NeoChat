from dataclasses import dataclass

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

def addServer(ip, port):
    Server(ip, port, ip, )
