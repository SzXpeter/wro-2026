#pragma once

#include <thread>
#include <atomic>
#include "stepper_motor.hpp"
#include "mpu6050.hpp"

class Robot {
public:
    Robot();
    ~Robot();

    void   moveRight(double speed, double distance, bool detachThread);
    void   moveLeft(double speed, double distance, bool detachThread);
    void   moveForward(double speed, double distance, bool detachThread);
    void   turn(double speed, double angle, bool detachThread);
    void   moveStraightGyro(double speed, double distanceMeters, double angle);
    void   turnGyro(double speed, double angle, bool detachThread);

    void   waitForLeftMotor()  { if (leftThread_.joinable())  leftThread_.join(); }
    void   waitForRightMotor() { if (rightThread_.joinable()) rightThread_.join(); }

    void waitForMotors() {
        if (leftThread_.joinable()) leftThread_.join();
        if (rightThread_.joinable()) rightThread_.join();
    }

    void   startGyro();
    void   stopGyro();
    double getGyroAngle();
    void   resetGyro();

private:
    static constexpr double PID_KP         = 32.5;
    static constexpr double PID_KI         = 0.01;
    static constexpr double PID_KD         = 2.5;
    static constexpr double RAMP_START_SPEED = 800.0; // microsteps/s — matches move() ramp start
    static constexpr double RAMP_FRACTION    = 0.2;   // fraction of travel used for ramp up/down
    // BCM GPIO pins (Waveshare DRV8825 HAT):
    //   Left  motor: DIR=13, STEP=19, ENABLE=12
    //   Right motor: DIR=24, STEP=26, ENABLE=4
    static constexpr int LEFT_STEP    = 19;
    static constexpr int LEFT_DIR     = 13;
    static constexpr int LEFT_ENABLE  = 12;
    static constexpr int RIGHT_STEP   = 26;
    static constexpr int RIGHT_DIR    = 24;
    static constexpr int RIGHT_ENABLE = 4;
    static constexpr int MICROSTEPS   = 16;

    std::atomic<bool> isGyroOn_ = false;

    std::thread  gyroThread_;
    StepperMotor left_;
    std::thread  leftThread_;
    StepperMotor right_;
    std::thread  rightThread_;
    MPU6050      gyro_;
};
