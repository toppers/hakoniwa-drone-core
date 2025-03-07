#pragma once


#include "aircraft/interfaces/isensor.hpp"

namespace hako::aircraft {

class ISensorAcceleration : public ISensor {
protected:
    bool has_prev_data;
    DroneVelocityBodyFrameType prev_data;
public:
    virtual ~ISensorAcceleration() {}
    virtual void run(const DroneEulerType& euler, const DroneVelocityBodyFrameType& vel, const DroneAngularVelocityBodyFrameType& angular_rate, const DroneAccelerationBodyFrameType& data) = 0;
    virtual DroneAccelerationBodyFrameType sensor_value() = 0;
};

}

