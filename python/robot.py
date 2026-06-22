import ctypes
import math
import os
import RPi.GPIO as GPIO

"""
38 GPIO fizikai szám: GRIO pin 1,  kiengedő
40 GPIO fizikai szám: GRIO pin 21, emelkar
36 GPIO fizikai szám: GRIO pin 16, leengedőkar
"""

class Robot:
    WHEEL_DIAMETER = 5.6
    WHEEL_CIRCUMFERENCE = WHEEL_DIAMETER * math.pi

    def __init__(self, BUTTON_PIN: int = 27):
        self.BUTTON_PIN = BUTTON_PIN
        lib_path = os.path.join(os.path.dirname(__file__), 'lib', 'librobot.so')
        self._lib = ctypes.CDLL(lib_path)
        self._setup_signatures()    
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def wait_for_button_press(self):
        print("gombra várva...")

        while GPIO.input(self.BUTTON_PIN) != GPIO.LOW:
            pass
        print("Megnyomva")

    def is_button_pressed(self) -> bool:
        return GPIO.input(self.BUTTON_PIN) == GPIO.LOW

    def _setup_signatures(self):
        self._lib.robot_move_right.argtypes    = [ctypes.c_double, ctypes.c_double, ctypes.c_bool]
        self._lib.robot_move_right.restype     = None
        self._lib.robot_move_left.argtypes     = [ctypes.c_double, ctypes.c_double, ctypes.c_bool]
        self._lib.robot_move_left.restype      = None
        self._lib.robot_move_forward.argtypes  = [ctypes.c_double, ctypes.c_double, ctypes.c_bool]
        self._lib.robot_move_forward.restype   = None
        self._lib.robot_turn.argtypes          = [ctypes.c_double, ctypes.c_double, ctypes.c_bool]
        self._lib.robot_turn.restype           = None
        self._lib.robot_turn_gyro.argtypes     = [ctypes.c_double, ctypes.c_double, ctypes.c_bool]
        self._lib.robot_turn_gyro.restype      = None
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

    def turn_left(self, distance: float, speed: float = 20, detach: bool = False) -> None:
        self._lib.robot_move_right(
            self._to_microsteps(speed),
            self._angle_to_microsteps(-distance),
            detach,
        )
    

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

    def turn_gyro(self, angle: float, speed: float = 10, detach: bool = False) -> None:
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

    def gyro_angle(self) -> float:
        """Visszaadja a giroszkóp jelenlegi szögét fokban."""
        return self._lib.get_gyro_angle()

    def reset_gyro(self) -> None:
        """Nullázza a giroszkóp szögét."""
        self._lib.reset_gyro()

    