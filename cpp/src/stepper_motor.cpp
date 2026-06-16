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
    digitalWrite(stepPin_, HIGH);
    delayMicroseconds(PULSE_US);
    digitalWrite(stepPin_, LOW);
}

void StepperMotor::move(int steps, double stepsPerSecond) {
    if (steps == 0 || stepsPerSecond <= 0.0)
        return;

    digitalWrite(dirPin_, steps < 0 ? HIGH : LOW);
    delayMicroseconds(DIR_SETUP_US);

    int absSteps = std::abs(steps);
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
