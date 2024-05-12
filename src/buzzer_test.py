# Only used for testing the Buzzer
import RPi.GPIO as GPIO # type: ignore
import time

GPIO.setmode(GPIO.BCM)

led_pin = 20
button_pin = 12
buzzer_pin = 19

GPIO.setup(led_pin, GPIO.OUT)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(buzzer_pin, GPIO.OUT)

def turn_on(pin):
	GPIO.output(pin, GPIO.HIGH)
	
def turn_off(pin):
	GPIO.output(pin, GPIO.LOW)	
	
def buzzer_beep():
	turn_on(buzzer_pin)
	time.sleep(0.1)
	turn_off(buzzer_pin)
	time.sleep(0.1)
	
try:
	while True:
		if GPIO.input(button_pin) == GPIO.LOW:
			turn_on(led_pin)
			for _ in range(2):
				buzzer_beep()
			print("button pressed")
			
		else:
			turn_off(led_pin)
			print("button released")
			
		
		time.sleep(0.1)
		
except KeyboardInterrupt:
	GPIO.cleanup()
