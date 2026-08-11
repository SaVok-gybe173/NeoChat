from dataclasses import dataclass, field

def load(path):
    global _path_bd
    _path_bd = path

def _get_path():
    global _path_bd
    return _path_bd

