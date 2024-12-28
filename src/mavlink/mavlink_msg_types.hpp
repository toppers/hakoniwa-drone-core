#ifndef _MAVLIN_MSG_TYPES_HPP_
#define _MAVLIN_MSG_TYPES_HPP_

#include "mavlink.h"
#include "mavlink_config.hpp"
#include "hako_mavlink_msgs/pdu_ctype_HakoHilSensor.h"
#include "hako_mavlink_msgs/pdu_ctype_HakoHilActuatorControls.h"
#include "hako_mavlink_msgs/pdu_ctype_HakoHilStateQuaternion.h"
#include "hako_mavlink_msgs/pdu_ctype_HakoHilGps.h"

typedef enum {
    MAVLINK_MSG_TYPE_UNKNOWN,
    MAVLINK_MSG_TYPE_HEARTBEAT,
    MAVLINK_MSG_TYPE_LONG,
    MAVLINK_MSG_TYPE_COMMAND_ACK,
    MAVLINK_MSG_TYPE_HIL_SENSOR,
    MAVLINK_MSG_TYPE_HIL_STATE_QUATERNION,
    MAVLINK_MSG_TYPE_SYSTEM_TIME,
    MAVLINK_MSG_TYPE_HIL_GPS,
    MAVLINK_MSG_TYPE_HIL_ACTUATOR_CONTROLS,
    MAVLINK_MSG_TYPE_NUM,
} MavlinkMsgType;

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

typedef struct {
    MavlinkMsgType type;
    union {
        Hako_HakoHilSensor hil_sensor;
        Hako_HakoHilActuatorControls hil_actuator_controls;
        Hako_HakoHilStateQuaternion hil_state_quaternion;
        Hako_HakoHilGps hil_gps;
    } data;
} MavlinkHakoMessage;


#endif /* _MAVLIN_MSG_TYPES_HPP_ */