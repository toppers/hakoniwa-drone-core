#pragma once


#include "controller/iaircraft_controller.hpp"
#include "impl/drone_controller.hpp"


namespace hako::controller::impl {
class FlightController : public IAircraftController {
public:
    FlightController(bool is_param_text_base, std::string& data);
    virtual ~FlightController() {}
    virtual bool is_radio_control() override {
        return false;
    }
    virtual void reset() override;
    virtual mi_aircraft_control_out_t run(mi_aircraft_control_in_t& in) override;
private:
    DroneController ctrl_;
};
} // namespace hako::controller::impl
