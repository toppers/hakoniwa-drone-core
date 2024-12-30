#ifndef _MAVLIN_MSG_TYPES_HPP_
#define _MAVLIN_MSG_TYPES_HPP_

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
        Hako_HakoHilSensor hil_sensor;
        Hako_HakoHilActuatorControls hil_actuator_controls;
        Hako_HakoHilStateQuaternion hil_state_quaternion;
        Hako_HakoHilGps hil_gps;
    } data;
} MavlinkHakoMessage;


#endif /* _MAVLIN_MSG_TYPES_HPP_ */
