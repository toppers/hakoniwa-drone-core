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

} // namespace hako::service