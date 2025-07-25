#pragma once

#include <memory>
#include <string>

#include "config/drone_config.hpp"
#include "controller/aircraft_controller_types.h"
#include "logger.hpp"

namespace hako::controller {

enum class AircraftControlMode {
    ATTI,
    GPS
};


struct PwmDuty {
    double d[HAKO_AIRCRAFT_MAX_ROTOR_NUM];
};


class IAircraftMixer {
public:
    virtual ~IAircraftMixer() {}
    virtual PwmDuty run(mi_aircraft_control_out_t& in) = 0;
};
class IAircraftController: public logger::ILog {
private:
    std::shared_ptr<IAircraftMixer> mixer_;
    int index_;
protected:
    std::shared_ptr<logger::IHakoLogger> logger;
public:
    virtual ~IAircraftController() {
        logger->close();
    }
    void set_logger(std::shared_ptr<logger::IHakoLogger> logger)
    {
        this->logger = logger;
    }
    virtual bool is_radio_control() = 0;
    virtual void reset() = 0;
    virtual void set_index(int index) {
        index_ = index;
    }
    virtual void set_mixer(std::unique_ptr<IAircraftMixer> mixer) {
        mixer_ = std::move(mixer);
    }
    virtual std::shared_ptr<IAircraftMixer> mixer() {
        return mixer_;
    }
    virtual mi_aircraft_control_out_t run(mi_aircraft_control_in_t& in) = 0;

    virtual void set_mode(AircraftControlMode mode) = 0;

    virtual void set_flip_control(bool enabled) = 0;

    virtual AircraftControlMode get_mode() = 0;

    virtual int get_internal_state() = 0;

    virtual bool is_flip_control_enabled() = 0;
};

class IAircraftControllerContainer {
public:
    static std::shared_ptr<IAircraftControllerContainer> create();
    virtual ~IAircraftControllerContainer() = default;
    virtual std::vector<std::shared_ptr<IAircraftController>>& getControllers() = 0;
    virtual void createAircraftControllers(config::DroneConfigManager& configManager, bool is_param_text_base) = 0;
};

}
