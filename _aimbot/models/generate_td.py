import cv2
import numpy as np
import os
import random
import joblib

DATADIR = "C:/Users/henri/Desktop/models/"

categories = ["ct", "tr"]

im_size = 100

training_data = []

for i, cat in enumerate(categories):
    path = os.path.join(DATADIR, cat)
    for img in os.listdir(path):
        try:
            img_array = cv2.imread(os.path.join(path, img))
            img_array = cv2.resize(img_array, (im_size, im_size))
            training_data.append([img_array, i])
        except Exception as err:
            print(err)

random.shuffle(training_data)

joblib.dump(training_data, "training_data")
