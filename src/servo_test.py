# Only used for testing the servo
import RPi.GPIO as GPIO # type: ignore
import time

# Set GPIO mode
GPIO.setmode(GPIO.BCM)

# Set GPIO pin for servo
servo_pin = 13

# Set PWM frequency (Hz)
PWM_freq = 50

# Set PWM duty cycle range
PWM_duty_min = 2.5
PWM_duty_max = 12.5

# Setup GPIO pin for servo as PWM
GPIO.setup(servo_pin, GPIO.OUT)
pwm = GPIO.PWM(servo_pin, PWM_freq)

# def angle_to_duty(angle):
#     duty = (angle / 180.0) * (PWM_duty_max - PWM_duty_min) + PWM_duty_min
#     return duty



pwm.start(0)

try:
    # Start PWM
    
    # Rotate servo clockwise to 90 degrees
    pwm.ChangeDutyCycle(10)
    time.sleep(2)  # Adjust time for your servo to reach 90 degrees

    pwm.ChangeDutyCycle(5)
    time.sleep(2)  # Adjust time for your servo to return to 0 degrees
    
    # Rotate servo counterclockwise back to 0 degrees (return to original position)
    pwm.ChangeDutyCycle(3)
    time.sleep(2)  # Adjust time for your servo to return to 0 degrees

finally:
    # Clean up
    pwm.stop()
    GPIO.cleanup()

# pwm.stop()
# GPIO.cleanup()
