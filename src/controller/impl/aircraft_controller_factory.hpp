#pragma once


#include "config/drone_config.hpp"
#include "iaircraft_controller.hpp"
#include <memory>

using namespace hako::config;

namespace hako::controller::impl {

extern std::shared_ptr<IAircraftController> create_aircraft_controller(int index, const DroneConfig& drone_config, bool is_param_text_base);

class AircraftControllerContainer : public IAircraftControllerContainer {
public:
    AircraftControllerContainer() = default;
    virtual ~AircraftControllerContainer() override = default;
    std::vector<std::shared_ptr<IAircraftController>>& getControllers() override {
        return controllers_;
    }
    void createAircraftControllers(config::DroneConfigManager& configManager) override {
        size_t configCount = configManager.getConfigCount();
        for (size_t i = 0; i < configCount; ++i) {
            config::DroneConfig config;
            if (configManager.getConfig(i, config)) {
                auto controller = create_aircraft_controller(static_cast<int>(i), config, false);
                if (controller == nullptr) {
                    throw std::runtime_error("Failed to create controller");
                }
                addController(controller);
            }
        }
    }
private:
    void addController(std::shared_ptr<IAircraftController> controller) {
        controllers_.push_back(std::move(controller));
    }
    std::vector<std::shared_ptr<IAircraftController>> controllers_;
};
}

