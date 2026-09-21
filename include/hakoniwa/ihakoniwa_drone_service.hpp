#pragma once

#include <stdint.h>
#include <limits>
#include <stdexcept>
#include <string>
#include <memory>
#include "service/iservice_container.hpp"

namespace hako::drone {
class IHakoniwaDroneService {
public:
    static std::shared_ptr<IHakoniwaDroneService> create();
    virtual ~IHakoniwaDroneService() {}

    virtual bool registerService(
        std::string& asset_name,
        std::string& config_path,
        uint64_t delta_time_usec,
        uint64_t max_delay_usec,
        std::shared_ptr<service::IServiceContainer> service_container,
        bool sync_time_only = false,
        bool disable_conductor = false) = 0;
    virtual bool startService() = 0;
    virtual bool stopService() = 0;

    virtual bool isStarted() = 0;
    virtual void setRealSleepMsec(uint32_t sleep_msec) = 0;

    virtual void setPduIdMap(service::ServicePduDataIdType pdu_id, int channel_id) = 0;

    // Appended with a compatibility fallback so existing source-level
    // implementations that only support millisecond pacing remain valid.
    virtual void setRealSleepUsec(uint64_t sleep_usec)
    {
        if ((sleep_usec % 1000) != 0
            || (sleep_usec / 1000) > std::numeric_limits<uint32_t>::max()) {
            throw std::invalid_argument(
                "This Hakoniwa service implementation only supports whole-millisecond sleep");
        }
        setRealSleepMsec(static_cast<uint32_t>(sleep_usec / 1000));
    }
};
} // namespace hako::drone
