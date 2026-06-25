import dis
from pickle import GLOBAL
from turtle import left

from servo_motors import * 
import cv2, os, time, threading
from datetime import datetime
from framecolors import process_image

COLOR_GRID = None



def release_all_to_grid():
    release_cubes()
    for _ in range(3):
        my_robot.move_straight_gyro(5.1, angle=0, speed=3)
        time.sleep(0.1)
        # my_robot.wait_for_button_press()
        release_cubes()

def go_to_pos_vertical(pos):
    set_vertical_motor(375 + pos*415)

def pick_up_two_cubes(lefter):
    raise NotImplementedError()
    # go_to_pos_vertical(0)
    # time.sleep(0.25)
    # my_robot.wait_for_button_press()
    lift_cube(down = False)
    time.sleep(0.75)
    set_lifter(100)        
    time.sleep(0.25)
    threading.Thread(target=get_cube_back).start()
    set_vertical_motor(abs(my_robot.get_motor_encoder(my_robot.PORT_A)) + 690)
    my_robot.wait_for_button_press()
    time.sleep(0.75)
    down_lifter()
    if lefter:
        set_vertical_motor(abs(my_robot.get_motor_encoder(my_robot.PORT_A)) + 225)
    # my_robot.wait_for_button_press()
    time.sleep(0.5)
    
    lift_cube()

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
    my_robot.turn_left_gyro(speed=12.5, angle=-55, slow=False)
    my_robot.turn_right_gyro(speed=12.5, angle=0, slow=False)
    my_robot.move_straight_gyro(distance=-80, angle=0, speed=20, rampFraction=.075)

    def movement_in_picture_and_process():
        # megtolja a dolgot a picture_and_process függvényben
        my_robot.turn_right_gyro(angle=-20, speed=12.5)
        my_robot.move_straight_gyro(distance=10, angle=-20, speed=15)
        # my_robot.log(my_robot.gyro_angle())
        my_robot.move_straight_gyro(distance=28, angle=0, speed=15)

    COLOR_GRID = picture_and_process(movement_in_picture_and_process)
    my_robot.log(COLOR_GRID)
    # my_robot.wait_for_button_press()


    # my_robot.wait_for_button_press()
    my_robot.move_straight_gyro(distance=-11, angle=-30, speed=15)
    # my_robot.wait_for_button_press()
    my_robot.turn_gyro(speed=10, angle = 40)
    my_robot.move_straight_gyro(40, angle=40, speed=15, rampFraction=0.1)
    my_robot.turn_gyro(0)
    my_robot.move_straight_gyro(3.5, angle=0, speed=15, rampFraction=0.1)
    # my_robot.wait_for_button_press()
    my_robot.align_to_black()
    my_robot.turn_gyro(90)
    my_robot.align_to_black()

def pick_up_color_cubes(now_position, goal_position, pos, two_cubes = False):
    set_lifter(-5)
    if now_position > goal_position:
        my_robot.move_straight_gyro(-14.5+14*(goal_position-now_position+1), angle=90, speed=15)
    elif now_position < goal_position:
        my_robot.log(13.5*(now_position-goal_position), now_position, goal_position)
        my_robot.move_straight_gyro(distance=13.5 + 14*(goal_position-now_position-1), angle=90, speed=15)
    my_robot.align_to_black()
    my_robot.move_straight_gyro(-4 + (4.5*pos), angle=90, rampFraction=0.5, speed=10)
    my_robot.turn_gyro(0)
    go_to_pos_vertical(pos)
    time.sleep(1.5)
    my_robot.move_straight_gyro(3.5, 0, speed=10, rampFraction=0.5)

    lift_cube()
    for _ in range(2):
        my_robot.move_straight_gyro(6.6, 0, speed=10, rampFraction=0.5)
        lift_cube()
        time.sleep(0.5)
    my_robot.move_straight_gyro(-17, 0, speed=10, rampFraction=0.25)
    my_robot.align_to_black()
    my_robot.turn(90)
    my_robot.move_straight_gyro(-2*pos, 90, speed=10, rampFraction=0.25)
    my_robot.align_to_black()


def pick_up_cube(now_position: int, goal_position: int, cube_pos1: int, cube_pos2:int):
    go_to_pos_vertical(0)
    set_lifter(-5)
    if now_position > goal_position:
        my_robot.move_straight_gyro(15.5+14*(goal_position-now_position), angle=90, speed=15)
    elif now_position < goal_position:
        my_robot.log(13*(now_position-goal_position), now_position, goal_position)
        my_robot.move_straight_gyro(distance=12.5 + 14*(goal_position-now_position), angle=90, speed=15)
    my_robot.align_to_black()
    my_robot.move_straight_gyro(-4.125, angle=90, rampFraction=0.5, speed=10)
    my_robot.turn_gyro(0)
    my_robot.move_straight_gyro(3.9, 0, speed=10, rampFraction=0.5)
    # my_robot.wait_for_button_press()
    # pick_up_two_cubes(0)
    my_robot.move_straight_gyro(-10, 0, speed=10, rampFraction=0.5)
    my_robot.align_to_black()
    my_robot.turn(90)
    my_robot.align_to_black()

def put_cubes_down(now_position):
    goal_position = 1
    if now_position > goal_position:
        my_robot.move_straight_gyro(-14.5+14*(goal_position-now_position+1), angle=90, speed=15)
    elif now_position < goal_position:
        my_robot.log(13.5*(now_position-goal_position), now_position, goal_position)
        my_robot.move_straight_gyro(distance=13.5 + 14*(goal_position-now_position-1), angle=90, speed=15)
    # my_robot.move_straight_gyro(distance=13.5, angle=90)
    my_robot.align_to_black()
    my_robot.move_straight_gyro(distance=4, angle=90, rampFraction=0.35)
    my_robot.turn_gyro(0, speed=7)
    my_robot.move_straight_gyro(distance=-40, angle=0, rampFraction=.1)
    my_robot.align_to_black(speed=-5)
    my_robot.move_straight_gyro(distance=-22, speed=10, angle=0)
    my_robot.wait_for_button_press()
    set_slope(55, True)
    release_all_to_grid()

def test_moving():
    for i in range(1, 5):
        my_robot.wait_for_button_press()
        my_robot.move_straight_gyro(30, angle=0, speed=10)
        print(my_robot.gyro_angle())

def print_gyro():
    while my_robot.is_button_pressed() == False:
        print(my_robot.gyro_angle())
        time.sleep(0.01)

def picture_and_process(movement):
    # and also push the thing back
    try: 
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        image_path = os.path.join(os.path.dirname(__file__), "kepek", f'kep_{timestamp}.jpg')
        print(image_path)
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
            my_robot.log("Feldolgozás külön szálon fut...")
        
            #Mozgás...
            movement()


            worker.join()  # megvárjuk, míg a szál végez
            my_robot.log(f"process_image futási ideje: {results['elapsed_ms']:.1f} ms")
            my_robot.log(f"Végül: {results['grid']}")
            return results['grid']

    except Exception as e:
        print(f"Hiba történt: {e}")
        movement()
        return [['kek', 'feher', 'feher', 'sarga'], ['zold', 'sarga', 'zold', 'kek'], ['sarga', 'feher', 'kek', 'kek']]
