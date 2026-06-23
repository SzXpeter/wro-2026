import robot
import cv2, os, time, threading
from datetime import datetime
from framecolors import process_image
import RPi.GPIO as GPIO
import brickpi3

my_robot = robot.Robot()
my_robot.wait_for_button_press()
COLOR_GRID = None
LEENGEDO_SERVO_PIN = 16
EMELKAR_SERVO_PIN = 21
KIENGETO_SERVO_PIN = 20
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LEENGEDO_SERVO_PIN, GPIO.OUT)
GPIO.setup(EMELKAR_SERVO_PIN, GPIO.OUT)
GPIO.setup(KIENGETO_SERVO_PIN, GPIO.OUT)
leengedo_pwm = GPIO.PWM(LEENGEDO_SERVO_PIN, 50)
emelkar_pwm = GPIO.PWM(EMELKAR_SERVO_PIN, 50)
kiengeto_pwm = GPIO.PWM(KIENGETO_SERVO_PIN, 50)

leengedo_pwm.start(0)
emelkar_pwm.start(0)
kiengeto_pwm.start(0)
BP = brickpi3.BrickPi3()
VERTICAL_MOTOR_PORT = BP.PORT_A
BP.reset_motor_encoder(VERTICAL_MOTOR_PORT)

def set_vertical_motor(angle, speed= 1000):
    BP.set_motor_limits(VERTICAL_MOTOR_PORT, 0, speed)
    BP.set_motor_position(BP.PORT_A, angle)

def set_servo_motors(pwm, angle = 98, hold=True):

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
    
def down_cubes_slowly():
    for angle in range(23, 98, 15):
        set_servo_motors(leengedo_pwm, angle, hold=True)
    set_servo_motors(leengedo_pwm, 90, hold=True)
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

def grab_cube():
    # set_servo_motors(emelkar_pwm, 25, hold=True)

    set_servo_motors(emelkar_pwm, 200, hold = True)
    time.sleep(1)
    set_servo_motors(emelkar_pwm, 0, hold=False)
    set_servo_motors(emelkar_pwm, -25, hold=False)
    threading.Thread(target=get_cube_back).start()

def get_cube_back():
    set_servo_motors(leengedo_pwm, 45)
    time.sleep(1)
    set_servo_motors(leengedo_pwm, 30)
    time.sleep(0.5)
    set_servo_motors(leengedo_pwm, 25, hold=False)

def up_cubes():
    set_servo_motors(leengedo_pwm, 45)
    set_servo_motors(leengedo_pwm, 23)

def release_cubes():
    set_servo_motors(kiengeto_pwm, 25, hold=False)
    time.sleep(0.25)
    set_servo_motors(kiengeto_pwm, 130, hold=True)

def test_turn():
    for i in range(1, 5):
        my_robot.turn_right_gyro(10, 90*i)
        my_robot.log(my_robot.gyro_angle())
        time.sleep(0.5)
    my_robot.wait_for_button_press()
    for i in range(3, -1, -1):
        my_robot.turn_right_gyro(10, 90*i)
        my_robot.log(my_robot.gyro_angle())
        time.sleep(0.5)

def go_to_picture():
    global COLOR_GRID
    my_robot.turn_left_gyro(speed=7.5, angle=-55, slow=False)
    my_robot.log(my_robot.gyro_angle())
    my_robot.turn_right_gyro(speed=7.5, angle=0, slow=False)
    my_robot.log(my_robot.gyro_angle())
    my_robot.move_straight_gyro(-75, angle=0, speed=15)
    my_robot.log(my_robot.gyro_angle())
    COLOR_GRID = picture_and_process()
    my_robot.log(COLOR_GRID)
    # my_robot.wait_for_button_press()


    my_robot.turn_right_gyro(angle=-40, speed=10)
    my_robot.move_straight_gyro(7, angle=-40, speed=15)
    my_robot.log(my_robot.gyro_angle())
    my_robot.move_straight_gyro(25, angle=0, speed=15)
    my_robot.wait_for_button_press()
    my_robot.move_straight_gyro(-15, angle=-45, speed=10)
    my_robot.wait_for_button_press()
    my_robot.turn_right_gyro(speed=10, angle=30)
    my_robot.move_straight_gyro(40, angle=30, speed=15)

def test_moving():
    for i in range(1, 5):
        my_robot.wait_for_button_press()
        my_robot.move_straight_gyro(30, angle=0, speed=10)
        print(my_robot.gyro_angle())

def print_gyro():
    while my_robot.is_button_pressed() == False:
        print(my_robot.gyro_angle())
        time.sleep(0.01)

def picture_and_process():
    try: 
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_path = os.path.join(os.path.dirname(__file__), f'kep_{timestamp}.jpg')

        if ret:
            cv2.imwrite(image_path, frame)
            print(f"Kép elmentve: kep_{timestamp}.jpg")
        else:
            print("Hiba: nem sikerült képet készíteni!")

        cap.release()

        base = os.path.dirname(image_path)
        image = cv2.imread(image_path)
        if image is None:
            print(f"Kép nem olvasható: {image_path}")
            raise Exception(f"Kép nem olvasható: {image_path}")
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
            return results['grid']

    except Exception as e:
        print(f"Hiba történt: {e}")
        return [['kek', 'feher', 'feher', 'sarga'], ['zold', 'sarga', 'zold', 'kek'], ['sarga', 'feher', 'kek', 'kek']]
    
def task1():
    my_robot.move_straight_gyro(distance=56, angle=0)
    my_robot.turn(angle=45)
