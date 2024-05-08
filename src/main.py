with_gui = 0
try:
    with_gui = int(input('Enter mode\n(0) without GUI, (1) with GUI: '))
except Exception as e:
    print(e)
    quit()

import time
import os
import asyncio
import base64
import aiohttp  # type: ignore
import cv2 as cv # type: ignore
import RPi.GPIO as GPIO # type: ignore

# custome modules
from globals import TRIG_PIN, ECHO_PIN, PICAM2, TRAINING_DIR, VALIDATION_DIR, HAAR_CASCADE, SIO, HTTP_REST_ENDPOINTS, REMOTE_SERVER_HOST, VIDEO_WRITER
import sensors
import api_interface
import collect_training_data
# import train_model
# import recognize_face

# FACE_RECOGNIZER = cv.face.LBPHFaceRecognizer_create()



# Set GPIO mode
GPIO.setmode(GPIO.BCM)

# Setup GPIO pins
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# Setup Camera configurations
PICAM2.preview_configuration.main.size = (1280, 720)
PICAM2.preview_configuration.main.format = 'RGB888'
PICAM2.preview_configuration.align()
PICAM2.configure('preview')
PICAM2.start()







# socket.io event listeners
@SIO.event
def from_server_to_add_new_authorized_user(data):
    global add_new_authorized_user
    global new_authorized_user_data
    add_new_authorized_user = True
    new_authorized_user_data = data
    print('message: ', data)
    



# people = []
# if os.path.exists(TRAINING_DIR):
#     for p in os.listdir(TRAINING_DIR):
#         people.append(p)
# else:
#     first_authorized_user = input('Enter First Authorized User: ')
#     is_done_capturing = False
#     count = 0
#     while not is_done_capturing:
#         frame = PICAM2.capture_array()
#         is_successfully_captured, is_done_capturing = collect_training_data.capture_new_images(HAAR_CASCADE, frame, first_authorized_user, TRAINING_DIR, VALIDATION_DIR, count, 20)
#         if is_successfully_captured:
#             count += 1
#     people.append(first_authorized_user)
#     # train_model.train_face_recognizer(TRAINING_DIR, VALIDATION_DIR, people)

# print('Recognized People: ', people)
# print('Press D to Exit...')


# if os.path.exists('./model_trained.yml'):
#     FACE_RECOGNIZER.read('./model_trained.yml')
# else:
#     train_model.train_face_recognizer(TRAINING_DIR, VALIDATION_DIR, people)




async def main():
    global VIDEO_WRITER
    is_socket_connected = False
    add_new_authorized_user = False
    new_authorized_user_data = None
    is_recording_video = False
    try:
        currently_captured_image_count = 0
        async with aiohttp.ClientSession() as session:
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
                resized_frame = cv.resize(frame, (182, 102))

                face_detection_state = 'OFF'
                distance = sensors.get_distance(TRIG_PIN, ECHO_PIN)
                if distance is not None: # Just for printing the distance
                    print('Distance: {:.2f} cm'.format(distance))
                else:
                    print('Ultrasonic Sensor is not connected...')
            
                if distance != None and distance < 150: # Filter distances below 150cm
                    if not is_recording_video:
                        VIDEO_WRITER = cv.VideoWriter(os.path.join('vids', f"video_{time.strftime('%Y%m%d%H%M%S')}.avi"), cv.VideoWriter_fourcc(*'XVID'), 20.0, (1280, 720))
                        is_recording_video = True

                    face_detection_state = 'ON'
                    # recognize_face.identify_face(HAAR_CASCADE, FACE_RECOGNIZER, frame, people)
                    if add_new_authorized_user:
                        if new_authorized_user_data != None:
                            is_successfully_captured, is_done_capturing = collect_training_data.capture_new_images(HAAR_CASCADE, frame, new_authorized_user_data['name'], TRAINING_DIR, VALIDATION_DIR, currently_captured_image_count, 20)
                            if is_successfully_captured:
                                currently_captured_image_count += 1
                            if is_done_capturing:
                                currently_captured_image_count = 0
                                resized_frame = cv.resize(frame, (182, 102))
                                _, im_buff_arr = cv.imencode('.jpg', resized_frame)
                                byte_frame = im_buff_arr.tobytes()
                                profile_image_data = base64.b64encode(byte_frame).decode('utf-8')
                                await asyncio.gather(api_interface.send_profile_user_image(session, HTTP_REST_ENDPOINTS['authorized_users_v1'], (profile_image_data, new_authorized_user_data)))
                                print(f'New Authorized User [{new_authorized_user_data["name"]}] is registered.')
                                add_new_authorized_user = False
                        else:
                            print('no user data...')
                    if VIDEO_WRITER is not None:
                        # print('Writing video...')
                        VIDEO_WRITER.write(frame)
                else:
                    if VIDEO_WRITER is not None:
                        # print('Saving video...')
                        VIDEO_WRITER.release()
                        is_recording_video = False
                        # recently_recorded_videos =
                    current_day_record_data = await api_interface.create_current_day_record_get_request_task(session, HTTP_REST_ENDPOINTS['day_records_v2'])
                    request_tasks = api_interface.send_recorded_videos(session, HTTP_REST_ENDPOINTS['detections_v1'], os.listdir('vids'), current_day_record_data['_id'])
                    for task in request_tasks:
                        await task
                cv.putText(frame, f'Face Detection State: {face_detection_state}', (30, 40), cv.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)

                if with_gui == 1:
                    cv.imshow('Frame', frame)
                    if cv.waitKey(20) == ord('d'):
                        break

    except KeyboardInterrupt:
        GPIO.cleanup()
        if VIDEO_WRITER is not None:
            VIDEO_WRITER.release()
        if with_gui == 1:
            cv.destroyAllWindows()







asyncio.run(main())










GPIO.cleanup()
if with_gui == 1:
    cv.destroyAllWindows()

