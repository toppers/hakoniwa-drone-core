#ifndef _DRONE_SERVICE_RC_API_H_
#define _DRONE_SERVICE_RC_API_H_

#ifdef __cplusplus
extern "C" {
#endif

extern int drone_service_rc_init(const char* drone_config_dir_path, const char* custom_json_path, int is_keyboard_control);
extern int drone_service_rc_set_pdu_id_map(int pdu_ic, int channel_id);
extern int drone_service_rc_start();
extern int drone_service_rc_run();
extern int drone_service_rc_stop();

/*
 * stick operations
 */
extern int drone_service_rc_put_vertical(int index, double value);
extern int drone_service_rc_put_horizontal(int index, double value);
extern int drone_service_rc_put_heading(int index, double value);
extern int drone_service_rc_put_forward(int index, double value);
/*
 * button operations
 */
extern int drone_service_rc_put_radio_control_button(int index, int value);
extern int drone_service_rc_put_magnet_control_button(int index, int value);
extern int drone_service_rc_put_camera_control_button(int index, int value);
extern int drone_service_rc_put_home_control_button(int index, int value);
/*
 * get position and attitude
 */
extern int drone_service_rc_get_position(int index, double* x, double* y, double* z);
extern int drone_service_rc_get_attitude(int index, double* x, double* y, double* z);

/*
 * miscs
 */
extern unsigned long long drone_service_rc_get_time_usec(int index);

#ifdef __cplusplus
}
#endif
#endif /* _DRONE_SERVICE_RC_API_H_ */