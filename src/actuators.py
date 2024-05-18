import time
import RPi.GPIO as GPIO # type: ignore

def open_door(pwm):
    pwm.start(0)
    pwm.ChangeDutyCycle(7.5)
    time.sleep(2) # Adjust time for your servo to reach 90 degrees
    
def close_door(pwm):
    pwm.start(0)
    pwm.ChangeDutyCycle(12.5)
    time.sleep(2)

def turnon_light(pin):
    GPIO.output(pin, GPIO.HIGH)

def turnoff_light(pin):
    GPIO.output(pin, GPIO.LOW)

def sound_buzzer(pin):
    for _ in range(10):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.05)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.05)