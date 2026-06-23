import ctypes
import math
import os, sys, time
import RPi.GPIO as GPIO # type: ignore
from brickpi3 import BrickPi3
from my_color_sernsor import my_color_sensor

"""
38 GPIO fizikai szám: GRIO pin 1,  kiengedő
40 GPIO fizikai szám: GRIO pin 21, emelkar
36 GPIO fizikai szám: GRIO pin 16, leengedőkar
"""

class Robot(BrickPi3):
    WHEEL_DIAMETER = 5.6
    WHEEL_CIRCUMFERENCE = WHEEL_DIAMETER * math.pi

    def __init__(self, BUTTON_PIN: int = 27):
        self.BUTTON_PIN = BUTTON_PIN
        self.color_sensor_PORT = self.PORT_1 # TODO: check real port
        self.color_sensor = my_color_sensor(self.color_sensor_PORT, self)
        lib_path = os.path.join(os.path.dirname(__file__), 'lib', 'librobot.so')
        self._lib = ctypes.CDLL(lib_path)
        self._setup_signatures()    
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.start_log()
        # self.wait_for_button_press()

    def __delete__(self, instance):
        self.stop_left_continuos()
        self.stop_right_continuos()

    def wait_for_button_press(self):
        print("gombra várva...")

        while GPIO.input(self.BUTTON_PIN) != GPIO.LOW:
            pass
        print("Megnyomva")

    def is_button_pressed(self) -> bool:
        return GPIO.input(self.BUTTON_PIN) == GPIO.LOW

    def _setup_signatures(self):
        self._lib.robot_move_right.argtypes   = [ctypes.c_double, ctypes.c_double, ctypes.c_bool]
        self._lib.robot_move_right.restype    = None

        self._lib.robot_start_right_continous.argtypes = [ctypes.c_double]
        self._lib.robot_start_right_continous.restype  = None
        self._lib.robot_set_right_speed.argtypes       = [ctypes.c_double]
        self._lib.robot_set_right_speed.restype        = None
        self._lib.robot_stop_right_continous.argtypes  = []
        self._lib.robot_stop_right_continous.restype   = None

        self._lib.robot_move_left.argtypes    = [ctypes.c_double, ctypes.c_double, ctypes.c_bool]
        self._lib.robot_move_left.restype     = None

        self._lib.robot_start_left_continous.argtypes  = [ctypes.c_double]
        self._lib.robot_start_left_continous.restype   = None
        self._lib.robot_set_left_speed.argtypes        = [ctypes.c_double]
        self._lib.robot_set_left_speed.restype         = None
        self._lib.robot_stop_left_continous.argtypes   = []
        self._lib.robot_stop_left_continous.restype    = None

        self._lib.robot_move_forward.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_bool]
        self._lib.robot_move_forward.restype  = None
        self._lib.robot_turn.argtypes         = [ctypes.c_double, ctypes.c_double, ctypes.c_bool]
        self._lib.robot_turn.restype          = None
        self._lib.robot_turn_gyro.argtypes    = [ctypes.c_double, ctypes.c_double, ctypes.c_bool]
        self._lib.robot_turn_gyro.restype     = None
        self._lib.robot_move_straight_gyro.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]
        self._lib.robot_move_straight_gyro.restype  = None
        self._lib.wait_for_left_motor.argtypes = []
        self._lib.wait_for_left_motor.restype  = None
        self._lib.wait_for_right_motor.argtypes= []
        self._lib.wait_for_right_motor.restype = None
        self._lib.get_gyro_angle.argtypes      = []
        self._lib.get_gyro_angle.restype       = ctypes.c_double
        self._lib.reset_gyro.argtypes          = []
        self._lib.reset_gyro.restype           = None

    def _to_microsteps(self, cm: float) -> float:
        return cm / self.WHEEL_CIRCUMFERENCE * 3200

    def _angle_to_microsteps(self, angle: float) -> float:
        return 4400 / 90 * -angle

    def move_right(self, distance: float, speed: float = 20, detach: bool = False) -> None:
        self._lib.robot_move_left(
            self._to_microsteps(speed),
            self._to_microsteps(distance),
            detach,
        )

    def move_left(self, distance: float, speed: float = 20, detach: bool = False) -> None:
        self._lib.robot_move_right(
            self._to_microsteps(speed),
            self._to_microsteps(-distance),
            detach,
        )

    def turn_right(self, distance: float, speed: float = 20, detach: bool = False) -> None:
        self._lib.robot_move_left(
            self._to_microsteps(speed),
            self._angle_to_microsteps(distance),
            detach,
        )

    def start_left_continuos(self, speed: float):
        self._lib.robot_start_left_continous(
            self._to_microsteps(speed)
        )

    def stop_left_continuos(self):
        self._lib.robot_stop_left_continous()

    def start_right_continuos(self, speed: float):
        self._lib.robot_start_right_continous(
            self._to_microsteps(speed)
        )

    def stop_right_continuos(self):
        self._lib.robot_stop_right_continous()

    def turn_left(self, distance: float, speed: float = 5, detach: bool = False) -> None:
        self._lib.robot_move_right(
            self._to_microsteps(speed),
            self._angle_to_microsteps(-distance),
            detach,
        )

    def turn_left_gyro(self, speed, angle, slow=True):
        start_angle = self.gyro_angle()
        if (start_angle > angle):
            self.start_left_continuos(speed)
            angle_now = self.gyro_angle()
            while (angle_now > angle):
                if (slow and abs(angle - angle_now) < 10):
                    self.start_left_continuos(speed/5)
                    slow = False
                angle_now = self.gyro_angle()
        else: 
            self.start_left_continuos(-speed)
            angle_now = self.gyro_angle()
            while (angle_now < angle): 
                if (slow and abs(angle_now - angle) < 10):
                    self.start_left_continuos(-speed/5)
                    slow = False
                angle_now = self.gyro_angle()
        self.stop_left_continuos()
    
    def turn_right_gyro(self, speed, angle, slow=True):
        start_angle = self.gyro_angle()
        start_time = time.time()
        is_fastened = False
        if (start_angle > angle):
            self.start_right_continuos(speed/2)
            angle_now = self.gyro_angle()
            while (angle_now > angle):
                if (slow and abs(angle - angle_now) < 10):
                    self.start_right_continuos(speed/5)
                    slow = False
                angle_now = self.gyro_angle()
                if time.time() - start_time > 2 and not is_fastened:
                    self.start_right_continuos(speed)
                    self.log("fastened")
                    is_fastened = True

        else: 
            self.start_right_continuos(-speed/2)
            angle_now = self.gyro_angle()
            while (angle_now < angle): 
                if (slow and abs(angle_now - angle) < 10):
                    self.start_right_continuos(-speed/5)
                    slow = False
                angle_now = self.gyro_angle()
                if time.time() - start_time > 2 and not is_fastened:
                    self.start_right_continuos(-speed)
                    self.log("fastened")
                    is_fastened = True

        self.stop_right_continuos()

    def move(self, distance: float, speed: float = 20, detach: bool = False) -> None:
        """
        Mozgatja a robotot előre/hátra cm-ben.

        params
        ----------
        distance: float
            Távolság cm-ben. Negatív érték esetén hátrafelé mozog.
        speed: float
            Sebesség cm/s-ban.
        detach: bool
            Ha True, a mozgás külön szálon fut és azonnal visszatér.
        """
        self._lib.robot_move_forward(
            self._to_microsteps(speed),
            self._to_microsteps(distance),
            detach,
        )

    def turn(self, angle: float, speed: float = 10, detach: bool = False) -> None:
        """
        Forgatja a robotot giroszkóp nélkül.

        params
        ----------
        angle: float
            Szög fokban. Pozitív = jobbra, negatív = balra.
        speed: float
            Sebesség cm/s-ban.
        detach: bool
            Ha True, a mozgás külön szálon fut és azonnal visszatér.
        """
        self._lib.robot_turn(self._to_microsteps(speed), angle, detach)

    def move_straight_gyro(self, distance: float, angle: float, speed: float = 20) -> None:
        """
        Mozgatja a robotot előre/hátra cm-ben giroszkóppal egyenesen tartva.

        params
        ----------
        distance: float
            Távolság cm-ben. Negatív érték esetén hátrafelé mozog.
        speed: float
            Sebesség cm/s-ban.
        angle: float
            Cél szög fokban.
        """
        self._lib.robot_move_straight_gyro(
            self._to_microsteps(speed),
            self._to_microsteps(distance),
            angle
        )

    def wait_for_left_motor(self) -> None:
        """Megvárja, míg a bal motor befejezi a mozgást."""
        self._lib.wait_for_left_motor()

    def wait_for_right_motor(self) -> None:
        """Megvárja, míg a jobb motor befejezi a mozgást."""
        self._lib.wait_for_right_motor()

    def turn_gyro(self, angle: float, speed: float = 7, detach: bool = False) -> None:
        """
        Forgatja a robotot giroszkóppal.

        params
        ----------
        angle: float
            Szög fokban. Pozitív = jobbra, negatív = balra.
        speed: float
            Sebesség cm/s-ban.
        detach: bool
            Ha True, a mozgás külön szálon fut és azonnal visszatér.
        """
        self._lib.robot_turn_gyro(self._to_microsteps(speed), angle, detach)

    def align_to_black(self, speed=5, black_threshold = None):
        self.start_left_continuos(speed=speed)
        self.start_right_continuos(speed=speed)
        is_running = 3 
        while (is_running):
            if self.color_sensor.is_black_reflection(black_threshold):
                is_running -= 1
            elif is_running: 
                is_running = 3
        self.log(f"fekete: {self.color_sensor.get_reflection()}")
        self.stop_left_continuos()
        self.stop_right_continuos()

    def gyro_angle(self) -> float:
        """Visszaadja a giroszkóp jelenlegi szögét fokban."""
        return self._lib.get_gyro_angle()

    def reset_gyro(self) -> None:
        """Nullázza a giroszkóp szögét."""
        self._lib.reset_gyro()

    def log(self, *text):
        with open(self.log_file_name, "a") as f:
            f.write(f"{' '.join(map(str, text))}\n")
            print(f"{' '.join(map(str, text))}\n", file=sys.stderr)
                
    def start_log(self):
        try:
            os.mkdir("./log")
        except:
            pass

        log_files = os.listdir("./log")
        i = 1
        if len(log_files) > 0:
            log_files.sort()
            i = int(log_files[-1][4:7]) + 1

        self.log_file_name = "./log/log_{0:03d}.txt".format(i)
        self.displayed_events = []
        with open(self.log_file_name, "w+") as f:
            pass
        print("Log file created: {0}".format(self.log_file_name), file=sys.stderr)    
