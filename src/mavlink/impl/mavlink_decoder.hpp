#ifndef _MAVLINK_DECODER_HPP_
#define _MAVLINK_DECODER_HPP_

#include <mavlink.h>
#include "impl/mavlink_service.hpp"
#include "impl/mavlink_config.hpp"

namespace hako::mavlink::impl {

extern bool mavlink_decode(uint8_t chan, const char* packet, int packet_len, mavlink_message_t *msg);
extern bool mavlink_get_message(mavlink_message_t *msg, MavlinkDecodedMessage *message);

}

#endif /* _MAVLINK_DECODER_HPP_ */
