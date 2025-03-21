#pragma once


#include "isensor.hpp"
#include "aircraft/interfaces/idrone_dynamics.hpp"

namespace hako::aircraft {

class ISensorGyro : public ISensor {
public:
    virtual ~ISensorGyro() {}
    virtual void run(const DroneAngularVelocityBodyFrameType& data) = 0;
    virtual DroneAngularVelocityBodyFrameType sensor_value() = 0;
};

}
