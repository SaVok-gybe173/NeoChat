import requests
from ping3 import ping

def getName(ip: str, port: int) -> str:
    return f"{ip}:{port}"

def getActive(ip: str, port: int):
    return True

def getRegion(ip: str) -> str:
    response = requests.get(f'https://ipinfo.io/{ip}/json')
    data: dict = response.json()
    return data.get("country", 'null')

def getMode(ip: str, port: int) -> str:
    return "Chat"
