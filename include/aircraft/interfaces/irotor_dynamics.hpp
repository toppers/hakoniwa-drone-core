#pragma once


#include "aircraft/interfaces/primitive_types.hpp"
#include "config/drone_config_types.hpp"
#include "iaircraft_input.hpp"

namespace hako::aircraft {


class IRotorDynamics {
public:
    virtual ~IRotorDynamics() {}

    virtual void set_aircraft_input_accessor(std::shared_ptr<IAirCraftInputAccessor> accessor) = 0;
    virtual void set_rotor_speed(DroneRotorSpeedType &rotor_speed) = 0;

    virtual DroneRotorSpeedType get_rotor_speed() const = 0;

    virtual bool has_battery_dynamics() = 0;
    virtual void set_battery_dynamics_constants(const config::RotorBatteryModelConstants &c) = 0;

    virtual double get_rad_per_sec_max() const = 0;
    virtual void reset() = 0;

    virtual void run(double control) = 0;
    virtual void run(double control, double vbat) = 0;

    virtual double get_thrust() = 0;
    virtual double get_torque(double ccw) = 0;

    virtual double get_pwm_duty_rate() = 0;
};

}
