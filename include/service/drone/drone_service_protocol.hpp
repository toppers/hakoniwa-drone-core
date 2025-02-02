#pragma once

namespace hako::service {
static inline double radian_to_degree(double radian) {
    return radian * (180.0 / M_PI);
}
typedef struct {
    double x;
    double y;
    double z;
} Vector3Type;

#define DRONE_SERVICE_MAX_ROTOR_NUM 8
typedef struct {
    int num;
    double duty_rate[DRONE_SERVICE_MAX_ROTOR_NUM];
} RotorControlType;

} // namespace hako::service