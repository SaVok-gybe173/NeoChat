import sys
sys.path.append("./src")
sys.path.append(".")
from src.storage.logger import *

printLog("test1")

print(setFileLog("testerror.log"))

printLog("test2")
printLog("test22")


print(getLogList())

createFileLog("testerror.log")

printLog("test3")

print(getLogList())