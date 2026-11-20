#pragma once

#include <cstddef>

namespace hako::aircraft {

inline constexpr std::size_t kLegacyRotorCount = 4;
inline constexpr std::size_t kMaxRotorCount = 16;

// Compatibility name for the fixed-quad implementation. Runtime code must use
// IAirCraft::get_rotor_count() instead.
inline constexpr int ROTOR_NUM = static_cast<int>(kLegacyRotorCount);

}  // namespace hako::aircraft
