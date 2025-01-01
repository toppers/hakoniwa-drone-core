#pragma once

#include <iostream>
#include <memory>
#include <atomic>
#include <thread>
#include <functional>
#include "hako_mavlink_msgs/pdu_ctype_HakoHilSensor.h"
#include "hako_mavlink_msgs/pdu_ctype_HakoHilActuatorControls.h"
#include "hako_mavlink_msgs/pdu_ctype_HakoHilStateQuaternion.h"
#include "hako_mavlink_msgs/pdu_ctype_HakoHilGps.h"

namespace hako::mavlink {

typedef enum {
    MAVLINK_SERVICE_IO_TYPE_TCP,
    MAVLINK_SERVICE_IO_TYPE_UDP,
    MAVLINK_SERVICE_IO_TYPE_NUM,
} MavlinkServiceIoType;

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

typedef struct {
    const char *ipaddr;
    int portno;
} IMavlinkCommEndpointType;


class IMavLinkService {
public:
    static IMavLinkService* create(int index, MavlinkServiceIoType io_type, const IMavlinkCommEndpointType *server_endpoint, const IMavlinkCommEndpointType *client_endpoint);
    virtual ~IMavLinkService() = default;

    virtual bool sendMessage(MavlinkHakoMessage& message) = 0;
    virtual bool readMessage(MavlinkHakoMessage& message, bool &is_dirty) = 0;
    virtual bool startService() = 0;
    virtual void stopService() = 0;
};

class MavLinkServiceContainer {
public:
    MavLinkServiceContainer() = default;
    ~MavLinkServiceContainer() = default;
    void addService(IMavLinkService& service) {
        services_.push_back(std::ref(service));
    }
    std::vector<std::reference_wrapper<IMavLinkService>>& getServices() {
        return services_;
    }
private:
    std::vector<std::reference_wrapper<IMavLinkService>> services_;
};


} // namespace hako::mavlink
