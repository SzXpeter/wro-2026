#include "robot.hpp"
#include <chrono>
#include <cmath>
#include <iostream>

Robot::Robot()
    : left_ (LEFT_STEP,  LEFT_DIR,  LEFT_ENABLE,  MICROSTEPS)
    , right_(RIGHT_STEP, RIGHT_DIR, RIGHT_ENABLE, MICROSTEPS)
    , gyro_ ()
{
    gyro_.init();
    gyro_.calibrate(1000);
    startGyro();
    right_.enable();
    left_.enable();
    // gyro_.resetAngleX();
}

Robot::~Robot() {
    isGyroOn_.store(false);
    gyroThread_.join();
}

void Robot::moveRight(double speed, double distance, bool detachThread, double rampFraction) {
    rightThread_ = std::thread([&]{ right_.move(  distance, speed, rampFraction); });
    if (!detachThread) rightThread_.join();
}

void Robot::moveLeft(double speed, double distance, bool detachThread, double rampFraction) {
    leftThread_ = std::thread([&]{ left_.move(  distance, speed, rampFraction); });
    if (!detachThread) leftThread_.join();
}

void Robot::moveForward(double speed, double distance, bool detachThread, double rampFraction) {
    int steps = static_cast<int>(distance);

    // Right motor is mirrored → opposite direction for forward movement
    leftThread_  = std::thread([&]{ left_.move(  steps, speed, rampFraction); });
    rightThread_ = std::thread([&]{ right_.move(-steps, speed, rampFraction); });

    if (detachThread) return;
    if (leftThread_.joinable()) leftThread_.join();
    if (rightThread_.joinable()) rightThread_.join();
}

void Robot::turn(double speed, double angle, bool detachThread = false, double rampFraction) {
    int steps = 2200 / 90 * -angle;
    // steps = steps = static_cast<int>(-(angle * 155.0 * 3200.0) / (360.0 * 56.0));
   
    leftThread_  = std::thread([&]{ left_.move(steps, speed, rampFraction); });
    rightThread_ = std::thread([&]{ right_.move(steps, speed, rampFraction); });

    if (detachThread) return;
    if (leftThread_.joinable()) leftThread_.join();
    if (rightThread_.joinable()) rightThread_.join();
}

void Robot::startGyro() {
    if (isGyroOn_.load()) return;
    isGyroOn_.store(true);
    gyroThread_ = std::thread([this]{
        while (isGyroOn_.load()) {
            gyro_.update();
            std::this_thread::sleep_for(std::chrono::microseconds(1250));
        }
    });
}

double Robot::getGyroAngle() {
    return gyro_.getAngleX();
}

void Robot::resetGyro() {
    gyro_.resetAngleX();
}

void Robot::stopGyro() {
    isGyroOn_.store(false);
    if (gyroThread_.joinable())
        gyroThread_.join();
}

void Robot::moveStraightGyro(double speed, double distance, double angle, double rampFraction) {
    stopGyro();

    double dir            = (distance < 0.0) ? -1.0 : 1.0;
    double correctDistance = std::abs(distance) * 1.2344;
    double targetAngle    = angle;
    double estimatedSteps = 0.0;
    double integral       = 0.0;
    double lastError      = 0.0;

    using Clock = std::chrono::steady_clock;
    auto lastTime = Clock::now();

    left_.startContinuous(dir * RAMP_START_SPEED);
    right_.startContinuous(-dir * RAMP_START_SPEED);

    while (estimatedSteps < correctDistance) {
        auto now = Clock::now();
        double dt = std::chrono::duration<double>(now - lastTime).count();
        lastTime = now;

        gyro_.update();

        double progress    = std::min(estimatedSteps / correctDistance, 1.0);
        double speedFactor = (progress < rampFraction)        ? progress / rampFraction
                           : (progress > 1.0 - rampFraction)  ? (1.0 - progress) / rampFraction
                                                                : 1.0;
        double currentSpeed = std::max(speed * speedFactor, RAMP_START_SPEED);

        double error      = gyro_.getAngleX() - targetAngle;
        integral         += error * dt;
        double derivative = (dt > 0.0) ? (error - lastError) / dt : 0.0;
        lastError         = error;

        double correction = PID_KP * error + PID_KI * integral + PID_KD * derivative;

        left_.setContinuousSpeed(dir * currentSpeed + correction);
        right_.setContinuousSpeed(-dir * currentSpeed + correction);

        estimatedSteps += currentSpeed * dt;

        std::this_thread::sleep_for(std::chrono::microseconds(1250));
    }

    left_.stopContinuous();
    right_.stopContinuous();
    startGyro();
}

void Robot::turnGyro(double speed, double angle, bool detachThread, double rampFraction) {
    stopGyro();

    double startAngle = gyro_.getAngleX(); // measure from current heading — no reset
    double dir        = (angle < 0.0) ? 1.0 : -1.0;

    left_.startContinuous(RAMP_START_SPEED * dir);
    right_.startContinuous(RAMP_START_SPEED * dir);

    while (true) {
        gyro_.update();

        double turned   = std::abs(gyro_.getAngleX() - startAngle);
        double absAngle = std::abs(angle);
        if (turned >= absAngle) break;

        double progress    = turned / absAngle;
        double speedFactor = (progress < rampFraction) ? progress / rampFraction
                           : (progress > 1.0 - rampFraction) ? (1.0 - progress) / rampFraction : 1.0;
        double currentSpeed = std::max(speed * speedFactor, RAMP_START_SPEED) * dir;

        left_.setContinuousSpeed(currentSpeed);
        right_.setContinuousSpeed(currentSpeed);

        std::this_thread::sleep_for(std::chrono::microseconds(1250));
    }

    left_.stopContinuous();
    right_.stopContinuous();
    startGyro();
}
