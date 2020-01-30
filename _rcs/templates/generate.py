import cv2
import numpy as np
from os import getcwd
from PIL import Image

res = "1280x1024"

weapons = ["ak", "m4", "sg", "galil", "aug", "famas", "m4a1", "ump", "mp9", "mp5"]


area = (1175,767, 1221, 785)


path =  getcwd()

normal_path = path + "/normal/" + res + "/"

white_lower = np.array([243,243,243])
white_upper = np.array([255,255,255])

def remove_glow(template):
    mask = cv2.inRange(template, white_lower, white_upper)
    ng_template = cv2.bitwise_and(template, template, mask = mask)
    return ng_template

def pil2cv(pil_img):
    cv_img = np.array(pil_img)
    cv_img = cv_img[:,:,::-1].copy()
    return cv_img

for w in weapons:
    im_normal = Image.open(normal_path + w + ".jpg")

    im_normal = im_normal.crop(area)

    cv_im_normal = pil2cv(im_normal)

    template = remove_glow(cv_im_normal)

    cv2.imwrite(path + "/t_" + w + ".png", template)

    print(w,"\t","DONE")


    


