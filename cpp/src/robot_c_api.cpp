#include "robot.hpp"

// Single global Robot instance — constructed once when the .so is loaded.
static Robot robot;

extern "C" {
    void robot_move_forward(double speed, double distance, bool detachThread) {
        robot.moveForward(speed, distance, detachThread);
    }

    void robot_turn(double speed, double angle, bool detachThread) {
        robot.turn(speed, angle, detachThread);
    }

    void robot_turn_gyro(double speed, double angle, bool detachThread) {
        robot.turnGyro(speed, angle, detachThread);
    }

    void robot_move_straight_gyro(double speed, double distance) {
        robot.moveStraightGyro(speed, distance);
    }

    double get_gyro_angle() {
        return robot.getGyroAngle();
    }

    void reset_gyro() {
        robot.resetGyro();
    }
}
