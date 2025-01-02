#include "impl/flight_controller/flight_controller.hpp"
#include <algorithm>
#include <iostream>

using namespace hako::controller::impl;

FlightController::FlightController(bool is_param_text_base, std::string& data) :
    ctrl_(is_param_text_base, data)
{
    std::cout << "FlightController::FlightController()" << std::endl;
    ctrl_.reset();
}

void FlightController::reset()
{
    ctrl_.reset();
}

mi_aircraft_control_out_t FlightController::run(mi_aircraft_control_in_t& in)
{
    mi_aircraft_control_out_t out = {};

    FlightControllerInputEulerType euler = {in.euler_x, in.euler_y, in.euler_z};
    FlightControllerInputPositionType pos = {in.pos_x, in.pos_y, -in.pos_z};
    FlightControllerInputVelocityType velocity = {in.u, in.v, -in.w};
    FlightControllerInputAngularRateType angular_rate = {in.p, in.q, in.r};

    /*
     * target values are set on NED coordinate system
     * Z-axis is inverted for better understanding
     */
    double target_pos_x    =  in.target_pos_x;
    double target_pos_y    =  in.target_pos_y;
    double target_pos_z    = -in.target_pos_z;
    double target_velocity =  in.target_velocity;
    double target_angle    =  in.target_yaw_deg;

    /*
     * altitude control
     */
    DroneAltInputType alt_in(pos, velocity, target_pos_z);
    DroneAltOutputType alt_out = ctrl_.alt->run(alt_in);
    /*
     * angle control
     */
    DroneHeadingControlInputType head_in(euler, target_angle);
    DroneHeadingControlOutputType head_out = ctrl_.head->run(head_in);
    /*
     * position control
     */
    DronePosInputType pos_in(pos, velocity, euler, target_pos_x, target_pos_y, target_velocity);
    DronePosOutputType pos_out = ctrl_.pos->run(pos_in);
    /*
     * angular rate control
     */
    DroneAngleInputType angle_in(euler, angular_rate, pos_out.target_roll, pos_out.target_pitch, head_out.target_yaw_rate);
    DroneAngleOutputType angle_out = ctrl_.angle->run(angle_in);
    /*
     * output
     */
    out.mass = in.mass;
    out.thrust = alt_out.thrust;
    out.torque_x = angle_out.p;
    out.torque_y = angle_out.q;
    out.torque_z = angle_out.r;
    return out;
}


