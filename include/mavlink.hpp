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
#include "hako_mavlink_msgs/pdu_ctype_HakoSystemTime.h"
#include "hako_mavlink_msgs/pdu_ctype_HakoHeartbeat.h"
#include "hako_mavlink_msgs/pdu_ctype_HakoAHRS2.h"
#include "hako_mavlink_msgs/pdu_ctype_HakoSERVO_OUTPUT_RAW.h"

namespace hako::mavlink {

enum class MavlinkServiceIoType {
    TCP,
    UDP,
    NUM,
};

enum class MavLinkServiceDesitinationType {
    SITL,
    MAVPROXY,
};

enum class MavlinkMsgType {
    UNKNOWN,
    HEARTBEAT,
    LONG,
    COMMAND_ACK,
    SYSTEM_TIME,
    AHRS2,
    SERVO_OUTPUT_RAW,
    HIL_SENSOR,
    HIL_STATE_QUATERNION,
    HIL_GPS,
    HIL_ACTUATOR_CONTROLS,
    USER_CUSTOM,
    NUM,
};

#define MAVLINK_USER_CUSTOM_MAX_LEN 1024
typedef struct {
    int len;
    char data[MAVLINK_USER_CUSTOM_MAX_LEN];
} MavlinkUserCustomDataType;
typedef struct {
    MavlinkMsgType type;
    union {
        Hako_HakoSystemTime system_time;
        Hako_HakoHeartbeat heartbeat;
        Hako_HakoAHRS2 ahrs2;
        Hako_HakoSERVO_OUTPUT_RAW servo_output_raw;
        Hako_HakoHilSensor hil_sensor;
        Hako_HakoHilActuatorControls hil_actuator_controls;
        Hako_HakoHilStateQuaternion hil_state_quaternion;
        Hako_HakoHilGps hil_gps;
        MavlinkUserCustomDataType user_custom;
    } data;
} MavlinkHakoMessage;

typedef struct {
    const char *ipaddr;
    int portno;
} IMavlinkCommEndpointType;

typedef struct {
    MavlinkMsgType type;
    bool (*user_custom_decode) (int index, const void* data, int detalen, hako::mavlink::MavlinkHakoMessage& message);
} MavLinkUserCustomDecoderType;

class IMavLinkServiceCallback {
public:
    virtual void onReceiveMessage(int index) = 0;
};

class IMavLinkService {
public:
    static std::shared_ptr<IMavLinkService> create(int index, MavlinkServiceIoType io_type, const IMavlinkCommEndpointType *server_endpoint, const IMavlinkCommEndpointType *client_endpoint);
    virtual ~IMavLinkService() = default;

    virtual bool addMavProxyClient(MavlinkServiceIoType io_type, const IMavlinkCommEndpointType& mavproxy_endpoint) = 0;

    virtual bool setReceiverCallback(IMavLinkServiceCallback& callback) = 0;

    virtual bool sendMessage(MavLinkServiceDesitinationType destination, MavlinkHakoMessage& message) = 0;

    virtual bool sendMessage(MavlinkHakoMessage& message) = 0;
    virtual bool readMessage(MavlinkHakoMessage& message, bool &is_dirty) = 0;
    virtual bool startService() = 0;
    virtual void stopService() = 0;
    virtual bool setUserCustomDecoder(MavLinkUserCustomDecoderType decoder) = 0;
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
