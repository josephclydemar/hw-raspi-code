# with_gui = 0
# try:
#     with_gui = int(input('Enter mode\n(0) without GUI, (1) with GUI: '))
# except Exception as e:
#     print(e)
#     quit()



import os
import time
import threading
import base64
import cv2 # type: ignore
import socketio # type: ignore
import requests # type: ignore
from requests_toolbelt import MultipartEncoder # type: ignore
from flask import Flask, render_template, Response # type: ignore
import RPi.GPIO as GPIO # type: ignore
from picamera2 import Picamera2 # type: ignore
import numpy as np # type: ignore
from keras_facenet import FaceNet # type: ignore
import pickle

from constant_variables import REMOTE_SERVER_HOST, REST_ENDPOINTS, TRIG_PIN, ECHO_PIN, LED_PIN, BUTTON_PIN, BUZZER_PIN, SERVO_PIN, PWM_FREQ, FRAME_SHAPE, FPS


sio = socketio.Client()
is_socket_connected = False
is_gpio_initialized = False

picam_initialized = False
picam = None

is_recording = False
video_writer = None
frame_count = 0

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
face_net = FaceNet()
app = Flask(__name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates')))

authorized_users = {}
start_recording_time = 0

operating_mode = 'auto'

is_door_open = False

# Set GPIO mode
# if not is_gpio_initialized:
GPIO.setmode(GPIO.BCM)

# Setup GPIO pins for Ultrasonic sensor
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

GPIO.setup(SERVO_PIN, GPIO.OUT)
PWM = GPIO.PWM(SERVO_PIN, PWM_FREQ)

# PWM.start(0)
# is_gpio_initialized = True

from utils import rescale_frame
from actuators import open_door, close_door, turnon_light, turnoff_light, sound_buzzer
from sensors import get_distance





with open(os.path.join('trained_models', 'data3.pkl'), 'rb') as file:
    database = pickle.load(file)
    response_obj = requests.get(REST_ENDPOINTS['authorized_users_v1'])
    json_users_data = response_obj.json()
    for user in json_users_data:
        authorized_users[user['_id']] = {
            '_id': user['_id'],
            'name': user['name'],
            'recognized_count': 0,
        }






def allow_authorized_user_entry(user_id, image_frame, pwm):
    global is_door_open
    open_door(pwm)
    time.sleep(2)
    close_door(PWM)
    send_authorized_user_entry(user_id, image_frame)
    is_door_open = False



def send_authorized_user_entry(authorized_user_id, image_frame):
    global REST_ENDPOINTS
    rescaled_frame = rescale_frame(image_frame, scale=0.4)
    ret, jpeg = cv2.imencode('.jpg', rescaled_frame)
    byte_frame = jpeg.tobytes()
    b64_encoded_image = base64.b64encode(byte_frame).decode('utf-8')
    response = requests.post(REST_ENDPOINTS['authorized_users_entries_v1'], data={
        'authorizedUserId': authorized_user_id,
        'capturedImage': b64_encoded_image,
    })
    print(response.json())




while not is_socket_connected:
    try:
        sio.connect(REMOTE_SERVER_HOST)
        print('socketio id:', sio.sid)
        is_socket_connected = True

        @sio.event
        def from_server_control_door(data):
            global PWM, BUZZER_PIN
            # print('Open Door', data)
            # sound_buzzer(BUZZER_PIN)
            if data == 'open_door':
                open_door(PWM)
            if data == 'close_door':
                close_door(PWM)
        
        @sio.event
        def from_server_set_operating_mode(data):
            global operating_mode
            print(data)
            operating_mode = data
        
        @sio.event
        def from_server_control_light(data):
            global LED_PIN
            if data == 'turnon_light':
                turnon_light(LED_PIN)
            if data == 'turnoff_light':
                turnoff_light(LED_PIN)

    except Exception as e:
        print(e)





def initialize_picamera():
    global picam_initialized, picam
    picam = Picamera2()
    picam.preview_configuration.main.size = FRAME_SHAPE
    picam.preview_configuration.main.format = 'RGB888'
    picam.preview_configuration.align()
    picam.configure('preview')
    picam.start()

    # config = picam.create_preview_configuration({'size': (808, 606)})
    # picam.align_configuration(config)
    # picam.configure(config)
    # picam.start()
    picam_initialized = True

# Generator function to generate frames for streaming
def generate():
    global picam_initialized, picam, video_writer, FRAME_SHAPE, FPS, frame_count, is_recording, start_recording_time, is_door_open, operating_mode, PWM
    if not picam_initialized:
        initialize_picamera()
    while True:
        frame = picam.capture_array()
        # frame = rescale_frame(frame, scale=0.5)

        distance = get_distance(TRIG_PIN, ECHO_PIN)
        cv2.putText(frame, f'Distance: {round(distance, 3)} cm', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 0), 2)
        if distance < 200:
            if not is_recording:
                print('Started recording video...')
                video_writer = cv2.VideoWriter(os.path.join('videos', 'new', 'new_video.avi'), cv2.VideoWriter_fourcc(*'XVID'), FPS, FRAME_SHAPE)
                start_recording_time = time.time()
                is_recording = True
            
            
            if operating_mode != 'off':
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces_rect = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=9)
                number_of_faces = len(faces_rect)
                sio.emit('from_raspi_number_of_faces_detected', number_of_faces)
                if number_of_faces == 1:
                    for x, y, w, h in faces_rect:
                        face_img = cv2.resize(frame[y:y+h, x:x+w], (160, 160))
                        face_signature = face_net.embeddings(np.expand_dims(face_img, axis=0))
                        
                        min_dist = 0.7
                        identity = 'Unknown'
                        
                        # Check distance to known faces in the database
                        for key, value in database.items():
                            dist = np.linalg.norm(value - face_signature)
                            if dist < min_dist:
                                min_dist = dist
                                identity = key
                        
                        if operating_mode != 'manual':
                            if identity != 'Unknown':
                                print('Auto open activate')
                                if not is_door_open:
                                    authorized_users[identity]['recognized_count'] += 1
                                    for key, value in authorized_users.items():
                                        if value['recognized_count'] == 1:
                                            is_door_open = True
                                            for k in authorized_users.keys():
                                                authorized_users[k]['recognized_count'] = 0
                                            # allow_authorized_user_entry(key, frame.copy(), PWM)
                                            sio.emit('from_raspi_user_entered', f'{authorized_users[key]["name"]} has entered.')
                                            threading.Thread(target=allow_authorized_user_entry, args=(key, frame, PWM)).start()
                        
                        # Draw rectangle around the face
                        color = (0, 0, 255) if identity == 'Unknown' else (0, 255, 0)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                        # cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                        text = f'{authorized_users[identity]["name"]} {(dist * 1.2):.2f}' if identity != 'Unknown' else 'Unknown'
                        cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1.8, color, 2)
        if is_recording:
            video_writer.write(frame)
            frame_count += 1
            if time.time() - start_recording_time > 15:
                print('Stopped recording video...')
                video_writer.release()
                is_recording = False
                if os.path.exists(os.path.join('videos', 'new', 'new_video.avi')):
                    os.rename(os.path.join('videos', 'new', 'new_video.avi'), os.path.join('videos', 'ready', f'{time.time_ns()}.avi'))
                is_recording = False
        ret, jpeg = cv2.imencode('.jpg', frame)
        byte_frame = jpeg.tobytes()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + byte_frame + b'\r\n')



def send_recorded_videos():
    global frame_count, FPS
    with requests.Session() as session:
        while True:
            if len(os.listdir(os.path.join('videos', 'ready'))) > 0:
                current_day_response = session.get(REST_ENDPOINTS['day_records_v2'])
                current_day_json = current_day_response.json()
                for filename in os.listdir(os.path.join('videos', 'ready')):
                    file = open(os.path.join('videos', 'ready', filename), 'rb')
                    # video_capture = cv2.VideoCapture(os.path.join('videos', 'ready', filename))
                    # frame_count = video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
                    # print('frame count: ', frame_count)

                    # video_duration_seconds = frame_count//10
                    payload = MultipartEncoder(fields={
                        'recorded_video': (filename, file, 'video/avi'),
                        'day_record_id': current_day_json['_id'],
                        'video_duration_seconds': f'{round(frame_count / FPS)}-sec',
                    })
                    response = session.post(REST_ENDPOINTS['detections_v1'], data=payload, headers={'Content-Type': payload.content_type})
                    file.close()
                    print(response.json())
                    os.remove(os.path.join('videos', 'ready', filename))
                    frame_count = 0
                    # time.sleep(0.1)



def listen_for_gpio():
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            sio.emit('from_raspi_doorbell_press', 'The Doorbell has been pressed. Please check your camera.')
            sound_buzzer(BUZZER_PIN)





try:
    if __name__ == '__main__':
        threads = (
                threading.Thread(target=send_recorded_videos),
                threading.Thread(target=listen_for_gpio),
            )
        for t in threads:
            t.start()

        @app.route('/')
        def index():
            return render_template('index.html')

        @app.route('/video_feed')
        def video_feed():
            return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

        app.run(host='0.0.0.0', port=8080, debug=False)
        
except KeyboardInterrupt:
    GPIO.cleanup()


