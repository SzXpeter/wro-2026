#include "stepper_motor.hpp"
#include <wiringPi.h>
#include <cmath>
#include <stdexcept>

static constexpr unsigned int PULSE_US     = 5;  // DRV8825 min step pulse: 1.9µs
static constexpr unsigned int DIR_SETUP_US = 5;

StepperMotor::StepperMotor(int stepPin, int dirPin, int enablePin, int microsteps)
    : stepPin_(stepPin), dirPin_(dirPin), enablePin_(enablePin), microsteps_(microsteps)
{
    // wiringPiSetupGpio() is safe to call multiple times
    if (wiringPiSetupGpio() < 0)
        throw std::runtime_error("wiringPi init failed — gpio group member?");

    pinMode(stepPin_, OUTPUT);
    pinMode(dirPin_,  OUTPUT);
    digitalWrite(stepPin_, LOW);
    digitalWrite(dirPin_,  LOW);

    if (enablePin_ >= 0) {
        pinMode(enablePin_, OUTPUT);
        disable(); // start disabled (active LOW)
    }
}

StepperMotor::~StepperMotor() {
    stopContinuous();
    disable();
}

void StepperMotor::enable() {
    if (enablePin_ >= 0)
        digitalWrite(enablePin_, HIGH);
}

void StepperMotor::disable() {
    if (enablePin_ >= 0)
        digitalWrite(enablePin_, LOW);
}

void StepperMotor::pulse() {
    ++stepCount_;
    digitalWrite(stepPin_, HIGH);
    delayMicroseconds(PULSE_US);
    digitalWrite(stepPin_, LOW);
}

long StepperMotor::getStepCount() const { return stepCount_.load(); }
void StepperMotor::resetStepCount()     { stepCount_.store(0); }

void StepperMotor::move(int steps, double stepsPerSecond) {
    if (steps == 0 || stepsPerSecond <= 0.0)
        return;

    digitalWrite(dirPin_, steps < 0 ? HIGH : LOW);
    delayMicroseconds(DIR_SETUP_US);

    int absSteps = (steps < 0) ? -steps : steps;
    unsigned int periodUs = static_cast<unsigned int>(1'000'000.0 / stepsPerSecond);
    int delayUs    = (periodUs > PULSE_US) ? (periodUs - PULSE_US) : 1u;

    int remainingSteps = absSteps;
    float rampSpeed = 800.0f;
    unsigned short rampSteps = 0;
    while (rampSpeed < stepsPerSecond) {
        int currentUs = static_cast<unsigned int>(1'000'000.0 / rampSpeed) - PULSE_US;
        for (int i = 0; i < ((100 > remainingSteps) ? remainingSteps : 100) ; ++i) {
            pulse();
            delayMicroseconds(currentUs);
        }
        rampSpeed *= 1.5;
        remainingSteps-=100;
        rampSteps++;
    }
    for (int i = 0; i < 2 * remainingSteps - absSteps; ++i) {
        pulse();
        delayMicroseconds(delayUs);
    }
    for (int i = 0; i < rampSteps; i++) {
        int currentUs = static_cast<unsigned int>(1'000'000.0 / rampSpeed) - PULSE_US;
        for (int i = 0; i < 100; i++) {
            pulse();
            delayMicroseconds(currentUs);
        }
        rampSpeed /= 1.5;
    }
}

void StepperMotor::startContinuous(double stepsPerSecond = 3200.0) {
    if (running_) return;
    setContinuousSpeed(stepsPerSecond);
    running_ = true;
    continuousThread_ = std::thread(&StepperMotor::continuousLoop, this);
}

void StepperMotor::stopContinuous() {
    running_ = false;
    if (continuousThread_.joinable())
        continuousThread_.join();
}

void StepperMotor::setContinuousSpeed(double stepsPerSecond) {
    continuousSpeed_.store(stepsPerSecond);
}

void StepperMotor::continuousLoop() {
    bool lastDir = true;
    bool dirInitialized = false;

    while (running_) {
        double speed = continuousSpeed_.load();

        if (speed == 0.0) {
            delayMicroseconds(1000);
            continue;
        }

        bool forward = speed > 0.0;
        double absSpeed = std::abs(speed);

        if (!dirInitialized || forward != lastDir) {
            digitalWrite(dirPin_, forward ? LOW : HIGH);
            delayMicroseconds(DIR_SETUP_US);
            lastDir = forward;
            dirInitialized = true;
        }

        unsigned int periodUs = static_cast<unsigned int>(1'000'000.0 / absSpeed);
        unsigned int delayUs  = (periodUs > PULSE_US) ? (periodUs - PULSE_US) : 1u;

        pulse();
        delayMicroseconds(delayUs);
    }
}
