#pragma once

#include <string>
#include <vector>
#include <optional>

namespace hako::config {
    struct OutOfBoundsReset {
        std::vector<bool> position; /* X, Y, Z */
        std::vector<bool> velocity; /* X, Y, Z */
        std::vector<bool> angular_velocity; /* X, Y, Z */
    };
    struct RotorBatteryModelConstants {
        double R;
        double Cq;
        double K;
        double D;
        double J;
    };
    struct BatteryModelParameters {
        std::string vendor;
        std::string BatteryModelCsvFilePath;
        std::string model;
        double NominalCapacity;
        double EODVoltage;
        double NominalVoltage;
        double VoltageLevelGreen;
        double VoltageLevelYellow;
        double CapacityLevelYellow;
    };
}
