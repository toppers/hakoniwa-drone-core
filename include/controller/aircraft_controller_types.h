#ifndef _AIRCRAFT_CONTROLLER_TYPES_H_
#define _AIRCRAFT_CONTROLLER_TYPES_H_

typedef struct {
    double roll;
    double pitch;
} mi_aircraft_control_in_attitude_t;
typedef struct {
    // NOTE: For radio control, a negative value indicates upward movement.
    double power;
} mi_aircraft_control_in_throttle_t;
typedef struct {
    double r;
} mi_aircraft_control_in_direction_velocity_t;

typedef struct {
    double x;
    double y;
    double z;
} mi_aircraft_control_in_position_t;
typedef struct {
    double height;
} mi_aircraft_control_in_altitude_t;
typedef struct {
    /*
     * Flight/API target values.
     *
     * Do not use direction_velocity.r for target yaw; that field is the
     * radio-control yaw stick / yaw-rate command.
     */
    double yaw_deg;
    double speed_m_s;
} mi_aircraft_control_in_flight_target_t;

#define HAKO_AIRCRAFT_MAX_ROTOR_NUM    16

typedef struct {
    int radio_control; /* 0: off, 1: on */
    /*
     * Radio control
     */
    mi_aircraft_control_in_attitude_t attitude;
    mi_aircraft_control_in_throttle_t throttle;
    mi_aircraft_control_in_direction_velocity_t direction_velocity;
    /*
     * Position control
     */
    mi_aircraft_control_in_position_t position;
    mi_aircraft_control_in_altitude_t altitude;
    mi_aircraft_control_in_flight_target_t flight;
} mi_aircraft_control_in_target_t;

typedef struct {
    /*
     * Control information
     */
    mi_aircraft_control_in_target_t target;

    /*
     * Drone's state
     */
    double mass;
    double drag;
    double max_rpm;
    //position
    double pos_x;
    double pos_y;
    double pos_z;
    //angle: body FRD attitude with respect to local NED [rad]
    double euler_x; /* roll / phi */
    double euler_y; /* pitch / theta */
    double euler_z; /* yaw / psi */
    // velocity
    double u; /* velocity x in body frame */
    double v; /* velocity y in body frame */
    double w; /* velocity z in body frame */
    // acceleration
    double ax; /* acceleration x in world frame (NED), [m/s^2] */
    double ay; /* acceleration y in world frame (NED), [m/s^2] */
    double az; /* acceleration z in world frame (NED), [m/s^2] */
    // angular velocity: body FRD components [rad/s]
    // NOTE: p/q/r are not Euler angle derivatives.
    double p; /* angular velocity about body +X (Forward) */
    double q; /* angular velocity about body +Y (Right) */
    double r; /* angular velocity about body +Z (Down) */
    // angular acceleration
    double p_dot; /* angular acceleration x in body frame (FRD), [rad/s^2] */
    double q_dot; /* angular acceleration y in body frame (FRD), [rad/s^2] */
    double r_dot; /* angular acceleration z in body frame (FRD), [rad/s^2] */
} mi_aircraft_control_in_t;

static inline void mi_aircraft_control_in_set_radio_control(
    mi_aircraft_control_in_t* in,
    int radio_control)
{
    in->target.radio_control = radio_control;
}

static inline int mi_aircraft_control_in_get_radio_control(
    const mi_aircraft_control_in_t* in)
{
    return in->target.radio_control;
}

static inline void mi_aircraft_control_in_set_flight_target(
    mi_aircraft_control_in_t* in,
    double target_pos_x,
    double target_pos_y,
    double target_pos_z,
    double target_velocity,
    double target_yaw_deg)
{
    in->target.position.x = target_pos_x;
    in->target.position.y = target_pos_y;
    in->target.position.z = target_pos_z;
    in->target.altitude.height = -target_pos_z;
    in->target.flight.speed_m_s = target_velocity;
    in->target.flight.yaw_deg = target_yaw_deg;
}

static inline double mi_aircraft_control_in_get_target_pos_x(
    const mi_aircraft_control_in_t* in)
{
    return in->target.position.x;
}

static inline double mi_aircraft_control_in_get_target_pos_y(
    const mi_aircraft_control_in_t* in)
{
    return in->target.position.y;
}

static inline double mi_aircraft_control_in_get_target_pos_z(
    const mi_aircraft_control_in_t* in)
{
    return in->target.position.z;
}

static inline double mi_aircraft_control_in_get_target_velocity(
    const mi_aircraft_control_in_t* in)
{
    return in->target.flight.speed_m_s;
}

static inline double mi_aircraft_control_in_get_target_yaw_deg(
    const mi_aircraft_control_in_t* in)
{
    return in->target.flight.yaw_deg;
}

typedef struct {
    // Current body FRD attitude with respect to local NED [rad].
    double roll_rad;
    double pitch_rad;
    double yaw_rad;
} mi_aircraft_control_current_attitude_t;

typedef struct {
    // Current angular velocity expressed in body FRD [rad/s].
    // p/q/r are body-axis rates, not roll_dot/pitch_dot/yaw_dot.
    double p;
    double q;
    double r;
} mi_aircraft_control_current_angular_rate_t;

typedef struct {
    mi_aircraft_control_current_attitude_t attitude;
    mi_aircraft_control_current_angular_rate_t angular_rate;
} mi_aircraft_control_current_state_t;

typedef struct {
    double mass;
    double thrust;
    double torque_x;
    double torque_y;
    double torque_z;

    /*
     * Current-state snapshot for the downstream mixer / allocation boundary.
     * These values are metadata for state-dependent allocation and do not
     * change the meaning of thrust / torque above.
     */
    mi_aircraft_control_current_state_t current_state;
} mi_aircraft_control_out_t;

static inline void mi_aircraft_control_out_set_current_state(
    mi_aircraft_control_out_t* out,
    const mi_aircraft_control_in_t* in)
{
    out->current_state.attitude.roll_rad = in->euler_x;
    out->current_state.attitude.pitch_rad = in->euler_y;
    out->current_state.attitude.yaw_rad = in->euler_z;
    out->current_state.angular_rate.p = in->p;
    out->current_state.angular_rate.q = in->q;
    out->current_state.angular_rate.r = in->r;
}


#endif /* _AIRCRAFT_CONTROLLER_TYPES_H_ */
