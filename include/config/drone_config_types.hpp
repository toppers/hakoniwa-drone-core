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
        double yawAirDragLinearCoefficient{0.0};
        double yawAirDragQuadraticCoefficient{0.0};
    };
    struct GpsSensorQualityConfig {
        struct Accuracy {
            double horizontal_m{0.5};
            double vertical_m{0.75};
            double speed_mps{0.5};
        };
        double sacc_mps{0.5};
        double eph_m{10.0};
        double epv_m{10.0};
        int satellites_visible{10};
        std::optional<Accuracy> accuracy{};
    };
    struct ControllerEkfConfig {
        bool enable{false};
        std::uint64_t imu_interval_usec{3000};
        std::uint64_t mag_interval_usec{20000};
        std::uint64_t baro_interval_usec{10000};
        std::uint64_t gps_interval_usec{100000};
        bool imu_average{false};  // controller.ekf.imuAverage
        std::string param_file_path{};
        // controller.ekf.altitudeReference: "world" (default) gives the controllers the altitude in
        // the world frame, as without the EKF; "takeoff" gives it from where the EKF started (the
        // vehicle at rest on the ground), as ArduPilot and PX4 hold altitude above home.
        bool altitude_from_takeoff{false};
    };
    struct SitlConfig {
        std::uint64_t actuator_timeout_msec{300};
        // Maps an incoming SITL actuator channel to a local rotor index.
        // An empty mapping preserves the identity channel-to-rotor order.
        std::vector<std::uint32_t> actuator_to_rotor_index{};
        // PX4 only: HIL_SENSOR period. 0 (unset) keeps the historical 3 ms with one physics
        // step per actuator; a set value holds each actuator over the physics steps up to the
        // next sensor (e.g. 4 ms on 1 ms physics, as PX4 Gazebo can).
        std::uint64_t sensor_period_msec{0};
    };

// Seeded skips of the control stages' due runs (drone_config controller.stageSkip; Control Link only).
struct ControlStageSkip {
    std::uint64_t seed{1};
    double altitude{0.0};
    double horizontal{0.0};
    double attitude{0.0};
    double rate{0.0};
};

}
