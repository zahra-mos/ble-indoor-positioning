#button
import RPi.GPIO as GPIO
import time
import subprocess
import os

BUTTON_PIN = 12
COUNTER_FILE = "ref_counter.txt"

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def get_next_reference():
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, "w") as f:
            f.write("1")
        return "RS1"

    with open(COUNTER_FILE, "r") as f:
        count = int(f.read().strip())

    next_ref = f"RS{count}"
    with open(COUNTER_FILE, "w") as f:
        f.write(str(count + 1))

    return next_ref

print("Waiting for button press...")

try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            reference_point = get_next_reference()
            print(f"Button pressed! Starting scan for {reference_point}...")
            subprocess.run(["python3", "ble_receiver.py", reference_point])
            time.sleep(0.5)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    GPIO.cleanup()
