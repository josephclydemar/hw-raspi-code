import time
import RPi.GPIO as GPIO # type: ignore

def get_distance(TRIG_PIN, ECHO_PIN):
	# Set trigger to HIGH for 10us
	GPIO.output(TRIG_PIN, True)
	time.sleep(0.00001)
	GPIO.output(TRIG_PIN, False)

	# Wait for echo pin to go high
	start_time = time.time()
	while GPIO.input(ECHO_PIN) == 0:
		if time.time() - start_time > 0.1:
			# print("Timeout")
			return None
	pulse_start = time.time()

	# Wait for echo pin to go low
	while GPIO.input(ECHO_PIN) == 1:
		if time.time() - start_time > 0.1:
			# print("Timeout")
			return None
	pulse_end = time.time()

	# Calculate pulse duration
	pulse_duration = pulse_end - pulse_start

	# Convert time to distance (speed of sound: 343m/s or 34300cm/s)
	distance = pulse_duration * 34300 / 2
	return distance