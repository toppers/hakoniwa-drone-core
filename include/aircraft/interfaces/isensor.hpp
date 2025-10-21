#pragma once

#include "primitive_types.hpp"

#include "isensor_noise.hpp"
#include "isensor_data_assembler.hpp"
#include "iaircraft_input.hpp"

namespace hako::aircraft {

class ISensor {
protected:
    ISensorNoise *noise;
    void *vendor_model;
    void *context;
    std::shared_ptr<IAirCraftInputAccessor> aircraft_input_accessor;
public:
    virtual ~ISensor() {}
    virtual void set_vendor(void *vendor, void *context)
    {
        this->vendor_model = vendor;
        this->context = context;
    }
    virtual void set_noise(ISensorNoise *n)
    {
        this->noise = n;
    }
    virtual void set_aircraft_input_accessor(std::shared_ptr<IAirCraftInputAccessor> accessor)
    {
        this->aircraft_input_accessor = accessor;
    }
};

}
