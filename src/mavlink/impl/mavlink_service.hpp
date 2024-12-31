#ifndef _MAVLINK_SERVICE_HPP_
#define _MAVLINK_SERVICE_HPP_

#include "mavlink_types.hpp"
#include "imavlink_service.hpp"
#include "impl/imavlink_comm.hpp"
#include <iostream>
#include <memory>
#include <atomic>
#include <thread>

namespace hako::mavlink {

class MavLinkService : public IMavLinkService {
public:
    explicit MavLinkService(int index, MavlinkServiceIoType io_type, const IcommEndpointType *server_endpoint, const IcommEndpointType *client_endpoint);
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
    std::unique_ptr<hako::comm::ICommClient> comm_client_;
    std::unique_ptr<hako::comm::ICommServer> comm_server_;
    std::unique_ptr<hako::mavlink::IMavLinkComm> mavlink_comm_;
    std::unique_ptr<IcommEndpointType> client_endpoint_;
    std::unique_ptr<ICommIO> comm_io_;
    IcommEndpointType server_endpoint_;
    MavlinkServiceIoType io_type_;
    std::atomic<bool> is_service_started_;
    int index_;
    std::unique_ptr<std::thread> receiver_thread_;
    static bool is_initialized_;
};

} // namespace hako::mavlink

#endif /* _MAVLINK_SERVICE_HPP_ */
