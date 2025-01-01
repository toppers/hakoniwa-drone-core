#pragma once

#include "mavlink.h"
#include "impl/mavlink_service.hpp"

namespace hako::mavlink::impl {
class MavlinkDump {
public:
    static void mavlink_header_dump(mavlink_message_t &msg);
    static void mavlink_message_dump(MavlinkDecodedMessage &message);
};
} // namespace hako::mavlink

