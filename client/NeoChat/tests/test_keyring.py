import sys
sys.path.append("./src")
sys.path.append(".")

from NeoChat.src.crypto.keyring import *

print(get_password('akk2'))
set_password("akk", "kkr")
set_password("akk2", "kkr3")
print(get_password('akk'))
delete_password('akk')
print(get_password('akk'))