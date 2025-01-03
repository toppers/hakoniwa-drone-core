#pragma once

#include "isensor.hpp"

namespace hako::aircraft {

class ISensorGps : public ISensor {
protected:
    double ref_lat;
    double ref_lon;
    double ref_alt;
public:
    virtual ~ISensorGps() {}
    virtual void init_pos(double lat_data, double lon_data, double alt_data)
    {
        this->ref_lat = lat_data;
        this->ref_lon = lon_data;
        this->ref_alt = alt_data;
    }
    virtual void run(const DronePositionType& p, const DroneVelocityType& v) = 0;
    virtual DroneGpsDataType sensor_value() = 0;
};

}
