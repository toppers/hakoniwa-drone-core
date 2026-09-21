#pragma once

#include "primitive_types.hpp"
#include "iaircraft_input.hpp"
#include "isensor_baro.hpp"
#include "rotor_count.hpp"

#include <vector>

namespace hako::aircraft {

class IThrustDynamics {
public:
    virtual ~IThrustDynamics() {}

    virtual void set_aircraft_input_accessor(std::shared_ptr<IAirCraftInputAccessor> accessor) = 0;
    virtual void set_rotor_config(const std::vector<RotorConfigType>& rotor_config) = 0;
    virtual void set_thrust(const DroneThrustType &thrust) = 0;
    virtual void set_torque(const DroneTorqueType &torque) = 0;

    virtual DroneThrustType get_thrust() const = 0;
    virtual DroneTorqueType get_torque() const = 0;

    virtual void run(const std::vector<DroneRotorSpeedType>& rotor_speed, const AircraftInputType& input) = 0;
    virtual void reset() = 0;

};

}
