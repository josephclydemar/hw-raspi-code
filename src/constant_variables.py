import os

# Set pins for ultrasonic sensor
TRIG_PIN = 23
ECHO_PIN = 24

# Set pins for buzzer, button, and led
LED_PIN = 20
BUTTON_PIN = 12
BUZZER_PIN = 19


SERVO_PIN = 13
PWM_FREQ = 50 # (Hz)

# Set PWM duty cycle range
# PWM_duty_min = 2.5
# PWM_duty_max = 12.5

FRAME_SHAPE = (1280, 720)

TRAINING_DIR = os.path.join('captured_faces', 'train')
VALIDATION_DIR = os.path.join('captured_faces', 'val')

REMOTE_SERVER_HOST = 'http://192.168.69.171:8500'
REST_ENDPOINTS = {
    'authorized_users_v1': f'{REMOTE_SERVER_HOST}/api/v1/authorized_users',
    'authorized_users_entries_v1': f'{REMOTE_SERVER_HOST}/api/v1/authorized_users_entries',
    'day_records_v1': f'{REMOTE_SERVER_HOST}/api/v1/day_records',
    'detections_v1': f'{REMOTE_SERVER_HOST}/api/v1/detections',
    'authorized_users_v2': f'{REMOTE_SERVER_HOST}/api/v2/authorized_users',
    'day_records_v2': f'{REMOTE_SERVER_HOST}/api/v2/day_records',
    'detections_v2': f'{REMOTE_SERVER_HOST}/api/v2/detections',
}

FPS = 10