#pragma once

#include <iostream>
#include <vector>
#include <memory>
#include <atomic>
#include <thread>
#include <functional>
#include <ostream>
#include "hako_mavlink_msgs/pdu_ctype_HakoHilSensor.h"
#include "hako_mavlink_msgs/pdu_ctype_HakoHilActuatorControls.h"
#include "hako_mavlink_msgs/pdu_ctype_HakoHilStateQuaternion.h"
#include "hako_mavlink_msgs/pdu_ctype_HakoHilGps.h"

namespace hako::mavlink {

enum class MavlinkServiceIoType {
    TCP,
    UDP,
    NUM,
};

enum class MavlinkMsgType {
    UNKNOWN,
    HEARTBEAT,
    LONG,
    COMMAND_ACK,
    HIL_SENSOR,
    HIL_STATE_QUATERNION,
    SYSTEM_TIME,
    HIL_GPS,
    HIL_ACTUATOR_CONTROLS,
    NUM,
};

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
    static std::shared_ptr<IMavLinkService> create(int index, MavlinkServiceIoType io_type, const IMavlinkCommEndpointType *server_endpoint, const IMavlinkCommEndpointType *client_endpoint);
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
    void addService(std::shared_ptr<IMavLinkService> service) {
        services_.push_back(service);
    }
    std::vector<std::shared_ptr<IMavLinkService>>& getServices() {
        return services_;
    }
private:
    std::vector<std::shared_ptr<IMavLinkService>> services_;
};


} // namespace hako::mavlink
