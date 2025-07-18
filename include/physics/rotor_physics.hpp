#pragma once
#include "drone_frames.hpp"

namespace hako::drone_physics {

/**
 * These functions are rotor dynamics.
 * Treats the rotor as a single unit.
 */

/* The rotor dynamics modeled as a first-order lag system. eq.(2.48) */
double rotor_omega_acceleration( /* omega acceleration in [rad/s^2]*/
    double Kr, /* gain constant in */
    double Tr, /* time constant */
    double omega, /* angular velocity in [rad/s] */
    double duty_rate /* 0.0-1.0 (ratio of PWM) */ );

/* realistic model for rotor */
double rotor_omega_acceleration( /* omega acceleration in [rad/s^2]*/
    double Vbat, /* battery voltage in volt [V]*/
    double R, /* resistance in ohm [V/A] */
    double Cq, /* torque coeff (= B param in anti-torque) [N ms^2/rad^2] */
    double J, /* propeller inertia in [kg m^2] */
    double K, /* back electromotive force coeff in [N m/A] */
    double D, /* Kinematic viscosity coefficient [Nms/rad] */
    double omega, /* angular velocity in [rad/s] */
    double duty_rate /* 0.0-1.0 (ratio of PWM) */);

/* current in the rotor */
double rotor_current(  /* current in [A] */
    double Vbat, /* battery voltage in volt [V]*/
    double R, /* resistance in ohm [V/A] */
    double K, /* back electromotive force coeff in [N m/A] */
    double omega, /* angular velocity in [rad/sec] */
    double duty_rate /* 0.0-1.0 (ratio of PWM) */);

/* thrust from omega in radian/sec eq.(2.50)*/
double rotor_thrust( /* thrust in [N] */
    double Ct, /* thrust coeff, in Trust = Ct*(Omega)^2 (referred to as 'A' in Nonami's book ) in [N s^2/rad^2]*/
    double omega /* in [rad/s] */,
    double atm_pressure = 1.0 /* atmospheric pressure in [atm] */ );

/* this makes z-axis rotation eq.(2.56) */
double rotor_anti_torque( /* anti torque(z-axis) in [Nm]*/
    double Cq, /* torque coefficient (referred to as B in nonami's book in [N m s^2/rad^2] */
    double J, /* innertia of propeller [kg m^2] */
    double omega, /* in [rad/s] */
    double omega_acceleratoin, /* in [rad/s^2] */
    double ccw /* 1 or -1 */ );

/**
 * These functions are body dynamics.
 * Treats one body with multiple rotors.
 */

/* the sum of the n trust from the rotors eq.(2.61) */
double body_thrust( /* thrust in [N] */
    double Ct, /* thrust coeff, in Trust = Ct*(Omega)^2 (referred to as 'A' in Nonami's book ) in [N s^2/rad^2] */
    unsigned n, /* number of rotors */
    const double omega[], /* in radian/sec */
    double atm_pressure = 1.0 /* atmospheric pressure in [atm] */ );

/* the sum of the n torques from the rotors including anti-torque */
/* eq.(2.60)-(2.62)*/
TorqueType body_torque( /* torque in [Nm] */
    double Ct, /* thrust coeff, in Trust = Ct*(Omega)^2 (referred to as 'A' in Nonami's book ) in [N s^2/rad^2] */
    double Cq, /* torque coefficient (referred to as B in nonami's book in [N m s^2/rad^2] */
    double Jr, /* torque coefficient for 2nd order rotation */
    unsigned n, /* number of rotors */
    const VectorType position[], /* position of each rotor in [m] */
    const double ccw[], /* 1 or -1 */
    const double omega[], /* in [rad/s] */
    const double omega_acceleration[], /* in [rad/s^2] */
    double atm_pressure = 1.0 /* atmospheric pressure in [atm] */  );


/**
 * Linear approximation versions
 * used in jMAVsim implemntation.
 * Used in comparing with the non-linear(our) model.
 */
double rotor_thrust_linear(double Ct2, double omega);
double rotor_anti_torque_linear(double Cq2, double omega, double ccw);
TorqueType body_torque_linear(double Ct2, double Cq2, unsigned n,
    const VectorType position[], const double ccw[], const double omega[]);
double body_thrust_linear(double Ct2, unsigned n, const double omega[]);

/**
 * Atmospheric pressure at the altitude.
 * Returns the atmospheric pressure at the altitude in [atm]. 1 atm is 1013.25 hPa.
 */
double atmospheric_pressure(double sea_level_atm, /* atmospheric pressure at sea level in [atm] */
                            double altitude_from_sea, /* altitude from sea level in [m] */
                            double ground_temperature); /* ground temperature in [degree celsius] */

} /* namespace hako::drone_physics */