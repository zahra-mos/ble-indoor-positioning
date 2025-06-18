import asyncio
import sys
from datetime import datetime
from bleak import BleakScanner
from RPLCD.gpio import CharLCD
import RPi.GPIO as GPIO

# === Setup GPIO ===
GPIO.setwarnings(False)  # Suppress GPIO pin reuse warning

# === Get reference point from command-line ===
if len(sys.argv) < 2:
    print("Usage: python3 ble_receiver.py RS<number>")
    sys.exit(1)

REFERENCE_POINT = sys.argv[1]
TEXT_FILE = f"rssi_data_{REFERENCE_POINT}.txt"
scan_duration = 30  # seconds

# === Target MAC addresses to monitor ===
TARGET_MACS = [
    "2c:cf:67:c8:dd:d0",
    "2c:cf:67:c8:dd:ea",
    "2c:cf:67:c8:dd:d2",
    "2c:cf:67:c8:dd:d3"
]

# === Setup LCD ===
lcd = CharLCD(
    cols=16, rows=2,
    pin_rs=25, pin_e=24,
    pins_data=[23, 17, 18, 22],
    numbering_mode=GPIO.BCM,
    pin_rw=None
)

# === Utility Functions ===
def create_txt():
    with open(TEXT_FILE, "w") as f:
        f.write("Timestamp\tReference Point\tDevice Address\tDevice Name\tRSSI\n")

# Save to the csv file
def save_to_txt(rp, address, name, rssi):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(TEXT_FILE, "a") as f:
        line = f"{timestamp}\t{rp}\t{address}\t{name if name else 'Unknown'}\t{rssi}\n"
        f.write(line)


#Display on the LCD
def show_on_lcd(rssi, address):
    lcd.clear()
    short_mac = address[-5:].replace(":", "")
    lcd.cursor_pos = (0, 0)
    lcd.write_string(f"RSSI:{rssi: >4}")
    lcd.cursor_pos = (1, 0)
    lcd.write_string(f"MAC:{short_mac}")

def detection_callback(device, advertisement_data):
    if device.address.lower() in TARGET_MACS:
        rssi = advertisement_data.rssi
        print(f"[{datetime.now()}] Found {device.address} | RSSI: {rssi} | Name: {device.name}")
        save_to_txt(REFERENCE_POINT, device.address, device.name, rssi)
        show_on_lcd(rssi, device.address)

# === Main BLE Scan Logic ===
async def continuous_scan():
    print(f"Scanning for beacons at {REFERENCE_POINT}... Press Ctrl+C to stop.")
    create_txt()

    scanner = BleakScanner(detection_callback=detection_callback)

    await scanner.start()
    start_time = datetime.now()

    try:
        while (datetime.now() - start_time).seconds < scan_duration:
            await asyncio.sleep(0.5)  # keep running while the callback handles detection
    finally:
        await scanner.stop()
        print("Finished Scanning")
        lcd.clear()
        lcd.write_string("Finished")
        GPIO.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(continuous_scan())
    except KeyboardInterrupt:
        print("Scan stopped by user.")
        lcd.clear()
        GPIO.cleanup()
