import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)

on_time = 0.1 # time led is ON in seconds
off_time = 0.1 # time led is OFF in seconds

while True:
    GPIO.output(17, GPIO.HIGH)
    time.sleep(on_time) 
    GPIO.output(17, GPIO.LOW)
    time.sleep(off_time) 
