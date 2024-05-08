import os
import socketio # type: ignore
import cv2 as cv # type: ignore
from picamera2 import Picamera2 # type: ignore

# Set pins for trigger and echo
TRIG_PIN = 23
ECHO_PIN = 24

TRAINING_DIR = os.path.join('captured_faces', 'train')
VALIDATION_DIR = os.path.join('captured_faces', 'val')

REMOTE_SERVER_HOST = 'http://192.168.1.2:8500'
HTTP_REST_ENDPOINTS = {
    'authorized_users_v1': f'{REMOTE_SERVER_HOST}/api/v1/authorized_users',
    'day_records_v1': f'{REMOTE_SERVER_HOST}/api/v1/day_records',
    'detections_v1': f'{REMOTE_SERVER_HOST}/api/v1/detections',
    'authorized_users_v2': f'{REMOTE_SERVER_HOST}/api/v2/authorized_users',
    'day_records_v2': f'{REMOTE_SERVER_HOST}/api/v2/day_records',
    'detections_v2': f'{REMOTE_SERVER_HOST}/api/v2/detections',
}

SIO = socketio.Client()

HAAR_CASCADE = cv.CascadeClassifier('./haarcascades/haarcascade_frontalface_default.xml')

VIDEO_WRITER = None

PICAM2 = Picamera2()