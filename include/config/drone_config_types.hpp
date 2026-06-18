#pragma once

#include <string>
#include <vector>
#include <optional>
#include <cstdint>

namespace hako::config {
    enum class LoggingMode {
        None,
        Csv,
        Memory,
    };
    struct OutOfBoundsReset {
        std::vector<bool> position; /* X, Y, Z */
        std::vector<bool> velocity; /* X, Y, Z */
        std::vector<bool> angular_velocity; /* X, Y, Z */
    };
    struct RotorBatteryModelConstants {
        double R;
        double Cq;
        double Ct; //for rigid body model
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
    struct MuJoCoParameters {
        std::string modelName;
        std::string modelPath;
        std::vector<std::string> propNames;
    };
    struct GpsSensorQualityConfig {
        double sacc_mps{0.5};
        double eph_m{10.0};
        double epv_m{10.0};
        int satellites_visible{10};
    };
    struct ControllerEkfConfig {
        bool enable{false};
        std::uint64_t imu_interval_usec{3000};
        std::uint64_t mag_interval_usec{20000};
        std::uint64_t baro_interval_usec{10000};
        std::uint64_t gps_interval_usec{100000};
        std::string param_file_path{};
    };
}
