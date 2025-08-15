#pragma once
#include "drone_frames.hpp"

namespace hako::drone_physics {

typedef VectorType ImpulseType;
typedef VectorType InertiaDiagType;

/*
 *  Maths for anglular velocity and euler rate.
 */
/* translations between anguler vector and euler rate */
EulerRateType euler_rate_from_body_angular_velocity(
    const AngularVelocityType& angular_veleocy,
    const EulerType& euler);
AngularVelocityType body_angular_velocity_from_euler_rate(
    const EulerRateType& euler_rate,
    const EulerType& euler);

/*
 *  Dynamics(differential quuations) for accelertion from force and torque.
 */
AccelerationType acceleration_in_ground_frame(
    const VelocityType& ground,
    const EulerType& angle,
    double thrust, double mass /* 0 is not allowed */,
    double gravity, /* usually 9.8 > 0*/
    double drag1,   /* air friction of 1-st order(-d1*v) counter to velocity */
    double drag2 = 0.0 /* air friction of 2-nd order(-d2*v*v) counter to velocity */);

/* The translation dynamics. drags are vectors in the three directions */
AccelerationType acceleration_in_body_frame(
    const VelocityType& body_velocity,
    const EulerType& angle,
    const AngularVelocityType& body_angular_velocity, /* for Coriolis */
    double thrust, double mass, /* 0 is not allowed */
    double gravity, /* usually 9.8 > 0*/
    const VectorType& wind, /* wind vector in body frame */
    const VectorType& drag1,   /* air friction of 1-st order(-d1*v) counter to velocity */
    const VectorType& drag2  /* air friction of 2-nd order(-d2*v*v) counter to velocity */);

/* simplified version of the above */
AccelerationType acceleration_in_body_frame(
    const VelocityType& body_velocity,
    const EulerType& angle,
    const AngularVelocityType& body_angular_velocity,
    double thrust, double mass /* 0 is not allowed */,
    double gravity, /* usually 9.8 > 0*/
    double drag1,  /* air friction of 1-st order(-d1*v) counter to velocity */
    double drag2 = 0 /* air friction of 2-nd order(-d2*v*v) counter to velocity */);


/* angular acceleration in body frame based on JW' = W x JW =Tb ...eq.(1.137),(2.31) */
AngularAccelerationType
angular_acceleration_in_body_frame(
    const AngularVelocityType& body_angular_velocity,
    const TorqueType& torque, /* in body frame */
    const InertiaDiagType& I /* in body frame */);

/* euler angle acceleration(dd phi, dd theta, dd psi) */
EulerAccelerationType
euler_acceleration_in_ground_frame(
    const EulerRateType& current_euler_rate,
    const EulerType& current_euler,
    const TorqueType& torque, /* in BODY FRAME!! */
    const InertiaDiagType& I /* in BODY FRAME!! */);

/* Quaternion velocity(dq/dt) from body angllar velocity */
QuaternionVelocityType quaternion_velocity_from_body_angular_velocity(
    const AngularVelocityType& body_angular_velocity,
    const QuaternionType& quaternion);

/* Quaternion from euler angle */
QuaternionType quaternion_from_euler(const EulerType& euler);

/* Euler angle from Quaternion */
EulerType euler_from_quaternion(const QuaternionType& quaternion);

/**
 * Physics for collision with wall(walls don't move).
 * Calculates the velocity after the collision.
 * Input vectors in the same frame, return vector in the same frame.
*/
VelocityType velocity_after_contact_with_wall(
    const VelocityType& velocity_before_contact,
    const VectorType& normal_vector,  /* of the wall, will be normalized internally */
    double restitution_coefficient /* 0.0 - 1.0 */);

VelocityType velocity_after_contact_with_wall(
    const VelocityType& velocity_before_contact,
    const VectorType& center_position,
    const VectorType& contact_position,
    double restitution_coefficient /* 0.0 - 1.0 */);

/**
 * Impulse by collision. See 
 * https://github.com/hakoniwalab/hakoniwa-drone-pro/blob/main/src/physics/Collision.md
 * https://qiita.com/kenjihiranabe/items/f4acad92ebeda3334d03
 * for the meaning of the parameters below and other math details.
 * 
 * Impulse =defined= F * delta_t(Rikiseki in Japanese)
 * 1. mv' - mv = impulse (= delta momentum)
 * 2. v' - v = impulse/m (= delta velocity)
 * 3. Force = impulse/delta_t
 * 4. Acceleration = imuplse/(delta_t * m)
 * 5. Iw' - Iw = impulse x r (= delta angular momentum)
 * 6. w' - w = I^{-1} (impluse x r) (= delta angular velocity)
 **/
ImpulseType impulse_by_collision(/* coordicates are ALL in one frame, self body frame recommened */
    const VelocityType& self_velocity, /* self velocity */
    const AngularVelocityType& self_angular_velocity, /* self angular velocity */
    const EulerType& self_euler, /* {0,0,0} if you use self body frame(recommended) */
    const VelocityType& target_velocity, /* target velocity */
    const AngularVelocityType& target_angular_velocity, /* target angular velocity */
    const EulerType& target_euler,
    const VectorType& self_contact, /* self contact vector, from self center to contact = contact_point - center_point in body frame */
    const VectorType& target_contact, /* vector from target center to contact = contact_point - other_center_point in body frame */
    double self_mass,
    double target_mass,
    const InertiaDiagType& self_inertia, /* diagonal elements of the inertia tensor of the self in self body frame(euler) */
    const InertiaDiagType& target_inertia, /* diagonal elements of the inertia tensor of the target in target body frame(euler) */
    const VectorType& normal, /* normal vector of the contact surface (n and -n give the same result, don't care the +/- direction) */
    double restitution_coefficient /* 0.0-1.0*/);

ImpulseType impulse_by_collision(
    const VelocityType& self_velocity,
    const AngularVelocityType& self_angular_velocity,
    const EulerType& self_euler, /* {0,0,0} if you use self body frame(recommended) */
    const VelocityType& target_velocity, /* other velocity(at contact point including rotation w x r) in self body frame */
    const VectorType& self_contact,
    double self_mass,
    const InertiaDiagType& self_inertia,
    const VectorType& normal,
    double restitution_coefficient);


/* delta_v = v' - v (this will be added to the current velocity) */
inline VelocityType delta_velocity_from_impulse(
    const ImpulseType& impulse, double mass) { return impulse/mass;}

/* acceleration = dv/dt (this will be integrated with time to make vector) */
inline AccelerationType acceleration_from_impulse(
    const ImpulseType& impulse,
    double mass, double delta_time) { return impulse/(mass*delta_time); }

/* force to the object */
inline ForceType force_from_impulse(
    const ImpulseType& impulse, double delta_time) { return impulse/delta_time; }

inline AngularVelocityType delta_angular_velocity_from_impulse(
    const ImpulseType& impulse,
    const VectorType& r1,
    const InertiaDiagType& I1) {
        auto torque = cross(r1, impulse);
        return {torque.x /= I1.x, torque.y /= I1.y, torque.z /= I1.z };
    }

inline AngularAccelerationType angular_acceleration_from_impulse(
    const ImpulseType& impulse,
    const VectorType& r1,
    const InertiaDiagType& I1, double delta_time) {
        return delta_angular_velocity_from_impulse(impulse, r1, I1)/delta_time;
    }

inline TorqueType torque_from_impulse(
    const ImpulseType& impulse,
    const VectorType& r1,
    double delta_time) { return cross(r1, impulse)/delta_time; }

/**
 * Physics for boundary disturbance.
 * Boundaries are;
 * - ground(lower bottom)
 * - ceilings(upper bottom)
 * - walls(any surfaces).
 * The aboves are treated as infinite planes, and treated uniformly by the
 * dot product with the normal vector.
 *
 * The wind from the rotors reflects on the boundary,
 * and makes the disturbance force rational to its thrust.
 * Coordinates should be in the ground.
 * 
 * This implementation is based on the mirror reflection of rotors about the boundary.
 * The thrust*ratio comes from the reflection, ratio is reduced by the distance from the boundary.
 *
 * There is a wind disturbance version below from the force calculated here.
 */
ForceType boundary_disturbance(
    const VectorType& position, /* drone position in ground frame */
    const EulerType&  euler, /* drone euler angle */ 
    const VectorType& boundary_point, /* one point on the nearest boundary(in ground) */
    const VectorType& boundary_normal, /* vector of the nearest boundary (from the surface to the drone) (in ground frame)*/
    double thrust, /* thrust of the drone, always => 0 (-z direction) */
    double rotor_radius, /* effect of rotor radius on wind disturbance */
    double exponent = 1.5 /* exponent of the disturbance ratio to thrust, usually 1.5, others for testing */);

/* exaggerated version for testing and demo */
ForceType boundary_disturbance_exaggerated(
    const VectorType& position,
    const EulerType& euler,
    const VectorType& boundary_point,
    const VectorType& boundary_normal,
    double thrust,
    double rotor_radius,
    double exponent);

VelocityType boundary_disturbance_as_wind(
    const VectorType& position, const EulerType& euler,
    const VectorType& boundary_point, const VectorType& boundary_normal, double thrust,
    double rotor_radius,
    const VectorType& drag1, // used to convert to force to wind effect
    double exponent = 1.5);

inline VelocityType wind_from_drone(
    const VectorType& position, const EulerType& euler,
    const VectorType& boundary_point, const VectorType& boundary_normal, double thrust,
    double rotor_radius,
    const VectorType& drag1, // used to convert to force to wind effect
    double exponent = 1.5)
{
    return -boundary_disturbance_as_wind(position, euler, boundary_point, boundary_normal,
        thrust, rotor_radius, drag1, exponent);
}


inline bool boundary_is_near(double distance, double rotor_radius) {
    // asserting distance, rotor_radius >= 0
    return distance < 5.0 * rotor_radius; // the drone is near the boundary
}
inline bool boundary_is_near(const VectorType& position, const VectorType& boundary_point,
    const VectorType& boundary_normal, double rotor_radius) {
    // asserting normal is normalized
    auto distance = std::abs(dot(position - boundary_point, boundary_normal));
    return boundary_is_near(distance, rotor_radius);
}


} /* namespace hako::drone_physics */