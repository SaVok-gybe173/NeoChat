from .server import Server, SERVERS
from config import HOME
import os
import json

if not os.path.isdir(os.path.join(HOME, "storage")):
    os.mkdir(os.path.join(HOME, "storage"))

def getListStorege():
    for st in os.listdir(os.path.join(HOME, "storage")):
        os.path.join(HOME, "storage", st)        

def addStoregeServer(server: Server):
    path = os.path.join(HOME, "storage", f"{server.ip}-{server.port}")
    if not os.path.isdir(path):
        os.mkdir(path)
        with open(os.path.join(path, "config.json"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"ip": server.ip, "port": server.port,
                                "name": server.name, "region": server.region,
                                "mode": server.mode, "ping": server.ping,
                                "status": server.status, 
                                "favorite": server.favorite, "locked": server.locked}, indent=2))
    else:
        raise 