#pragma once

namespace hako::aircraft {

typedef struct {
    double value;
} mi_drone_sensor_disturbance_temperature_t;
typedef struct {
    double x;
    double y;
    double z;
} mi_drone_sensor_disturbance_wind_t;
typedef struct {
    struct {
        double x;
        double y;
        double z;
    } boundary_point;
    struct {
        double x;
        double y;
        double z;
    } boundary_normal;
} mi_drone_sensor_disturbance_boundary_t;
typedef struct {
    double sea_level_atm;
} mi_drone_sensor_disturbance_atm_t;
typedef struct {
    mi_drone_sensor_disturbance_temperature_t d_temp;
    mi_drone_sensor_disturbance_wind_t        d_wind;
    mi_drone_sensor_disturbance_boundary_t    d_boundary;
    mi_drone_sensor_disturbance_atm_t         d_atm;
} mi_drone_sensor_disturbance_t;


typedef struct {
    mi_drone_sensor_disturbance_t disturbance;
    double angular_velocity_x;
    double angular_velocity_y;
    double angular_velocity_z;
} mi_drone_sensor_gyro_in_t;

}
