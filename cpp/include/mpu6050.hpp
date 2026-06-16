#pragma once

#include <cstdint>
#include <chrono>

struct Vec3 {
    double x, y, z;
};

class MPU6050 {
public:
    enum class GyroRange  { DEG_250 = 0, DEG_500 = 1, DEG_1000 = 2, DEG_2000 = 3 };
    enum class AccelRange { G_2 = 0, G_4 = 1, G_8 = 2,  G_16 = 3 };

    // address: 0x68 (AD0 low, default) or 0x69 (AD0 high)
    explicit MPU6050(int address = 0x68);

    void init(GyroRange gyro = GyroRange::DEG_250, AccelRange accel = AccelRange::G_2);

    // Call once while robot is stationary to zero gyro drift
    void calibrate(int samples = 500);

    Vec3   readAccel();   // m/s²
    Vec3   readGyro();    // degrees/s (bias-corrected after calibrate())
    double readTemp();    // Celsius

    // Integrates gyro Z-axis. Call in a tight loop or from a timer thread.
    void   update();
    double getAngleZ()  const { return angleZ_; }
    void   resetAngleZ()      { angleZ_ = 0.0; }

private:
    int    fd_;
    double gyroScale_;
    double accelScale_;

    Vec3   gyroBias_{};
    double angleZ_ = 0.0;

    using Clock = std::chrono::steady_clock;
    Clock::time_point lastTime_{};
    bool firstUpdate_ = true;

    int16_t readRaw(int reg);
};
