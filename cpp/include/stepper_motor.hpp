#pragma once

// Requires: WiringPi 3.18
// No daemon needed; gpio group membership sufficient:
//   sudo usermod -aG gpio <user>

class StepperMotor {
public:
    // stepPin / dirPin: BCM GPIO numbers
    // enablePin: active-LOW enable; pass -1 if not wired
    // microsteps: hardware-configured microstepping (1/2/4/8/16/32)
    StepperMotor(int stepPin, int dirPin, int enablePin = -1, int microsteps = 8);
    ~StepperMotor();

    void enable();
    void disable();

    // steps > 0  → forward,  steps < 0 → backward
    // stepsPerSecond: microsteps per second
    void move(int steps, double stepsPerSecond);

private:
    int stepPin_;
    int dirPin_;
    int enablePin_;
    int microsteps_;

    void pulse();
};
