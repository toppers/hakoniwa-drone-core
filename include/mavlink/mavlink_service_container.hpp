#ifndef _MAVLINK_SERVICE_CONTAINER_HPP_
#define _MAVLINK_SERVICE_CONTAINER_HPP_

#include "imavlink_service.hpp"
#include <functional>

namespace hako::mavlink {
class MavLinkServiceContainer {
public:
    MavLinkServiceContainer() = default;
    ~MavLinkServiceContainer() = default;
    void addService(IMavLinkService& service) {
        services_.push_back(std::ref(service));
    }
    std::vector<std::reference_wrapper<IMavLinkService>>& getServices() {
        return services_;
    }
private:
    std::vector<std::reference_wrapper<IMavLinkService>> services_;
};
} // namespace hako::mavlink

#endif /* _MAVLINK_SERVICE_CONTAINER_HPP_ */
