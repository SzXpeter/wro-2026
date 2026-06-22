#include "robot.hpp"

// Single global Robot instance — constructed once when the .so is loaded.
static Robot robot;

extern "C" {
    void robot_move_right(double speed, double distance, bool detachThread) {
        robot.moveRight(speed, distance, detachThread);
    }

    void robot_move_left(double speed, double distance, bool detachThread) {
        robot.moveLeft(speed, distance, detachThread);
    }

    void robot_move_forward(double speed, double distance, bool detachThread) {
        robot.moveForward(speed, distance, detachThread);
    }

    void robot_turn(double speed, double angle, bool detachThread) {
        robot.turn(speed, angle, detachThread);
    }

    void robot_turn_gyro(double speed, double angle, bool detachThread) {
        robot.turnGyro(speed, angle, detachThread);
    }

    void robot_move_straight_gyro(double speed, double distance, double angle) {
        robot.moveStraightGyro(speed, distance, angle);
    }

    void wait_for_left_motor() {
        robot.waitForLeftMotor();
    }

    void wait_for_right_motor() {
        robot.waitForRightMotor();
    }

    double get_gyro_angle() {
        return robot.getGyroAngle();
    }

    void reset_gyro() {
        robot.resetGyro();
    }
}
