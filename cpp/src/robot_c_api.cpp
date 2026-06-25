#include "robot.hpp"

// Single global Robot instance — constructed once when the .so is loaded.
static Robot robot;

extern "C" {
    void robot_move_right(double speed, double distance, bool detachThread, double rampFraction) {
        robot.setLeftThread([&]{ robot.getLeftMotor().move( distance, speed, rampFraction); }, detachThread);
    }

    void robot_start_right_continous(double speed) {
        robot.getLeftMotor().startContinuous(speed);
    }

    void robot_set_right_speed(double speed) {
        robot.getLeftMotor().setContinuousSpeed(speed);
    }

    void robot_stop_right_continous() {
        robot.getLeftMotor().stopContinuous();
    }

    void robot_move_left(double speed, double distance, bool detachThread, double rampFraction) {
        robot.setRightThread([&]{ robot.getRightMotor().move( distance, speed, rampFraction); }, detachThread);
    }

    void robot_start_left_continous(double speed) {
        robot.getRightMotor().startContinuous(speed);
    }

    void robot_set_left_speed(double speed) {
        robot.getRightMotor().setContinuousSpeed(speed);
    }

    void robot_stop_left_continous() {
        robot.getRightMotor().stopContinuous();
    }


    void robot_move_forward(double speed, double distance, bool detachThread, double rampFraction) {
        robot.moveForward(speed, distance, detachThread, rampFraction);
    }

    void robot_turn(double speed, double angle, bool detachThread, double rampFraction) {
        robot.turn(speed, angle, detachThread, rampFraction);
    }

    void robot_turn_gyro(double speed, double angle, bool detachThread, double rampFraction) {
        robot.turnGyro(speed, angle, detachThread, rampFraction);
    }

    void robot_move_straight_gyro(double speed, double distance, double angle, double rampFraction) {
        robot.moveStraightGyro(speed, distance, angle, rampFraction);
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

    void reset_gyro(double angle) {
        robot.resetGyro(angle);
    }
}
