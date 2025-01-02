#pragma once

#include "comm/icomm_connector.hpp"

namespace hako::mavlink::impl {

class IMavLinkComm {
public:
    virtual ~IMavLinkComm() = default;

    virtual bool receiveMessage(::hako::comm::ICommIO* io, char* data, int datalen, int* recv_datalen) = 0;

    virtual bool sendMessage(::hako::comm::ICommIO* io, const char* data, int datalen) = 0;
};

} // namespace hako::comm


