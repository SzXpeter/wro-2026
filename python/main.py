from python.cube_test import best_order
from task import *

my_robot.wait_for_button_press()

# my_robot.wait_for_button_press()
# my_robot.reset_gyro()
# my_robot.calibrate()
# time.sleep(1)
now_pos = 0
order = best_order(COLOR_GRID)
go_to_picture()
pick_up_color_cubes(now_pos, order[0], 0)
now_pos = order[0]
pick_up_color_cubes(now_pos, order[1], 1)
now_pos = order[1]
pick_up_color_cubes(now_pos, order[2], 2)
now_pos = order[2]
# pick_up_color_cubes(1, 2, 2)
put_cubes_down(now_pos)

# release_all_to_grid()
# picture_and_process()
# time.sleep(1)
# pick_up_two_cubes(0)



# time.sleep(0.5)
my_robot.wait_for_button_press()
set_vertical_motor(0)
time.sleep(2)
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
#     lift_cube()

# down_cubes_slowly()
# Egy kép elkészítése
my_robot.reset_all()

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