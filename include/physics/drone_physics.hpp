#pragma once

/**
 * Includes the two public headers in this directory.
 * Drone + Body ...  Drone Body Physics(Body Dynamics, Frames and Forces)
 *       + Rotor ... Drone Rotor Physics(Rotor Dynamics)
 */

#define BP_INCLUDE_IO /* for printint out support */

#include "drone_frames.hpp"
#include "rotor_physics.hpp"
#include "body_physics.hpp"