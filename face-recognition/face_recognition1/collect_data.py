import os
import time
# import numpy as np
import cv2 as cv


haar_cascade = cv.CascadeClassifier('./haarcascades/haarcascade_frontalface_default.xml')

TRAINING_DIR = os.path.join('CapturedFaces', 'train')
VALIDATION_DIR = os.path.join('CapturedFaces', 'val')

def capture_new_images(image_name: str, training_image_count=50, validation_image_count=30):
    capture = cv.VideoCapture(0)
    try:
        os.makedirs(f'{TRAINING_DIR}/{image_name.lower()}')
    except FileExistsError as e:
        print(e)
    try:
        os.makedirs(f'{VALIDATION_DIR}/{image_name.lower()}')
    except FileExistsError as e:
        print(e)
    

    
    count = 0
    while count < training_image_count:
        _, frame = capture.read()
        gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces_rect = haar_cascade.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)
        if len(faces_rect) == 1:
            for x, y, w, h in faces_rect:
                faces_region_of_interest = gray_frame[y:y+h, x:x+w]
                cv.imwrite(f'{TRAINING_DIR}/{image_name.lower()}/{count}.jpg', faces_region_of_interest)
                print(f'[TRAINING] Captured image {count}...')
            time.sleep(0.02)
            count += 1

    count = 0
    while count < validation_image_count:
        _, frame = capture.read()
        gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        faces_rect = haar_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=9)
        if len(faces_rect) == 1:
            for x, y, w, h in faces_rect:
                faces_region_of_interest = frame[y:y+h, x:x+w]
                cv.imwrite(f'{VALIDATION_DIR}/{image_name.lower()}/{count}.jpg', faces_region_of_interest)
            print(f'[VALIDATION] Captured image {count}...')
            time.sleep(0.02)
            count += 1




if __name__ == '__main__':
    name = input('Enter name: ')
    capture_new_images(name, training_image_count=100)