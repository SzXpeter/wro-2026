from encodings.punycode import T
from unittest import mock

import RPi.GPIO as GPIO # type: ignore
import time, threading

from numpy import true_divide
import robot
my_robot = robot.Robot()


SLOPE_SERVO_PIN = 16 #LEENGEDO_SERVO
LIFTER_SERVO_PIN = 21 #EMELKAR_SERVO
RELEASE_SERVO_PIN = 20 #KIENGETO_SERVO
VERTICAL_MOTOR_PORT = my_robot.PORT_A
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(SLOPE_SERVO_PIN, GPIO.OUT)
GPIO.setup(LIFTER_SERVO_PIN, GPIO.OUT)
GPIO.setup(RELEASE_SERVO_PIN, GPIO.OUT)
slope_pwm = GPIO.PWM(SLOPE_SERVO_PIN, 50)
lifter_pwm = GPIO.PWM(LIFTER_SERVO_PIN, 50)
release_pwm = GPIO.PWM(RELEASE_SERVO_PIN, 50)

slope_pwm.start(0)
lifter_pwm.start(0)
release_pwm.start(0)
my_robot.reset_motor_encoder(VERTICAL_MOTOR_PORT)

def set_servo_motor(pwm: GPIO.PWM, angle: float, hold: bool):

    """
        30  fellül
        270 allul
    """
    cycle = -(angle - 270) / 36 + 4.6
    # GPIO.output(motorpin, True)

    pwm.ChangeDutyCycle(cycle)
    time.sleep(0.3)
    if not hold:
        pwm.ChangeDutyCycle(0)

def set_slope(angle: float = 0, hold=False):
    set_servo_motor(slope_pwm, angle, hold)

def set_lifter(angle: float = 0, hold=True):
    set_servo_motor(lifter_pwm, angle, hold)

def set_release(angle = 98, hold=True):
    set_servo_motor(release_pwm, angle, hold)

def set_vertical_motor(angle = 0, speed= 1000):
    my_robot.set_motor_limits(VERTICAL_MOTOR_PORT, 0, speed)
    my_robot.set_motor_position(my_robot.PORT_A, -angle)



def get_cube_back():
    set_slope(36.5, hold=True)
    time.sleep(0.25)
    set_slope(32, hold=True)
    time.sleep(0.5)
    set_slope(25, hold=True)
    time.sleep(0.5)
    set_slope(25)

def up_cubes():
    set_slope(45)
    set_slope(23)

def release_cubes():
    set_release(25, hold=False)
    time.sleep(0.25)
    set_release(130, hold=True)

def lift_cube(down = True):
    # set_servo_motors(emelkar_pwm, 25, hold=True)

    set_lifter(200, hold = True)
    if down:
        time.sleep(0.5)
        down_lifter()
        threading.Thread(target=get_cube_back).start()

def down_lifter():
    set_lifter(-10, hold=True)

def down_cubes_slowly():
    for angle in range(23, 98, 10):
        set_slope(angle, hold=True)
    set_slope(90, hold=True)
    # set_servo_motors  (30, hold=False)

def test_release_cubes():
    release_cubes()

    down_cubes_slowly()
    my_robot.wait_for_button_press()

    for _ in range(3):
        release_cubes()
        my_robot.move_straight_gyro(distance=5, angle=0, speed=10)
        print(my_robot.gyro_angle())
    release_cubes()