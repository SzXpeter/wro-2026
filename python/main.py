
from task import *

my_robot.wait_for_button_press()


# test_turn()
# my_robot.move_straight_gyro(distance=50, angle=0, speed=25)
# time.sleep(2)
# my_robot.move_straight_gyro(distance=50, angle=0, speed=25)

go_to_picture()
time.sleep(1)

exit(0)
# test_moving()
# my_robot.wait_for_button_press()
# test_release_cubes()
# print_gyro()
# picture_and_process()
# release_cubes()
# n = 315
# # set_vertical_motor(450)
# for i in range(3):
#     # my_robot.wait_for_button_press()
#     set_vertical_motor(n + 480*i)
#     time.sleep(0.5)
#     my_robot.wait_for_button_press()
#     grab_cube()

my_robot.log()

my_robot.wait_for_button_press()
set_vertical_motor(0)

time.sleep(0.5)
my_robot.wait_for_button_press()

# down_cubes_slowly()
# Egy kép elkészítése
BP.reset_all()

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