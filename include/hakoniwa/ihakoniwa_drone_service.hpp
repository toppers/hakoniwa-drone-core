#pragma once

#include <stdint.h>
#include <string>
#include <memory>
#include "service/iservice_container.hpp"

namespace hako::drone {
class IHakoniwaDroneService {
public:
    static std::shared_ptr<IHakoniwaDroneService> create();
    virtual ~IHakoniwaDroneService() {}

    virtual bool registerService(std::string& asset_name, std::string& config_path, uint64_t delta_time_usec, uint64_t max_delay_usec, std::shared_ptr<service::IServiceContainer> service_container, bool sync_time_only = false) = 0;
    virtual bool startService() = 0;
    virtual bool stopService() = 0;

    virtual bool isStarted() = 0;

    virtual void setPduIdMap(service::ServicePduDataIdType pdu_id, int channel_id) = 0;
};
} // namespace hako::drone

