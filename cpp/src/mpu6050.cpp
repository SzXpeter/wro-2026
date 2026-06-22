#include "mpu6050.hpp"
#include <wiringPiI2C.h>
#include <stdexcept>
#include <thread>

// MPU6050 register map
namespace Reg {
    constexpr int SMPLRT_DIV   = 0x19;
    constexpr int CONFIG        = 0x1A;
    constexpr int GYRO_CONFIG   = 0x1B;
    constexpr int ACCEL_CONFIG  = 0x1C;
    constexpr int ACCEL_XOUT_H  = 0x3B;
    constexpr int TEMP_OUT_H    = 0x41;
    constexpr int GYRO_XOUT_H   = 0x43;
    constexpr int PWR_MGMT_1    = 0x6B;
}

// LSB sensitivities per datasheet
static constexpr double GYRO_SCALE[]  = { 131.0, 65.5, 32.8, 16.4 };
static constexpr double ACCEL_SCALE[] = { 16384.0, 8192.0, 4096.0, 2048.0 };
static constexpr double GRAVITY       = 9.80665;

MPU6050::MPU6050(int address) : fd_(wiringPiI2CSetup(address)), gyroScale_(GYRO_SCALE[0]), accelScale_(ACCEL_SCALE[0]) {
    if (fd_ < 0)
        throw std::runtime_error("MPU6050: I2C setup failed (address 0x" + std::to_string(address) + ")");
}

void MPU6050::init(GyroRange gyro, AccelRange accel) {
    // Wake up (clear sleep bit)
    wiringPiI2CWriteReg8(fd_, Reg::PWR_MGMT_1, 0x00);

    // 1 kHz sample rate
    wiringPiI2CWriteReg8(fd_, Reg::SMPLRT_DIV, 0x00);

    // DLPF: ~94 Hz bandwidth
    wiringPiI2CWriteReg8(fd_, Reg::CONFIG, 0x02);

    wiringPiI2CWriteReg8(fd_, Reg::GYRO_CONFIG,  static_cast<int>(gyro)  << 3);
    wiringPiI2CWriteReg8(fd_, Reg::ACCEL_CONFIG, static_cast<int>(accel) << 3);

    gyroScale_  = GYRO_SCALE [static_cast<int>(gyro)];
    accelScale_ = ACCEL_SCALE[static_cast<int>(accel)];
}

void MPU6050::calibrate(int samples) {
    Vec3 sum{};
    for (int i = 0; i < samples; ++i) {
        int16_t gx = readRaw(Reg::GYRO_XOUT_H);
        int16_t gy = readRaw(Reg::GYRO_XOUT_H + 2);
        int16_t gz = readRaw(Reg::GYRO_XOUT_H + 4);
        sum.x += gx;
        sum.y += gy;
        sum.z += gz;
        std::this_thread::sleep_for(std::chrono::microseconds(1250));
    }
    gyroBias_.x = sum.x / samples;
    gyroBias_.y = sum.y / samples;
    gyroBias_.z = sum.z / samples;
}

Vec3 MPU6050::readAccel() {
    return {
        readRaw(Reg::ACCEL_XOUT_H)     / accelScale_ * GRAVITY,
        readRaw(Reg::ACCEL_XOUT_H + 2) / accelScale_ * GRAVITY,
        readRaw(Reg::ACCEL_XOUT_H + 4) / accelScale_ * GRAVITY,
    };
}

Vec3 MPU6050::readGyro() {
    return {
        (readRaw(Reg::GYRO_XOUT_H)     - gyroBias_.x) / gyroScale_,
        (readRaw(Reg::GYRO_XOUT_H + 2) - gyroBias_.y) / gyroScale_,
        (readRaw(Reg::GYRO_XOUT_H + 4) - gyroBias_.z) / gyroScale_,
    };
}

double MPU6050::readTemp() {
    return readRaw(Reg::TEMP_OUT_H) / 340.0 + 36.53;
}

void MPU6050::update() {
    auto now = Clock::now();
    if (firstUpdate_) {
        lastTime_   = now;
        firstUpdate_ = false;
        return;
    }
    double dt = std::chrono::duration<double>(now - lastTime_).count();
    lastTime_ = now;

    double gx = -(readRaw(Reg::GYRO_XOUT_H + 2) - gyroBias_.y) / gyroScale_;
    angleX_ += gx * dt;
}

int16_t MPU6050::readRaw(int reg) {
    int high = wiringPiI2CReadReg8(fd_, reg);
    int low  = wiringPiI2CReadReg8(fd_, reg + 1);
    return static_cast<int16_t>((high << 8) | low);
}
