#pragma once

#include <thread>
#include "stepper_motor.hpp"
#include "mpu6050.hpp"

class Robot {
public:
    Robot();
    ~Robot();

    // speed:    microsteps / second
    // distance: microsteps
    void   moveForward(double speed, double distance);
    void   turn(double speed, double angle);
    void   calibrateGyro();
    void   startGyro();
    double getGyroAngle();
    void   resetGyro();

private:
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

    bool isGyroOn_ = false;
    bool firstTurnOn_ = true;

    std::thread  gyroThread_;
    StepperMotor left_;
    StepperMotor right_;
    MPU6050      gyro_;
};
