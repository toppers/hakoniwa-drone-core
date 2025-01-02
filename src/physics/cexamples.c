#include <stdio.h>

// include the library header
#include "drone_physics_c.h"

static const double PI = 3.14159265358979;

int main() {
    // create a body frame from Euler angles.
    dp_euler_t frame = {0, 0, PI/2};
    dp_velocity_t body_velocity = {100, 200, 300};
    
    // Convert the body velocity to the ground frame.
    dp_velocity_t g = dp_ground_vector_from_body(&body_velocity, &frame);

    // get the x,y,z components of the velocity.
    printf("x=%g, y=%g, z=%g\n", g.x, g.y, g.z);
    // output: x = 200, y = -100, z = 300

    // you can also use explicit initialization.
    // reverse the conversion to the body frame.
    dp_velocity_t b = dp_body_vector_from_ground(
        &g, &(dp_euler_t){0, 0, PI/2}
    );

    // get the x,y,z components of the velocity.
    printf("x=%g, y=%g, z=%g\n", b.x, b.y, b.z);
    // output: x = 100, y = 200, z = 300, back again.

    return 0;
}