#!/usr/bin/env python3
from brickpi3 import *
import sys, time

class my_color_sensor:
    def __init__(self, port, BP: BrickPi3):
        self.port = port
        self.BP = BP
        self.BP.set_sensor_type(port, BP.SENSOR_TYPE.EV3_COLOR_REFLECTED)
        self.last_time = time.time()
        self.last_value = 0
        try:
            with open('color_values_{0}.txt'.format(self.port), 'r') as f:
                self.white_value = int(f.readline())
                self.black_value = int(f.readline())
        except:
            self.white_value = 422
            self.black_value = 622
            print('Calibration missing: {0}'.format(port), file=sys.stderr )            


    def get_reflection(self):
        # if time.time_ns() - self.last_time < 1e7:
        #     return self.last_value
        
        # try:
        #     value = self.BP.get_sensor(self.port)
        #     diff = self.black_value - self.white_value
        #     self.last_time = time.time_ns()
        #     self.last_value = (int(((self.black_value - value) / diff) * 100))
        # except SensorError as se:
        #     self.BP.log("Colorsensor ", self.port, " SensorError: ", se)
        # except Exception as e:
        #     self.BP.log("Colorsensor ", self.port, " :", e)
        # return self.last_value
        value = self.BP.get_sensor(self.port)
        diff = self.black_value - self.white_value
        return (int(((self.black_value - value) / diff) * 100))      


    def is_black_reflection(self, threshold = None):
        if threshold == None:
            threshold = 15
        reflection = self.get_reflection()
        return  reflection <= threshold
    
    def  is_white_reflection(self, threshold = None):
        if threshold == None:
            threshold = 85
        return self.get_reflection() >= threshold

    def is_not_black_reflection(self, threshold = None):
        return not self.is_black_reflection(threshold)
    
    def is_not_white_reflection(self, threshold = None):
        return not self.is_white_reflection(threshold)

    def calibrate(self, button_pressed):
        print(self.port, "white")
        while not button_pressed():
            pass
        white_value = self.BP.get_sensor(self.port)
        time.sleep(0.3)
        # self.display.draw.text((10,10), 'FEKETE', font=fonts.load('luBS24'))
        # Sound().speak('Black')
        print(self.port, "black")
        while not button_pressed():
            pass
        black_value = self.BP.get_sensor(self.port)

        with open('color_values_{0}.txt'.format(self.port), 'w') as f:
            f.write('{0}\n'.format(white_value))
            f.write('{0}\n'.format(black_value))

        print('White: {0}, Black: {1}'.format(white_value, black_value), file=sys.stderr )

class my_gyro_sensor:
    def __init__(self, BP: BrickPi3, port) -> None:
        self.BP = BP
        self.port = port
        self.BP.set_sensor_type(port, self.BP.SENSOR_TYPE.EV3_GYRO_ABS_DPS)
        self.correction = 0
        self.offset = 0
        self.last_angle = 0
        self.last_time = time.time()

    @property
    def angle_raw(self):
        # resultx42 = self.BP.get_sensor(self.port)
        # return resultx42[0] * 2 + resultx42[1]
        return  self.BP.get_sensor(self.port)[0]

    def reset_without_reset(self, now_angle):
        self.offset = -now_angle

    def reset_with_angle(self, now_angle):
        self.offset = -now_angle - self.angle_raw
        self.last_angle = now_angle
        print(self.offset)

    def reset(self):
        self.correction = -self.angle_raw
        self.offset = 0
        # self.last_angle = 0

    @property
    def angle(self):
        if time.time_ns() - self.last_time < 1e8:
            # print(time.time_ns() - self.last_time)
            return -self.last_angle
        try:
            self.last_angle = self.angle_raw + self.correction + self.offset
            # print(self.last_angle)
        except SensorError as se:
            self.BP.log("Gyro SensorError: ", se)
        except Exception as e:
            self.BP.log("Gyro:", e)
        self.last_time = time.time_ns()
        return -self.last_angle
        #  return self.angle_raw + self.correction + self.offset
    