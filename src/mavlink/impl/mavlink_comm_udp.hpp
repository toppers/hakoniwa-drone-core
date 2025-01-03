#pragma once

#include "imavlink_comm.hpp"
#include "mavlink_comm_message_parser.hpp"

using namespace hako::comm;
namespace hako::mavlink::impl {

class MavLinkCommUdp : public IMavLinkComm {
public:
    bool receiveMessage(ICommIO* io, char* data, int datalen, int* recv_datalen) override {
        if (!io || !data || datalen <= 0) {
            std::cerr << "Invalid arguments to receiveMessage (UDP)" << std::endl;
            return false;
        }

        int len = 0;
        if (!io->recv(data, datalen, &len)) {
            return false;
        }
        //std::cout << "len: " << len << std::endl;
        int packet_length = MavLinkCommMessageParser::getMessageLength(data);
        //std::cout << "packet_length: " << packet_length << std::endl;

        if (!MavLinkCommMessageParser::parseMessage(data, len)) {
            return false;
        }
        if (recv_datalen) {
            *recv_datalen = MAVLINK_HEADER_LEN + packet_length;
        }
        return true;
    }


    bool sendMessage(ICommIO* io, const char* data, int datalen) override {
        return io && io->send(data, datalen, nullptr);
    }
};

} // namespace hako::comm
