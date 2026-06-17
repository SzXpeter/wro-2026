#pragma once

#include <atomic>
#include <thread>

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

    // Continuous pulsing on a background thread.
    // setContinuousSpeed() is safe to call from any thread at any time:
    //   positive → forward, negative → backward, 0 → idle (thread keeps running)
    void startContinuous(double stepsPerSecond);
    void stopContinuous();
    void setContinuousSpeed(double stepsPerSecond);

    long getStepCount() const;
    void resetStepCount();

private:
    int stepPin_;
    int dirPin_;
    int enablePin_;
    int microsteps_;

    std::atomic<double> continuousSpeed_{0.0};
    std::atomic<bool>   running_{false};
    std::atomic<long>   stepCount_{0};
    std::thread         continuousThread_;

    void pulse();
    void continuousLoop();
};
