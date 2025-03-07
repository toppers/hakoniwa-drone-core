#pragma once
#include "aircraft/iaircraft.hpp"

#ifdef MUJOCO_ENABLED
#include "mujoco/mujoco.h"
namespace hako::aircraft::mujoco {
    extern mjModel* getMuJoCoModel(int index);
    extern mjData* getMuJoCoData(int index);    
}
#endif
