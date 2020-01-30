import sys
import os
import time
import json
import threading
import cv2
import win32api
import win32gui
import win32con
import numpy as np
from PIL import ImageGrab
from wmi import WMI
from weapons import weapons

win32api.SetConsoleTitle("RCS - @sr-henry")

window_name = "Counter-Strike: Global Offensive"
hwnd = win32gui.FindWindow(0, window_name)
screen_template_areas = []
white_lower = np.array([243,243,243])
white_upper = np.array([255,255,255])

def pil_2_cv(pil_img):
    cv_img = np.array(pil_img)
    cv_img = cv_img[:,:,::-1].copy()
    return cv_img

def is_selected(screen, rate = 130):
    dom = np.where(screen == (255, 255, 255))
    if dom[0].size < rate:
        return False
    return True

def remove_glow(template):
    mask = cv2.inRange(template, white_lower, white_upper)
    ng_template = cv2.bitwise_and(template, template, mask = mask)
    return ng_template

def get_screen_template_areas():
    bbox = win32gui.GetWindowRect(hwnd)
    pil_img = ImageGrab.grab(bbox= bbox).convert("RGB")
    croped_imgs = list(map(pil_img.crop, screen_template_areas))
    return list(map(pil_2_cv, croped_imgs)) 

def detection(screen, template_weapon, threshold = 0.7):
    if screen is None or template_weapon is None:
        return False
    if not is_selected(screen):
        return False
    screen = remove_glow(screen)
    result = cv2.matchTemplate(screen, template_weapon, cv2.TM_CCOEFF_NORMED)
    if result[0][0] >= threshold:
        return True
    return False

def matcher(weapon):
    template_weapon = weapon["img"]
    scrs = get_screen_template_areas()
    ret = list(filter(lambda el: detection(el, template_weapon), scrs))
    if ret:
        return True
    return False

class WeaponThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.current_weapon = None
        self.on = True
    
    def run(self):
        while self.on:
            if win32gui.GetWindowText(win32gui.GetForegroundWindow()) == window_name:
                if matcher(weapons[0]):
                    self.current_weapon = weapons[0]
                elif matcher(weapons[1]):
                    self.current_weapon = weapons[1]
                elif matcher(weapons[2]):
                    self.current_weapon = weapons[2]
                elif matcher(weapons[3]):
                    self.current_weapon = weapons[3]
                elif matcher(weapons[4]):
                    self.current_weapon = weapons[4]
                elif matcher(weapons[5]):
                    self.current_weapon = weapons[5]
                elif matcher(weapons[6]):
                    self.current_weapon = weapons[6]
                elif matcher(weapons[7]):
                    self.current_weapon = weapons[7]
                elif matcher(weapons[8]):
                    self.current_weapon = weapons[8]
                else:
                    self.current_weapon = None
            else:
                self.current_weapon = None
            time.sleep(.2)

    def terminate(self):
        self.on = False

def set_screen_template_areas():
    default_area = np.array([948, 635, 983, 645])
    equipment    = np.array([0, -57, 0, -57])
    bomb         = np.array([0, -62, 0, -62])
    defuse       = np.array([0, -30, 0, -30])
    for i in range(3):
        screen_template_areas.append((default_area + equipment*i))
        screen_template_areas.append((default_area + equipment*i + bomb))
        screen_template_areas.append((default_area + equipment*i + defuse))

def load_weapon_templates():
    print("[!] Loading templates")
    path = os.getcwd() + "/1024x768/"
    for i, weapon in enumerate(weapons):
        weapon["img"] = cv2.imread(path + weapon["img_name"])
        if weapon["img"] is None:
            print(" -  ERROR", end="")
        else:
            print(" -  OK", end="")
        print("\t%s"%(weapon["name"]))

def load_config():
    print("\n[!] Loading config", end=": ")
    try:
        with open("config.json") as f:
            cfg = json.load(f)
            for weapon in weapons:
                weapon["x"] = abs(cfg[weapon["name"]]["x"])
                weapon["y"] = abs(cfg[weapon["name"]]["y"])
    except:
        print("ERROR")
        return False
    print("OK")
    return True

def perform_control(weapon):
    magazine = weapon["magazine"]
    pattern = weapon["pattern"]
    delay = (60 / weapon["rpm"]) - 3/1000
    x = weapon["x"]
    y = weapon["y"]
    shot_index = 0
    while win32api.GetAsyncKeyState(win32con.VK_LBUTTON) and shot_index != magazine:
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(pattern[shot_index][0] * x), int(pattern[shot_index][1] * y), 0, 0)
        time.sleep(delay)
        shot_index += 1

def get_hd_serial():
    c = WMI()
    item = c.Win32_PhysicalMedia()
    if type(item) == list:
        return str(item[0].SerialNumber).strip()
    else:
        return str(item.SerialNumber).strip()

def auth_ID():
    if get_hd_serial() == "WD-WCC2EFS39589":
        return True
    return False

def run():
    if not auth_ID():
        print("[!] User ID error")
        input("Press some key to exit...")
        return

    print("[:] User successfully authenticated\n")

    if not hwnd:
        print("[-] Error to find process\n")
        input("Press some key to exit...")
        return
    
    print("[+] Process found\n")
    set_screen_template_areas()
    load_weapon_templates()

    if not load_config():
        input("Press some key to exit...")
        return

    print("\n[!] Starting Weapon Detector\n")
    weapon_detector = WeaponThread()
    weapon_detector.setDaemon(True)
    weapon_detector.start()

    print("[?] F9 - exit\n")
    while True:
        if win32api.GetAsyncKeyState(win32con.VK_F9):
            weapon_detector.terminate()
            break
        if not weapon_detector.current_weapon is None:
            perform_control(weapon_detector.current_weapon)

if __name__ == "__main__":
    run()