import ctypes
import math
import os
import threading
import time
import cv2

from framecolors import process_image

_robot_lib_path = os.path.join(os.path.dirname(__file__), 'lib', 'librobot.so')
_robot = ctypes.CDLL(_robot_lib_path)
_robot.robot_move_forward.argtypes = [ctypes.c_double, ctypes.c_double]
_robot.robot_move_forward.restype  = None
_robot.robot_turn.argtypes = [ctypes.c_double, ctypes.c_double]
_robot.robot_turn.restype  = None
_robot.get_gyro_angle.argtypes = []
_robot.get_gyro_angle.restype  = ctypes.c_double
_robot.reset_gyro.argtypes = []
_robot.reset_gyro.restype = None

wheel_diameter = 5.6
wheel_circumference = wheel_diameter * math.pi

def move(distance: float, speed: float = 20) -> None:
    """
    Moves the robot forwards or backwards by cm.

    params
    ----------
    distance: float
        The distance the robot moves in centimeter. If negative the robot moves backwards
    speed: float
        The speed the robot moves in cm/s
    """
    _robot.robot_move_forward(speed / wheel_circumference * 3200, distance / wheel_circumference * 3200)

def turn(angle: float, speed: float = 10) -> None:
    """
    Turns the robot by the given degrees without using a gyrosensor.

    params
    ----------
    angle: float
        The degrees the robot turns by. Positive values turn the robot right, negative values turn it left
    speed: float
        The speed the robot turns by in cm/s
    """
    _robot.robot_turn(speed / wheel_circumference * 3200, angle)

def gyro_angle() -> float:
    return _robot.get_gyro_angle()

def reset_gyro() -> None:
    _robot.reset_gyro()

for i in range(600):
    print(gyro_angle())
    time.sleep(.1)

'''
image_path = os.path.join(os.path.dirname(__file__), 'capture.jpg')
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