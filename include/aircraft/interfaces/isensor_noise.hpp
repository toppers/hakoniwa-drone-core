#pragma once


#include "aircraft/interfaces/primitive_types.hpp"

namespace hako::aircraft {

class ISensorNoise {
public:
    virtual ~ISensorNoise() {}
    virtual double add_random_noise(double data) = 0;
};

}

