#pragma once


#include "iaircraft_controller.hpp"
#include "impl/drone_radio_controller.hpp"

namespace hako::controller::impl {
class RadioController : public IAircraftController {
public:
    RadioController(bool is_param_text_base, std::string& data);
    virtual ~RadioController() {}
    virtual bool is_radio_control() override {
        return true;
    }
    virtual void reset() override;
    virtual mi_aircraft_control_out_t run(mi_aircraft_control_in_t& in) override;
private:
    DroneRadioController ctrl_;
};
} // namespace hako::controller::impl

