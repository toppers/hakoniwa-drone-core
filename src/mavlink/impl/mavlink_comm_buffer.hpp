#pragma once

#include <unordered_map>
#include <vector>
#include <memory>
#include <utility>
#include <iostream>
#include <atomic>
#include "impl/mavlink_service.hpp"

namespace hako::mavlink::impl {

class MavlinkCommBuffer {
public:
    static void init();
    static bool write(int index, MavlinkDecodedMessage &message);
    static bool read(int index, MavlinkHakoMessage &message, bool &is_dirty);

private:
    static const int MAVLINK_INSTNACE_MAX_NUM = 1024;
    struct PairHash {
        template <class T1, class T2>
        std::size_t operator()(const std::pair<T1, T2>& p) const {
            auto hash1 = std::hash<T1>{}(p.first);
            auto hash2 = std::hash<T2>{}(p.second);
            return hash1 ^ (hash2 << 1);
        }
    };
    static void set_busy();
    static void unset_busy();
    static std::atomic<bool>  is_busy_;
    static std::atomic<bool>  is_dirty_[MAVLINK_INSTNACE_MAX_NUM][MAVLINK_MSG_TYPE_NUM];
    static std::unordered_map<std::pair<int, MavlinkMsgType>, std::unique_ptr<MavlinkHakoMessage>, PairHash> cache_;
};

} // namespace hako::mavlink
