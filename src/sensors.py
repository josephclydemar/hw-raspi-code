import time
import RPi.GPIO as GPIO # type: ignore



def get_distance(trig_pin, echo_pin):
	# Set trigger to HIGH for 10us
	GPIO.output(trig_pin, True)
	time.sleep(0.00001)
	GPIO.output(trig_pin, False)

	# Wait for echo pin to go high
	start_time = time.time()
	while GPIO.input(echo_pin) == 0:
		if time.time() - start_time > 0.1:
			# print('Timeout')
			return 6000
	pulse_start = time.time()

	# Wait for echo pin to go low
	while GPIO.input(echo_pin) == 1:
		if time.time() - start_time > 0.1:
			# print('Timeout')
			return 6000
	pulse_end = time.time()

	# Calculate distance (speed of sound: 343m/s or 34300cm/s)
	distance = (pulse_end - pulse_start) * 34300 / 2
	return distance