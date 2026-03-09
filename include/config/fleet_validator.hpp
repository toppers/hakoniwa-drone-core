#pragma once

#include <array>
#include <map>
#include <string>
#include <vector>

namespace hako::config {

struct DroneInstanceConfig {
    std::string name;
    std::string type;
    std::array<double, 3> position_meter;
    std::array<double, 3> angle_degree;
};

struct DroneFleetConfig {
    std::string fleet_filepath;
    std::string service_config_path;
    std::map<std::string, std::string> types;
    std::vector<DroneInstanceConfig> drones;
};

enum class FleetConfigLoadKind {
    Legacy,
    Fleet
};

struct FleetConfigLoadResult {
    bool ok;
    FleetConfigLoadKind kind;
    std::string message;
    DroneFleetConfig* fleet_config;
};

FleetConfigLoadResult loadFleetConfigFile(const std::string& fleet_config_path);
void releaseFleetConfigLoadResult(FleetConfigLoadResult& result);

}
