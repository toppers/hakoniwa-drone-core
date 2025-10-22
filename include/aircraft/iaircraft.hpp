#pragma once

#include "config/drone_config.hpp"

#include "aircraft/interfaces/idrone_dynamics.hpp"
#include "aircraft/interfaces/irotor_dynamics.hpp"
#include "aircraft/interfaces/ithrust_dynamics.hpp"
#include "aircraft/interfaces/ibattery_dynamics.hpp"
#include "aircraft/interfaces/isensor_acceleration.hpp"
#include "aircraft/interfaces/isensor_baro.hpp"
#include "aircraft/interfaces/isensor_gps.hpp"
#include "aircraft/interfaces/isensor_gyro.hpp"
#include "aircraft/interfaces/isensor_mag.hpp"

#include <memory>

namespace hako::aircraft {

class IAirCraft: public IAirCraftInputAccessor, public std::enable_shared_from_this<IAirCraft> {
protected:
    bool            enable_disturbance = false;
    IDroneDynamics *drone_dynamics = nullptr;
    IRotorDynamics *rotor_dynamics[ROTOR_NUM];
    RotorConfigType rotor_config[ROTOR_NUM];
    IThrustDynamics *thrust_dynamics = nullptr;
    IBatteryDynamics *battery_dynamics = nullptr;

    ISensorAcceleration *acc = nullptr;
    ISensorBaro *baro = nullptr;
    ISensorGps *gps = nullptr;
    ISensorGyro *gyro = nullptr;
    ISensorMag *mag = nullptr;
    std::string robo_name;
    int index = 0;
    bool enable_rotor_control = false;
    double radPerSecToRPM(double rad_per_sec) {
        return rad_per_sec * (60.0 / (2 * M_PI));
    }
    uint64_t simulation_time_usec = 0;
    uint64_t delta_time_usec = 0;
    AircraftInputType* aircraft_input = nullptr;
public:
    virtual ~IAirCraft() {}
    virtual void run(AircraftInputType& input) = 0;
    virtual void reset() = 0;
    const AircraftInputType& get_input() override
    {
        if (aircraft_input == nullptr) {
            throw std::runtime_error("Aircraft input is not set. Make sure to call run() before accessing input.");
        }
        return *aircraft_input;
    }

    void set_delta_time_usec(uint64_t d_time_usec)
    {
        this->delta_time_usec = d_time_usec;
    }
    void set_rotor_config(const RotorConfigType _rotor_config[ROTOR_NUM])
    {
        for (int i = 0; i < ROTOR_NUM; i++) {
            this->rotor_config[i] = _rotor_config[i];
        }
    }
    uint64_t get_simulation_time_usec()
    {
        return simulation_time_usec;
    }
    void enable_disturb()
    {
        this->enable_disturbance = true;
    }
    bool is_enabled_disturbance()
    {
        return this->enable_disturbance;
    }
    void set_rotor_control_enabled()
    {
        enable_rotor_control = true;
    }

    bool is_rotor_control_enabled()
    {
        return enable_rotor_control;
    }
    void set_name(const std::string& name)
    {
        this->robo_name = name;
    }
    std::string get_name() const
    {
        return this->robo_name;
    }
    void set_index(int _index)
    {
        this->index = _index;
    }
    uint32_t get_index()
    {
        return this->index;
    }
    void set_drone_dynamics(IDroneDynamics *src)
    {
        this->drone_dynamics = src;
    }
    IDroneDynamics& get_drone_dynamics()
    {
        return *drone_dynamics;
    }
    void set_rotor_dynamics(IRotorDynamics *src[ROTOR_NUM])
    {
        for (int i = 0; i < ROTOR_NUM; i++) {
            this->rotor_dynamics[i] = src[i];
            this->rotor_dynamics[i]->set_aircraft_input_accessor(std::static_pointer_cast<IAirCraftInputAccessor>(shared_from_this()));
        }
    }
    void set_battery_dynamics(IBatteryDynamics *src)
    {
        this->battery_dynamics = src;
    }
    IBatteryDynamics *get_battery_dynamics()
    {
        return this->battery_dynamics;
    }
    double get_rpm_max(int rotor_index)
    {
        if (rotor_index < ROTOR_NUM) {
            return radPerSecToRPM(this->rotor_dynamics[rotor_index]->get_rad_per_sec_max());
        }
        else {
            return -1;
        }
    }
    IRotorDynamics *get_rotor_dynamics(int rotor_index)
    {
        if (rotor_index < ROTOR_NUM) {
            return this->rotor_dynamics[rotor_index];
        }
        else {
            return nullptr;
        }
    }
    void set_thrus_dynamics(IThrustDynamics *src)
    {
        this->thrust_dynamics = src;

        if (this->thrust_dynamics != nullptr) {
            this->thrust_dynamics->set_aircraft_input_accessor(std::static_pointer_cast<IAirCraftInputAccessor>(shared_from_this()));
        }
    }
    void set_acc(ISensorAcceleration *src)
    {
        this->acc = src;
        if (this->acc != nullptr) {
            this->acc->set_aircraft_input_accessor(std::static_pointer_cast<IAirCraftInputAccessor>(shared_from_this()));
        }
    }
    ISensorAcceleration& get_acc()
    {
        return *acc;
    }
    void set_gps(ISensorGps *src)
    {
        this->gps = src;
        if (this->gps != nullptr) {
            this->gps->set_aircraft_input_accessor(std::static_pointer_cast<IAirCraftInputAccessor>(shared_from_this()));
        }
    }
    ISensorGps& get_gps()
    {
        return *gps;
    }
    void set_baro(ISensorBaro *src)
    {
        this->baro = src;
        if (this->baro != nullptr) {
            this->baro->set_aircraft_input_accessor(std::static_pointer_cast<IAirCraftInputAccessor>(shared_from_this()));
        }
    }
    ISensorBaro& get_baro()
    {
        return *baro;
    }
    void set_gyro(ISensorGyro *src)
    {
        this->gyro = src;
        if (this->gyro != nullptr) {
            this->gyro->set_aircraft_input_accessor(std::static_pointer_cast<IAirCraftInputAccessor>(shared_from_this()));
        }
    }
    ISensorGyro& get_gyro()
    {
        return *gyro;
    }

    void set_mag(ISensorMag *src)
    {
        this->mag = src;
        if (this->mag != nullptr) {
            this->mag->set_aircraft_input_accessor(std::static_pointer_cast<IAirCraftInputAccessor>(shared_from_this()));
        }
    }
    ISensorMag& get_mag()
    {
        return *mag;
    }

};

class IAirCraftContainer {
public:
    static std::shared_ptr<IAirCraftContainer> create();
    virtual ~IAirCraftContainer() {}
    /*
     * create different air crafts from config directory.
     */
    virtual void createAirCrafts(config::DroneConfigManager& configManager) = 0;
    /*
     * create same air crafts from config 0.
     */
    virtual bool createSameAirCrafts(config::DroneConfigManager& configManager, int create_num) = 0;
    virtual std::shared_ptr<IAirCraft> getAirCraft(size_t index) = 0;
    virtual std::vector<std::shared_ptr<IAirCraft>> getAllAirCrafts() = 0;
};
extern std::shared_ptr<IAirCraft> create_aircraft(int index, const config::DroneConfig& drone_config);

}
