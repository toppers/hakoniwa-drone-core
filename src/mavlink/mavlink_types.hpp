#ifndef _MAVLINK_TYPES_HPP_
#define _MAVLINK_TYPES_HPP_

#include "mavlink.h"
#include "mavlink/mavlink_msg_types.hpp"

typedef struct {
    MavlinkMsgType type;
    union {
        mavlink_heartbeat_t heartbeat;
        mavlink_command_long_t command_long;
        mavlink_command_ack_t command_ack;
        mavlink_hil_sensor_t hil_sensor;
        mavlink_hil_state_quaternion_t hil_state_quaternion;
        mavlink_system_time_t system_time;
        mavlink_hil_gps_t hil_gps;
        mavlink_hil_actuator_controls_t hil_actuator_controls;
    } data;
} MavlinkDecodedMessage;


#endif /* _MAVLINK_TYPES_HPP_ */