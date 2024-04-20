with_gui = 0
try:
    with_gui = int(input('Enter mode\n(0) without GUI, (1) with GUI: '))
except Exception as e:
    print(e)
    quit()

import os
import socketio # type: ignore
import requests # type: ignore
import base64
import cv2 as cv # type: ignore
import RPi.GPIO as GPIO # type: ignore
from picamera2 import Picamera2 # type: ignore


import sensors
import collect_training_data
import train_model
import recognize_face


# Set pins for trigger and echo
TRIG_PIN = 16
ECHO_PIN = 18

PICAM2 = Picamera2()
SIO = socketio.Client()
HAAR_CASCADE = cv.CascadeClassifier('./haarcascades/haarcascade_frontalface_default.xml')
FACE_RECOGNIZER = cv.face.LBPHFaceRecognizer.create()

FACE_RECOGNIZER.read('model_trained.yml')

TRAINING_DIR = os.path.join('captured_faces', 'train')
VALIDATION_DIR = os.path.join('captured_faces', 'val')

REMOTE_SERVER_HOST = 'http://192.168.1.2:8500'
API_PATH_ADD_NEW_AUTHORIZED_USER = '/api/v1/authorized_users'
API_PATH_ADD_NEW_DETECTION = '/api/v1/detections'

# Set GPIO mode
GPIO.setmode(GPIO.BOARD)

# Setup GPIO pins
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# Setup Camera configurations
PICAM2.preview_configuration.main.size = (1280, 720)
PICAM2.preview_configuration.main.format = 'RGB888'
PICAM2.preview_configuration.align()
PICAM2.configure('preview')
PICAM2.start()


# Global variables
is_socket_connected = False
add_new_authorized_user = False
new_authorized_user_data = None


people = ['momo', 'meme', 'mimi', 'mumu', 'mama']
#for p in os.listdir(TRAINING_DIR):
#    people.append(p)
print('Recognized People: ', people)
print('Press D to Exit...')



# socket.io event listeners
@SIO.event
def from_server_to_add_new_authorized_user(data):
    global add_new_authorized_user
    global new_authorized_user_data
    add_new_authorized_user = True
    new_authorized_user_data = data
    print('message: ', data)
    



try:
    currently_captured_image_count = 0
    while True:
        # Keep looping until connected to socket.io remote server
        while not is_socket_connected:
            try:
                SIO.connect(REMOTE_SERVER_HOST)
                print('Socket ID:', SIO.sid)
                is_socket_connected = True
            except Exception as e:
                print(e)
                continue
        
        # Capture image from Raspberry Pi Camera
        frame = PICAM2.capture_array()

        face_detection_state = 'OFF'
        distance = sensors.get_distance(TRIG_PIN, ECHO_PIN)
        if distance is not None: # Just for printing the distance
            print("Distance: {:.2f} cm".format(distance))
        if distance is not None and distance <= 150: # Filter distances below 150cm
            face_detection_state = 'ON'
            recognize_face.identify_face(HAAR_CASCADE, FACE_RECOGNIZER, frame, people)
            if add_new_authorized_user:
                add_new_authorized_user = False
                if new_authorized_user_data != None:
                    is_finished_capturing_images = collect_training_data.capture_new_images(HAAR_CASCADE, frame, new_authorized_user_data['name'], TRAINING_DIR, VALIDATION_DIR, currently_captured_image_count, 20)
                    currently_captured_image_count += 1
                    if is_finished_capturing_images:
                        currently_captured_image_count = 0
                        with open(f'{VALIDATION_DIR}/{new_authorized_user_data["name"]}/0.jpg', 'rb') as f:
                            profile_image_data = base64.b64encode(f.read()).decode('utf-8')
                            requests.post(f'{REMOTE_SERVER_HOST}{API_PATH_ADD_NEW_AUTHORIZED_USER}', data={ 'profileImage': profile_image_data, 'name': new_authorized_user_data['name'] })
                        train_model.train_face_recognizer(TRAINING_DIR, VALIDATION_DIR, people)
                        print(f'New Authorized User [{new_authorized_user_data["name"]}] is registered.')
                else:
                    print('no user data...')
        cv.putText(frame, f'Face Detection State: {face_detection_state}', (30, 40), cv.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)

        if with_gui == 1:
            cv.imshow('Frame', frame)
            if cv.waitKey(20) == ord('d'):
                break

except KeyboardInterrupt:
    GPIO.cleanup()
    if with_gui == 1:
        cv.destroyAllWindows()
    

GPIO.cleanup()
if with_gui == 1:
    cv.destroyAllWindows()

