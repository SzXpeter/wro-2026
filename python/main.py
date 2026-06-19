import sys
import os
import threading
import time
import cv2
import RPi.GPIO as GPIO
from framecolors import process_image
from robot import Robot
BUTTON_PIN = 27  


robot = Robot()

def wait_for_button_press():
    print("gombra várva...")
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    while GPIO.input(BUTTON_PIN) != GPIO.LOW:
        pass
    print("Megnyomva")

wait_for_button_press()
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Hiba: nem sikerült megnyitni a kamerát!")
    exit()

print("Kamera sikeresen megnyitva.")
print(f"Felbontás: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")

# Egy kép elkészítése
ret, frame = cap.read()
image_path = os.path.join(os.path.dirname(__file__), 'kep.jpg')

if ret:
    cv2.imwrite(image_path, frame)
    print("Kép elmentve: kep.jpg")
else:
    print("Hiba: nem sikerült képet készíteni!")

cap.release()

base = os.path.dirname(image_path)
image = cv2.imread(image_path)
if image is None:
    print(f"Kép nem olvasható: {image_path}")
else:
    results: dict[str, object] = {}

    def run_process_image():
        start = time.perf_counter()
        results['grid'] = process_image(image)[0]
        results['elapsed_ms'] = (time.perf_counter() - start) * 1000

    worker = threading.Thread(target=run_process_image)
    worker.start()

    # itt a fő szál közben mást is csinálhat
    print("Feldolgozás külön szálon fut...")
 
    #MOzgás...

    worker.join()  # megvárjuk, míg a szál végez
    print(f"process_image futási ideje: {results['elapsed_ms']:.1f} ms")
    print(results['grid'])

'''
# --- C++ calculator ---
lib_path = os.path.join(os.path.dirname(__file__), 'lib', 'libcalculator.so')
lib = ctypes.CDLL(lib_path)

lib.calc_add.argtypes = [ctypes.c_double, ctypes.c_double]
lib.calc_add.restype  = ctypes.c_double
lib.calc_sub.argtypes = [ctypes.c_double, ctypes.c_double]
lib.calc_sub.restype  = ctypes.c_double
lib.calc_mul.argtypes = [ctypes.c_double, ctypes.c_double]
lib.calc_mul.restype  = ctypes.c_double
lib.calc_div.argtypes = [ctypes.c_double, ctypes.c_double]
lib.calc_div.restype  = ctypes.c_double

a, b = 10.0, 3.0
print(f"{a} + {b} = {lib.calc_add(a, b)}")
print(f"{a} - {b} = {lib.calc_sub(a, b)}")
print(f"{a} * {b} = {lib.calc_mul(a, b)}")
print(f"{a} / {b} = {lib.calc_div(a, b):.4f}")
print(f"{a} / 0  = {lib.calc_div(a, 0.0)}")
'''