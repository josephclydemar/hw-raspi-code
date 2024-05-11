# from picamera2 import Picamera2 # type: ignore
import cv2 as cv
from flask import Flask, render_template, Response # type: ignore
import os

# PICAM2 = Picamera2()
# # Setup Camera configurations
# PICAM2.preview_configuration.main.size = (1280, 720)
# PICAM2.preview_configuration.main.format = 'RGB888'
# PICAM2.preview_configuration.align()
# PICAM2.configure('preview')
# PICAM2.start()

# app = Flask(__name__)
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
app = Flask(__name__, template_folder=template_dir)


def initialize_picamera():
    global picam_initialized, picam
    picam = Picamera2()
    picam.preview_configuration.main.size = (1280, 720)
    picam.preview_configuration.main.format = 'RGB888'
    picam.preview_configuration.align()
    picam.configure('preview')
    picam.start()
    picam_initialized = True


def generate():
    # with Picamera2() as PICAM2:
    #     PICAM2.preview_configuration.main.size = (1280, 720)
    #     PICAM2.preview_configuration.main.format = 'RGB888'
    #     PICAM2.preview_configuration.align()
    #     PICAM2.configure('preview')
    #     PICAM2.start()

    #     while True:
    #         frame = PICAM2.capture_array()
    #         ret, jpeg = cv.imencode('.jpg', frame)
    #         bin_frame = jpeg.tobytes()
    #         yield (b'--frame\r\n'
    #             b'Content-Type: image/jpeg\r\n\r\n' + bin_frame + b'\r\n')


    global picam_initialized, picam
    if not picam_initialized:
        initialize_picamera()
    while True:
    


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)


