#ifndef _MAVLINK_ENCODER_HPP_
#define _MAVLINK_ENCODER_HPP_

#include <mavlink.h>
#include "impl/mavlink_service.hpp"
#include "impl/mavlink_config.hpp"

namespace hako::mavlink::impl
{

extern int mavlink_get_packet(char* packet, int packet_len, const mavlink_message_t *msg);
extern bool mavlink_encode_message(int index, mavlink_message_t *msg, const MavlinkDecodedMessage *message);
}

#endif /* _MAVLINK_ENCODER_HPP_ */
