#pragma once


#include "aircraft/interfaces/primitive_types.hpp"
#include "aircraft/interfaces/idisturbance.hpp"
#include "logger/ilog.hpp"
#include "config/drone_config_types.hpp"
#include "iaircraft_input.hpp"

namespace hako::aircraft {

class IDroneDynamics: public logger::ILog {
protected:
    bool use_quaternion = false;
public:
    virtual ~IDroneDynamics() {}
    virtual void set_use_quaternion(bool use) {
        use_quaternion = use;
    }
    virtual void reset() = 0;
    virtual void set_drag(double drag1, double drag2) = 0;
    virtual double get_drag() const = 0;
    virtual void set_collision_detection(bool enable) = 0;
    virtual void set_manual_control(bool enable) = 0;
    virtual void set_body_size(double x, double y, double z) = 0;
    virtual void set_torque_constants(double cx, double cy, double cz) = 0;
    virtual void set_out_of_bounds_reset(const std::optional<config::OutOfBoundsReset>& reset_options) = 0;
    virtual void set_pos(const DronePositionType &pos) = 0;
    virtual void set_vel(const DroneVelocityType &vel) = 0;
    virtual void set_angle(const DroneEulerType &angle) = 0;
    virtual void set_rotor_radius(double radius) = 0;
    //body_boundary_disturbance_power
    virtual void set_body_boundary_disturbance_power(double power) = 0;

    virtual DronePositionType get_pos() const = 0;
    virtual DroneVelocityType get_vel() const = 0;
    virtual DroneEulerType get_angle() const = 0;

    virtual DroneVelocityType get_propeller_wind() const = 0;

    virtual DroneVelocityBodyFrameType get_vel_body_frame() const = 0;
    virtual DroneAngularVelocityBodyFrameType get_angular_vel_body_frame() const = 0;
    virtual DroneAccelerationBodyFrameType get_acc_body_frame() const = 0;
    virtual double get_mass() const = 0;
    virtual void set_mass(double mass) = 0;
    virtual bool has_collision_detection() = 0;
    virtual bool has_manual_control() = 0;

    virtual void run(const AircraftInputType &input) = 0;
};

}
