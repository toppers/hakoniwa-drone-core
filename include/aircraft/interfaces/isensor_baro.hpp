#pragma once

#include "isensor.hpp"
#include "idrone_dynamics.hpp"

namespace hako::aircraft {

class ISensorBaro : public ISensor {
protected:
    double ref_lat = 0.0;
    double ref_lon = 0.0;
    double ref_alt = 0.0;
public:
    virtual ~ISensorBaro() {}
    virtual void init_pos(double lat_data, double lon_data, double alt_data)
    {
        this->ref_lat = lat_data;
        this->ref_lon = lon_data;
        this->ref_alt = alt_data;
    }
    virtual void run(const DronePositionType& data, const AircraftInputType& input) = 0;
#ifdef HAKO_ENABLE_SENSOR_MODEL_V2
    virtual void run(const DronePositionType& data, const DroneEulerType& angle,
                     const AircraftInputType& input)
    {
        (void)angle;
        run(data, input);
    }
    virtual double temperature_c() = 0;
    virtual double physics_pressure_atm(const DronePositionType& position,
                                        const AircraftInputType& input)
    {
        (void)position;
        (void)input;
        return sensor_value_without_noise_in_atm();
    }
#endif
    virtual DroneBarometricPressureType sensor_value() = 0;
    virtual double sensor_value_without_noise_in_atm() = 0;
};

}
