import win32api
from win32con import VK_INSERT, VK_LBUTTON
from time import sleep

current_x, current_y = 0, 0
old_x, old_y = 0, 0
dx, dy = 0, 0

tracking = False

log_name = input("file name: ")

with open(log_name, "w") as f:
    f.write("[")
    while True:
        if win32api.GetAsyncKeyState(VK_INSERT):
            if tracking:
                tracking = False
                print("[-] Stop tranking")
                f.write("]")
                win32api.Beep(1700,300)
                break
            else:
                tracking = True
                print("[-] Start tranking")
                win32api.Beep(2000,100)
            sleep(.05)
            
        if win32api.GetAsyncKeyState(VK_LBUTTON) and tracking:
            win32api.Beep(1500, 200)
            current_x, current_y = win32api.GetCursorPos()
            if old_x == 0 and old_y == 0:
                old_x = current_x
                old_y = current_y
                dx = 0
                dy = 0

            else:
                dx = (current_x - old_x) + 1
                dy = (current_y - old_y) + 1
                old_x = current_x
                old_y = current_y
            
            f.write("(%d,%d),"%(dx*-1, dy*-1))
        
        sleep(.1)