#include "robot.hpp"

Robot::Robot()
    : left_ (LEFT_STEP,  LEFT_DIR,  LEFT_ENABLE,  MICROSTEPS)
    , right_(RIGHT_STEP, RIGHT_DIR, RIGHT_ENABLE, MICROSTEPS)
    , gyro_ ()
{
    gyro_.init();
    gyro_.calibrate(5000);
    startGyro();
    right_.enable();
    left_.enable();
    gyro_.resetAngleZ();
}

Robot::~Robot() {
    isGyroOn_ = false;
    gyroThread_.join();
}

void Robot::moveForward(double speed, double distance) {
    int steps = static_cast<int>(distance);

    // Right motor is mirrored → opposite direction for forward movement
    std::thread leftThread  ([&]{ left_.move( steps, speed); });
    std::thread rightThread ([&]{ right_.move(-steps, speed); });

    leftThread.join();
    rightThread.join();
}

void Robot::turn(double speed, double angle) {
    int steps = 2200 / 90 * -angle;
   
    std::thread leftThread  ([&]{ left_.move( steps, speed); });
    std::thread rightThread ([&]{ right_.move(steps, speed); });

    leftThread.join();
    rightThread.join();
}

void Robot::calibrateGyro() {
    gyro_.calibrate();
}

void Robot::startGyro() {
    if (isGyroOn_) return;
    isGyroOn_ = true;
    gyroThread_ = std::thread([this]{
        while (isGyroOn_) {
            gyro_.update();
            std::this_thread::sleep_for(std::chrono::microseconds(1250));
        }
    });
}

double Robot::getGyroAngle() {
    return gyro_.getAngleZ();
}

void Robot::resetGyro() {
    gyro_.resetAngleZ();
}
