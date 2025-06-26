#pragma once

#include "primitive_types.hpp"
#include "isensor_baro.hpp"

namespace hako::aircraft {

const int ROTOR_NUM = 4;

class IThrustDynamics {
public:
    virtual ~IThrustDynamics() {}

    virtual void set_rotor_config(const RotorConfigType rotor_config[ROTOR_NUM]) = 0;
    virtual void set_thrust(const DroneThrustType &thrust) = 0;
    virtual void set_torque(const DroneTorqueType &torque) = 0;

    virtual DroneThrustType get_thrust() const = 0;
    virtual DroneTorqueType get_torque() const = 0;

    virtual void run(const DroneRotorSpeedType rotor_speed[ROTOR_NUM], const AircraftInputType& input) = 0;
    virtual void reset() = 0;

};

}
