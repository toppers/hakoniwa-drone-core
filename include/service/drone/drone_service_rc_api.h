#ifndef _DRONE_SERVICE_RC_API_H_
#define _DRONE_SERVICE_RC_API_H_

#ifdef __cplusplus
extern "C" {
#endif

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT extern
#endif

EXPORT int drone_service_rc_init(int enable_datalog, const char* drone_config_dir_path, const char* debug_logpath);
EXPORT int drone_service_rc_init_single(const char* drone_config_text, const char* controller_config_text, int logger_enable, const char* debug_logpath);
EXPORT int drone_service_set_debuff_on_collision(int index, int debuff_duration_msec);
EXPORT int drone_service_rc_start();
EXPORT int drone_service_rc_run();
EXPORT int drone_service_rc_advance_timesteps_usec(unsigned long long time_usec);
EXPORT int drone_service_rc_stop();
EXPORT int drone_service_rc_reset();

/*
 * stick operations
 */
EXPORT int drone_service_rc_put_vertical(int index, double value);
EXPORT int drone_service_rc_put_horizontal(int index, double value);
EXPORT int drone_service_rc_put_heading(int index, double value);
EXPORT int drone_service_rc_put_forward(int index, double value);
/*
 * button operations
 */
EXPORT int drone_service_rc_put_radio_control_button(int index, int value);
EXPORT int drone_service_rc_put_magnet_control_button(int index, int value);
EXPORT int drone_service_rc_put_camera_control_button(int index, int value);
EXPORT int drone_service_rc_put_home_control_button(int index, int value);
/*
 * get position and attitude
 */
EXPORT int drone_service_rc_get_position(int index, double* x, double* y, double* z);
EXPORT int drone_service_rc_get_attitude(int index, double* x, double* y, double* z);
EXPORT int drone_service_rc_get_controls(int index, double* c1, double* c2, double* c3, double* c4, double* c5, double* c6, double* c7, double* c8);

/*
 * get body velocity and angular velocity
 */
EXPORT int drone_service_rc_get_body_velocity(int index, double* x, double* y, double* z);
EXPORT int drone_service_rc_get_body_angular_velocity(int index, double* x, double* y, double* z);

/*
 * Battery
 */
EXPORT int drone_service_rc_get_battery_status(int index, double* full_voltage, double* curr_voltage, double* curr_temp, unsigned int* status, unsigned int* cycles);

/*
 * Disturbance
 */
EXPORT int drone_service_rc_put_disturbance(int index, double d_temp, double d_wind_x, double d_wind_y, double d_wind_z);

/*
 * Collision
 */
EXPORT int drone_service_rc_put_collision(int index, double contact_position_x, double contact_position_y, double contact_position_z, double restitution_coefficient);

typedef struct {
    double x;
    double y;
    double z;
} HakoVectorType;
typedef HakoVectorType HakoVelocityType;
typedef HakoVectorType HakoAngularVelocityType;
typedef HakoVectorType HakoInertiaDiagType;
EXPORT int drone_service_rc_put_impulse_by_collision(
    int index, 
    int is_target_static,
    HakoVelocityType target_velocity, 
    HakoAngularVelocityType target_angular_velocity, 
    HakoVectorType target_euler,
    HakoVectorType self_contact_vector, 
    HakoVectorType target_contact_vector, 
    HakoInertiaDiagType target_inertia,
    HakoVectorType normal,
    double target_mass, 
    double restitution_coefficient);

/*
 * miscs
 */
EXPORT unsigned long long drone_service_rc_get_time_usec(int index);

#ifdef __cplusplus
}
#endif
#endif /* _DRONE_SERVICE_RC_API_H_ */