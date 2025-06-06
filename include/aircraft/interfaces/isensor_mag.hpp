#pragma once

#include "isensor.hpp"

namespace hako::aircraft {

class ISensorMag : public ISensor {
protected:
    double params_F;
    double params_I;
    double params_D;
public:
    virtual ~ISensorMag() {}
    virtual void set_params(double f, double i, double d)
    {
        this->params_F = f;
        this->params_I = i;
        this->params_D = d;
    }
    virtual void run(const DroneEulerType& angle) = 0;
    virtual DroneMagDataType sensor_value() = 0;
};

}
