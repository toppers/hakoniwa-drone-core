#ifndef _IMAVLINK_SERVICE_HPP_
#define _IMAVLINK_SERVICE_HPP_

#include "imavlink_comm.hpp"
#include "mavlink_msg_types.hpp"
#include <iostream>
#include <memory>
#include <atomic>
#include <thread>

namespace hako::mavlink {

typedef enum {
    MAVLINK_SERVICE_IO_TYPE_TCP,
    MAVLINK_SERVICE_IO_TYPE_UDP,
    MAVLINK_SERVICE_IO_TYPE_NUM,
} MavlinkServiceIoType;

class IMavLinkService {
public:
    static IMavLinkService* create(int index, MavlinkServiceIoType io_type, const IcommEndpointType *server_endpoint, const IcommEndpointType *client_endpoint);
    virtual ~IMavLinkService() = default;

    virtual bool sendMessage(MavlinkHakoMessage& message) = 0;
    virtual bool readMessage(MavlinkHakoMessage& message, bool &is_dirty) = 0;
    virtual bool startService() = 0;
    virtual void stopService() = 0;
};

} // namespace hako::mavlink

#endif /* _IMAVLINK_SERVICE_HPP_ */