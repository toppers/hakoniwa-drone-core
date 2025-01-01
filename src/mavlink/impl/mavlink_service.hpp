#pragma once

#include "mavlink.h"
#include "imavlink_service.hpp"
#include "icomm_connector.hpp"
#include "impl/imavlink_comm.hpp"
#include <iostream>
#include <memory>
#include <atomic>
#include <thread>

namespace hako::mavlink::impl {
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
class MavLinkService : public IMavLinkService {
public:
    explicit MavLinkService(int index, MavlinkServiceIoType io_type, const ::hako::comm::ICommEndpointType *server_endpoint, const ::hako::comm::ICommEndpointType *client_endpoint);
    virtual ~MavLinkService();

    static void init();
    static void finalize();

    virtual bool sendMessage(MavlinkHakoMessage& message) override;
    virtual bool readMessage(MavlinkHakoMessage& message, bool &is_dirty) override;
    virtual bool startService() override;
    virtual void stopService() override;

private:
    bool sendMessage(MavlinkDecodedMessage &message);
    bool sendCommandLongAck();
    void receiver();
    std::unique_ptr<::hako::comm::ICommClient> comm_client_;
    std::unique_ptr<::hako::comm::ICommServer> comm_server_;
    std::unique_ptr<IMavLinkComm> mavlink_comm_;
    std::unique_ptr<::hako::comm::ICommEndpointType> client_endpoint_;
    std::unique_ptr<::hako::comm::ICommIO> comm_io_;
    ::hako::comm::ICommEndpointType server_endpoint_;
    MavlinkServiceIoType io_type_;
    std::atomic<bool> is_service_started_;
    int index_;
    std::unique_ptr<std::thread> receiver_thread_;
    static bool is_initialized_;
};

} // namespace hako::mavlink

