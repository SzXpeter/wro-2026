#include "robot.hpp"

// Single global Robot instance — constructed once when the .so is loaded.
static Robot robot;

extern "C" {
    void robot_move_forward(double speed, double distance) {
        robot.moveForward(speed, distance);
    }

    void robot_turn(double speed, double angle) {
        robot.turn(speed, angle);
    }

    double get_gyro_angle() {
        return robot.getGyroAngle();
    }

    void reset_gyro() {
        robot.resetGyro();
    }
}
