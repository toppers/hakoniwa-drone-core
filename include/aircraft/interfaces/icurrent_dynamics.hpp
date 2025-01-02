#pragma once



namespace hako::aircraft {

class ICurrentDynamics {
public:
    virtual ~ICurrentDynamics() {};
    
    // return value Unit: [A]
    virtual double get_current() = 0;
};
}

