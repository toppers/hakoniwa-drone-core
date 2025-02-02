#ifndef _HAKONIWA_CONDUCTOR_H_
#define _HAKONIWA_CONDUCTOR_H_

#ifdef __cplusplus
extern "C" {
#endif

extern int hakoniwa_conductor_init();
extern int hakoniwa_conductor_start_service(unsigned long long delta_time_usec, unsigned long long max_delay_usec);
extern int hakoniwa_conductor_stop_service();
extern int hakoniwa_conductor_is_started();

#ifdef __cplusplus
}
#endif

#endif /* _HAKONIWA_CONDUCTOR_H_ */