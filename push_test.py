from machineCode2 import machine2
import time
item=machine2()
item.startUpdateLoop()
item.setPosition3(30)
time.sleep(5)
item.push(50,0.5)
