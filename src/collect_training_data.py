import os
import cv2 as cv # type: ignore


def capture_new_images(HAAR_CASCADE, frame, image_name: str, train_dir: str, val_dir: str, count: int, image_count_requirement: int):
    try:
        os.makedirs(f'{train_dir}/{image_name.lower()}')
    except FileExistsError as e:
        print('Error:', e)
    try:
        os.makedirs(f'{val_dir}/{image_name.lower()}')
    except FileExistsError as e:
        print('Error:', e)
    
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    faces_rect = HAAR_CASCADE.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=3)
    if len(faces_rect) == 1:
        for x, y, w, h in faces_rect:
            cv.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), thickness=1)
            gray_faces_roi = gray_frame[y:y+h, x:x+w]
            colored_faces_roi = frame[y:y+h, x:x+w]
            gray_faces_roi = cv.resize(gray_faces_roi, (100, 100))
            colored_faces_roi = cv.resize(colored_faces_roi, (100, 100))
            cv.imwrite(f'{train_dir}/{image_name.lower()}/{count}.jpg', gray_faces_roi)
            cv.imwrite(f'{val_dir}/{image_name.lower()}/{count}.jpg', colored_faces_roi)
            print(f'[TRAINING] captured image {train_dir}/{image_name.lower()}/{count}.jpg')
            print(f'[VALIDATION] captured image {val_dir}/{image_name.lower()}/{count}.jpg')
    return count + 1 >= image_count_requirement


