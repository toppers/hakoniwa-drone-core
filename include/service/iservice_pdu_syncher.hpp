#pragma once

#include "service/iservice_pdu_types.hpp"

namespace hako::service {
class IServicePduSyncher {
public:
    virtual ~IServicePduSyncher() = default;
    virtual bool flush(uint32_t index, ServicePduDataType& pdu) = 0;
    virtual bool load(uint32_t index, ServicePduDataType& pdu) = 0;
};
} // namespace hako::service

