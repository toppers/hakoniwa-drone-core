#pragma once

#include "service/iservice_pdu_types.hpp"
#include <chrono>

namespace hako::service {
class IServicePduSyncher {
public:
    virtual ~IServicePduSyncher() = default;
    virtual bool flush(uint32_t index, ServicePduDataType& pdu) = 0;
    virtual bool load(uint32_t index, ServicePduDataType& pdu) = 0;
    virtual bool reset_data() = 0;
    virtual void sync_time(uint64_t time_usec) = 0;

    // Optional simulation-clock boundary. In-process services use these NOP
    // defaults; an integration layer may expose its own clock through the same
    // object that already mediates PDU access.
    virtual bool is_time_sync_enabled() const { return false; }
    virtual uint64_t get_sync_time_usec() const { return 0; }
    virtual bool wait_until_sync_time(
        uint64_t target_time_usec,
        std::chrono::microseconds timeout)
    {
        (void)target_time_usec;
        (void)timeout;
        return true;
    }
    virtual void reset_time_sync() {}
    virtual void stop_time_sync() {}
};
} // namespace hako::service
