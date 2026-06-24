#pragma once

#include <thread>
#include <atomic>
#include <functional>
#include "stepper_motor.hpp"
#include "mpu6050.hpp"

class Robot {
public:
    Robot();
    ~Robot();

    void   moveRight(double speed, double distance, bool detachThread, double rampFraction = .2);
    void   moveLeft(double speed, double distance, bool detachThread, double rampFraction = .2);
    void   moveForward(double speed, double distance, bool detachThread, double rampFraction = .2);
    void   turn(double speed, double angle, bool detachThread, double rampFraction = .2);
    void   moveStraightGyro(double speed, double distanceMeters, double angle, double rampFraction = .2);
    void   turnGyro(double speed, double angle, bool detachThread, double rampFraction = .2);

    void   waitForLeftMotor()  { if (leftThread_.joinable())  leftThread_.join(); }
    void   waitForRightMotor() { if (rightThread_.joinable()) rightThread_.join(); }

    StepperMotor& getLeftMotor()  { return left_; }
    StepperMotor& getRightMotor() { return right_; }
    void setLeftThread( std::function<void()> thread, bool detach) {
        leftThread_ = std::thread(thread);
        if (leftThread_.joinable() && !detach) leftThread_.join();
    }
    void setRightThread(std::function<void()> thread, bool detach) {
        rightThread_ = std::thread(thread);
        if (rightThread_.joinable() && !detach) rightThread_.join();
    }

    void waitForMotors() {
        if (leftThread_.joinable()) leftThread_.join();
        if (rightThread_.joinable()) rightThread_.join();
    }

    void   startGyro();
    void   stopGyro();
    double getGyroAngle();
    void   resetGyro();

private:
    static constexpr double PID_KP         = 25;
    static constexpr double PID_KI         = 0.01;
    static constexpr double PID_KD         = 2.5;
    static constexpr double RAMP_START_SPEED = 800.0; // microsteps/s — matches move() ramp start
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
