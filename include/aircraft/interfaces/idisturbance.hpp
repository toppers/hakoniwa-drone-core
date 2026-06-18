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
#define USER_DEFINED_CUSTOM_DATA_NUM 1
#define USER_DEFINED_CUSTOM_DATA_FLOAT64_NUM 1
typedef struct {
    double data[USER_DEFINED_CUSTOM_DATA_FLOAT64_NUM];
} mi_drone_sensor_disturbance_user_custom_t;

/*
 * Rotor fault injection decoded from the disturbance PDU user custom area.
 *
 * PDU contract:
 * - d_user_custom[0] is reserved for existing GPS-related custom input.
 * - d_user_custom[1], when present in the upstream variable-length disturbance PDU,
 *   is interpreted as rotor fault scales.
 * - data[k] corresponds to rotor k scale.
 * - scale 1.0 means nominal, 0.0 means fully failed, and intermediate values mean degraded thrust.
 *
 * The external PDU remains variable-length. This fixed-size struct is the
 * repository-side decoded view used by the aircraft implementation.
 */
#define MI_DRONE_DISTURBANCE_USER_CUSTOM_SLOT_GPS 0
#define MI_DRONE_DISTURBANCE_USER_CUSTOM_SLOT_ROTOR_FAULT 1
#define MI_DRONE_ROTOR_FAULT_SCALE_NUM 16
typedef struct {
    bool enabled;
    double scale[MI_DRONE_ROTOR_FAULT_SCALE_NUM];
} mi_drone_rotor_fault_injection_t;

typedef struct {
    mi_drone_sensor_disturbance_temperature_t d_temp;
    mi_drone_sensor_disturbance_wind_t        d_wind;
    mi_drone_sensor_disturbance_boundary_t    d_boundary;
    mi_drone_sensor_disturbance_atm_t         d_atm;
    mi_drone_sensor_disturbance_user_custom_t d_user_custom[USER_DEFINED_CUSTOM_DATA_NUM]; 
    mi_drone_rotor_fault_injection_t          f_rotor;
} mi_drone_sensor_disturbance_t;

typedef struct {
    mi_drone_sensor_disturbance_t disturbance;
    double angular_velocity_x;
    double angular_velocity_y;
    double angular_velocity_z;
} mi_drone_sensor_gyro_in_t;

}
