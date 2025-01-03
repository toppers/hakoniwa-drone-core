#pragma once


#include "aircraft/iaircraft.hpp"
#include "logger/ilogger.hpp"
#include <memory>

using namespace hako::logger;

namespace hako::aircraft::impl {

class AirCraft : public IAirCraft {
private:
    std::shared_ptr<IHakoLogger> logger;
public:
    virtual ~AirCraft() 
    {
        logger->close();
    }
    void set_logger(std::shared_ptr<IHakoLogger> logger)
    {
        this->logger = logger;
    }
    void reset() override
    {
        drone_dynamics->reset();
        if (this->battery_dynamics != nullptr) {
            battery_dynamics->reset();
        }
        for (int i = 0; i < ROTOR_NUM; i++) {
            rotor_dynamics[i]->reset();
        }
        thrust_dynamis->reset();
        logger->reset();
        simulation_time_usec = 0;
    }
    void run(AircraftInputType& input) override
    {
        static const double vbat = 14.1;
        //actuators
        DroneRotorSpeedType rotor_speed[ROTOR_NUM];
        for (int i = 0; i < ROTOR_NUM; i++) {
            rotor_dynamics[i]->run(input.controls[i], vbat);
            rotor_speed[i] = rotor_dynamics[i]->get_rotor_speed();
        }
        thrust_dynamis->run(rotor_speed);
        input.thrust = thrust_dynamis->get_thrust();
        input.torque = thrust_dynamis->get_torque();
        
        drone_dynamics->run(input);
        if (input.manual.control) {
            drone_dynamics->set_angle(input.manual.angle);
        }

        //sensors
        acc->run(drone_dynamics->get_vel_body_frame());
        gyro->run(drone_dynamics->get_angular_vel_body_frame());
        gps->run(drone_dynamics->get_pos(), drone_dynamics->get_vel());
        mag->run(drone_dynamics->get_angle());
        baro->run(drone_dynamics->get_pos());

        logger->run();
        simulation_time_usec += delta_time_usec;
    }
    std::shared_ptr<IHakoLogger> get_logger()
    {
        return logger;
    }
};
}
