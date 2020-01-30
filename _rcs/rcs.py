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
from weapons import weapons

def pil_2_cv(pil_img):
    cv_img = np.array(pil_img)
    cv_img = cv_img[:,:,::-1].copy()
    return cv_img

class RCS(object):
    def __init__(self):
        self.window_name = "Counter-Strike: Global Offensive"
        self.hwnd = win32gui.FindWindow(0, self.window_name)
        self.screen_template_areas = []
        self.white_lower = np.array([243,243,243])
        self.white_upper = np.array([255,255,255])
        self.current_weapon = None
        self.on = True
    
    def is_selected(self, screen, rate = 130):
        dom = np.where(screen == (255, 255, 255))
        if dom[0].size < rate:
            return False
        return True

    def remove_glow(self, template):
        mask = cv2.inRange(template, self.white_lower, self.white_upper)
        ng_template = cv2.bitwise_and(template, template, mask = mask)
        return ng_template

    def get_screen_template_areas(self):
        bbox = win32gui.GetWindowRect(self.hwnd)
        pil_img = ImageGrab.grab(bbox= bbox).convert("RGB")
        croped_imgs = list(map(pil_img.crop, self.screen_template_areas))
        return list(map(pil_2_cv, croped_imgs)) 

    def detection(self, screen, template_weapon, threshold = 0.7):
        if screen is None or template_weapon is None:
            return False
        if not self.is_selected(screen):
            return False
        screen = self.remove_glow(screen)
        result = cv2.matchTemplate(screen, template_weapon, cv2.TM_CCOEFF_NORMED)
        if result[0][0] >= threshold:
            return True
        return False

    def matcher(self, weapon):
        template_weapon = weapon["img"]
        scrs = self.get_screen_template_areas()
        ret = list(filter(lambda el: self.detection(el, template_weapon), scrs))
        if ret:
            return True
        return False

    def _weapon_detector(self):
        while self.on:
            if win32gui.GetWindowText(win32gui.GetForegroundWindow()) == self.window_name:
                if self.matcher(weapons[0]):
                    self.current_weapon = weapons[0]
                elif self.matcher(weapons[1]):
                    self.current_weapon = weapons[1]
                elif self.matcher(weapons[2]):
                    self.current_weapon = weapons[2]
                elif self.matcher(weapons[3]):
                    self.current_weapon = weapons[3]
                elif self.matcher(weapons[4]):
                    self.current_weapon = weapons[4]
                elif self.matcher(weapons[5]):
                    self.current_weapon = weapons[5]
                elif self.matcher(weapons[6]):
                    self.current_weapon = weapons[6]
                elif self.matcher(weapons[7]):
                    self.current_weapon = weapons[7]
                elif self.matcher(weapons[8]):
                    self.current_weapon = weapons[8]
                else:
                    self.current_weapon = None
            else:
                self.current_weapon = None
            time.sleep(.2)

    def set_screen_template_areas(self):
        default_area = np.array([948, 635, 983, 645])
        equipment    = np.array([0, -57, 0, -57])
        bomb         = np.array([0, -62, 0, -62])
        defuse       = np.array([0, -30, 0, -30])
        for i in range(3):
            self.screen_template_areas.append((default_area + equipment*i))
            self.screen_template_areas.append((default_area + equipment*i + bomb))
            self.screen_template_areas.append((default_area + equipment*i + defuse))
    
    def load_weapon_templates(self):
        print("[!] Loading templates")
        path = os.getcwd() + "/1024x768/"
        for weapon in weapons:
            weapon["img"] = cv2.imread(path + weapon["img_name"])
            if weapon["img"] is None:
                print(" -  ERROR", end="")
            else:
                print(" -  OK", end="")
            print("\t%s"%(weapon["name"]))

    def load_config(self):
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

    def perform_control(self, weapon):
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

    def func_to_be_threaded(self):
        threading.Thread(target=self._weapon_detector, daemon=True).start()

    def run(self):
        if not self.hwnd:
            print("[-] Error to find process\n")
            input("Press some key to exit...")
            return
        
        print("[+] Process found\n")
        self.set_screen_template_areas()
        self.load_weapon_templates()

        if not self.load_config():
            input("Press some key to exit...")
            return

        print("\n[!] Starting Weapon Detector\n")
        self.func_to_be_threaded()

        print("F9 - exit\n")
        while True:
            if win32api.GetAsyncKeyState(win32con.VK_F9):
                self.on = False
                break
            if not self.current_weapon is None:
                self.perform_control(self.current_weapon)


        











