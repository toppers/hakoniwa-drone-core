#pragma once

#include <nlohmann/json.hpp>
#include <fstream>
#include <iostream>
#include <vector>
#include <filesystem>
#include <optional>

#include <regex>
#include <algorithm>
#include "config/drone_config_types.hpp"

namespace fs = std::filesystem;
#ifdef __APPLE__
#define SHARED_LIB_EXT  ".so"
#elif __linux__
#define SHARED_LIB_EXT  ".so"
#else
#define SHARED_LIB_EXT  ".dll"
#endif

namespace hako::config {
/* #define DRONE_PX4_RX_DEBUG_ENABLE */
/* DRONE_PX4_TX_DEBUG_ENABLE */
/* DRONE_PID_CONTROL_CPP */
struct RotorPosition {
    std::vector<double> position;
    double rotationDirection;
};
#define DEGREE2RADIAN(v)    ( (v) * M_PI / (180.0) )
#define RADIAN2DEGREE(v)    ( (180.0 * (v)) / M_PI )

class DroneConfig {
private:
    nlohmann::json configJson;
    std::string config_filepath;
    std::string controllerParamText = "";
public:
    DroneConfig() {}
    bool init(const std::string& configFilePath) {
        config_filepath = configFilePath;
        std::ifstream configFile(config_filepath);
        if (configFile.is_open()) {
            try {
                configFile >> configJson;
            } catch (nlohmann::json::parse_error& e) {
                std::cerr << "JSON parsing error: " << e.what() << std::endl;
                return false;
            }
        } else {
            std::cerr << "Unable to open config file: " << config_filepath << std::endl;
            return false;
        }
        return true;
    }
    bool init_from_text(const std::string& configText) {
        try {
            configJson = nlohmann::json::parse(configText);
        } catch (nlohmann::json::parse_error& e) {
            std::cerr << "JSON parsing error: " << e.what() << std::endl;
            return false;
        }
        return true;
    }

    /* Simulation parameters */
    double getSimTimeStep() const {
        return configJson["simulation"]["timeStep"].get<double>();
    }
    bool getSimLockStep() const {
        return configJson["simulation"]["lockstep"].get<bool>();
    }
    std::string getSimLogOutputDirectory() const 
    {
        std::string directory = configJson["simulation"]["logOutputDirectory"].get<std::string>();
        if (!std::filesystem::exists(directory)) {
            std::cerr << "Error: Log output directory '" << directory << "' does not exist." << std::endl;
            return "./";
        }
        return directory;
    }
    std::string getRoboName() const
    {
        return configJson["name"].get<std::string>();
    }
    std::string getSimLogFullPath(const std::string& filename) const
    {
        std::string logDirectory = getSimLogOutputDirectory();

        if (logDirectory.back() != '/' && logDirectory.back() != '\\') {
            logDirectory += "/";
        }

        return logDirectory + filename;
    }
    std::string getSimLogFullPathFromIndex(int index, const std::string& name) const
    {
        std::string logDirectory = getSimLogDirectoryPathFromIndex(index);
        if (logDirectory.back() != '/' && logDirectory.back() != '\\') {
            logDirectory += "/";
        }
        return logDirectory + name;
    }
    std::string getSimLogDirectoryPathFromIndex(int index) const
    {
        std::string logDirectory = getSimLogOutputDirectory();
        if (logDirectory.back() != '/' && logDirectory.back() != '\\') {
            logDirectory += "/";
        }
        std::string path = logDirectory + "drone_log" + std::to_string(index);
        return path;
    }

    /* Log Output for Sensors */
    bool isSimSensorLogEnabled(const std::string& sensorName) const {
        return configJson["simulation"]["logOutput"]["sensors"][sensorName].get<bool>();
    }

    /* Log Output for MAVLINK */
    bool isMSimavlinkLogEnabled(const std::string& mavlinkMessage) const {
        return configJson["simulation"]["logOutput"]["mavlink"][mavlinkMessage].get<bool>();
    }

    /* MAVLINK Transmission Period */
    int getSimMavlinkTransmissionPeriod(const std::string& mavlinkMessage) const {
        return configJson["simulation"]["mavlink_tx_period_msec"][mavlinkMessage].get<int>();
    }

    /* Location parameters */
    double getSimLatitude() const {
        return configJson["simulation"]["location"]["latitude"].get<double>();
    }

    double getSimLongitude() const {
        return configJson["simulation"]["location"]["longitude"].get<double>();
    }

    double getSimAltitude() const {
        return configJson["simulation"]["location"]["altitude"].get<double>();
    }

    struct MagneticField {
        double intensity_nT;
        double declination_deg;
        double inclination_deg;
    };

    MagneticField getSimMagneticField() const {
        MagneticField field;
        field.intensity_nT = configJson["simulation"]["location"]["magneticField"]["intensity_nT"].get<double>();
        field.declination_deg = configJson["simulation"]["location"]["magneticField"]["declination_deg"].get<double>();
        field.inclination_deg = configJson["simulation"]["location"]["magneticField"]["inclination_deg"].get<double>();
        return field;
    }

    /* Drone Dynamics parameters */
    std::string getCompDroneDynamicsPhysicsEquation() const {
        return configJson["components"]["droneDynamics"]["physicsEquation"].get<std::string>();
    }
    bool getCompDroneDynamicsMuJoCoParameters(MuJoCoParameters& params) const {
        if (configJson["components"]["droneDynamics"].contains("mujoco")) {
            params.modelPath = configJson["components"]["droneDynamics"]["mujoco"]["modelPath"].get<std::string>();
            params.modelName = configJson["components"]["droneDynamics"]["mujoco"]["modelName"].get<std::string>();
            params.propNames.clear();
            for (const auto& item : configJson["components"]["droneDynamics"]["mujoco"]["propNames"]) {
                params.propNames.push_back(item);
            }
            return true;
        }
        return false;
    }
    bool getCompDroneDynamicsUseQuaternion() const {
        if (configJson["components"]["droneDynamics"].contains("useQuaternion")) {
            return configJson["components"]["droneDynamics"]["useQuaternion"].get<bool>();
        }
        return false;
    }
    std::vector<double> getCompDroneDynamicsAirFrictionCoefficient() const {
        std::vector<double> frictions;
        for (const auto& item : configJson["components"]["droneDynamics"]["airFrictionCoefficient"]) {
            frictions.push_back(item);
        }
        return frictions;
    }
    bool getCompDroneDynamicsCollisionDetection() const {
        return configJson["components"]["droneDynamics"]["collision_detection"].get<bool>();
    }
    bool getCompDroneDynamicsEnableDisturbance() const {
         if (configJson["components"]["droneDynamics"].contains("enable_disturbance")) {
            return configJson["components"]["droneDynamics"]["enable_disturbance"].get<bool>();
         }
         else {
            return false;
         }
    }
    bool getCompDroneDynamicsManualControl() const {
        return configJson["components"]["droneDynamics"]["manual_control"].get<bool>();
    }
    std::vector<double> getCompDroneDynamicsBodySize() const {
        std::vector<double> body_size;
        for (const auto& item : configJson["components"]["droneDynamics"]["body_size"]) {
            body_size.push_back(item);
        }
        return body_size;
    }
    std::vector<double> getCompDroneDynamicsInertia() const {
        std::vector<double> inertia;
        for (const auto& item : configJson["components"]["droneDynamics"]["inertia"]) {
            inertia.push_back(item);
        }
        return inertia;
    }
    std::vector<double> getCompDroneDynamicsPosition() const {
        std::vector<double> inertia;
        for (const auto& item : configJson["components"]["droneDynamics"]["position_meter"]) {
            inertia.push_back(item);
        }
        return inertia;
    }
    std::vector<double> getCompDroneDynamicsAngle() const {
        std::vector<double> inertia;
        for (const auto& item : configJson["components"]["droneDynamics"]["angle_degree"]) {
            inertia.push_back(item);
        }
        return inertia;
    }
    double getCompDroneDynamicsMass() const {
        return configJson["components"]["droneDynamics"]["mass_kg"].get<double>();
    }
    std::optional<hako::config::OutOfBoundsReset> getCompDroneDynamicsOutOfBoundsReset() const {
        if (configJson["components"]["droneDynamics"].contains("out_of_bounds_reset")) {
            std::cout << "out_of_bounds_reset values are enabled." << std::endl;
            hako::config::OutOfBoundsReset out_of_bounds_reset;
            out_of_bounds_reset.position = configJson["components"]["droneDynamics"]["out_of_bounds_reset"]["position"].get<std::vector<bool>>();
            out_of_bounds_reset.velocity = configJson["components"]["droneDynamics"]["out_of_bounds_reset"]["velocity"].get<std::vector<bool>>();
            out_of_bounds_reset.angular_velocity = configJson["components"]["droneDynamics"]["out_of_bounds_reset"]["angular_velocity"].get<std::vector<bool>>();
            return std::make_optional(out_of_bounds_reset);
        }
        return std::nullopt;
    }
    //body_boundary_disturbance power
    double getCompDroneDynamicsBodyBoundaryDisturbancePower() const {
        if (configJson["components"]["droneDynamics"].contains("body_boundary_disturbance_power")) {
            std::cout << "body_boundary_disturbance_power is enabled: power = "
                      << configJson["components"]["droneDynamics"]["body_boundary_disturbance_power"].get<double>() << std::endl;
            return configJson["components"]["droneDynamics"]["body_boundary_disturbance_power"].get<double>();
        } else {
            std::cout << "WARNING: body_boundary_disturbance_power is not defined in the configuration." << std::endl;
            return 1.0; // Default value
        }
    }

    std::string getCompRotorVendor() const {
        if (configJson["components"]["rotor"].contains("vendor")) {
            return configJson["components"]["rotor"]["vendor"].get<std::string>();
        } else {
            return "None";
        }
    }

    hako::config::BatteryModelParameters getComDroneDynamicsBattery() const {
        hako::config::BatteryModelParameters params = {};
        try {
            if (configJson["components"].contains("battery")) {
                params.vendor = configJson["components"]["battery"]["vendor"].get<std::string>();
                if (configJson["components"]["battery"].contains("BatteryModelCsvFilePath")) {
                    params.BatteryModelCsvFilePath = configJson["components"]["battery"]["BatteryModelCsvFilePath"].get<std::string>();
                }
                if (configJson["components"]["battery"].contains("model")) {
                    params.model = configJson["components"]["battery"]["model"].get<std::string>();
                }
                else {
                    params.model = "constant";
                }
                params.VoltageLevelGreen = configJson["components"]["battery"]["VoltageLevelGreen"].get<double>();
                params.VoltageLevelYellow = configJson["components"]["battery"]["VoltageLevelYellow"].get<double>();
                params.NominalVoltage = configJson["components"]["battery"]["NominalVoltage"].get<double>();
                params.NominalCapacity = configJson["components"]["battery"]["NominalCapacity"].get<double>();
                params.EODVoltage = configJson["components"]["battery"]["EODVoltage"].get<double>();
                params.CapacityLevelYellow = configJson["components"]["battery"]["CapacityLevelYellow"].get<double>();
#ifdef HAKO_DEBUG_LOG
                std::cout << "Battery model is enabled." << std::endl;
#endif
                return params;
            }
            else {
                std::cout << "ERROR: Battery model config is invalid." << std::endl;
            }
        } catch (const std::exception& e) {
            std::cerr << "Error retrieving Battery Model config: " << e.what() << std::endl;
        }
        return params;
    }

    hako::config::RotorBatteryModelConstants getCompDroneDynamicsRotorDynamicsConstants() const {
        hako::config::RotorBatteryModelConstants constants = {};
        try {
            if (configJson.contains("components") &&
                configJson["components"].contains("rotor") &&
                configJson["components"]["rotor"].contains("dynamics_constants")) {
                
                constants.R  = configJson["components"]["rotor"]["dynamics_constants"]["R"].get<double>();
                constants.Cq = configJson["components"]["rotor"]["dynamics_constants"]["Cq"].get<double>();
                if (configJson["components"]["rotor"]["dynamics_constants"].contains("Ct")) {
                    //for rigid body model
                    constants.Ct = configJson["components"]["rotor"]["dynamics_constants"]["Ct"].get<double>();
                }
                else {
                    constants.Ct = 0.0;
                }
                constants.K  = configJson["components"]["rotor"]["dynamics_constants"]["K"].get<double>();
                constants.D  = configJson["components"]["rotor"]["dynamics_constants"]["D"].get<double>();
                constants.J  = configJson["components"]["rotor"]["dynamics_constants"]["J"].get<double>();
#ifdef HAKO_DEBUG_LOG
                std::cout << "Rotor battery model is enabled." << std::endl;
#endif
                return constants;
            }
        } catch (const std::exception& e) {
            std::cerr << "Error retrieving rotor dynamics constants: " << e.what() << std::endl;
        }
        std::cout << "ERROR: Rotor battery model config is invalid." << std::endl;
        return constants;
    }
    int getCompRotorRpmMax() const {
        return configJson["components"]["rotor"]["rpmMax"].get<int>();
    }
    double getCompRotorRadius() const {
        if (!configJson["components"]["rotor"].contains("radius")) {
            std::cerr << "ERROR: Rotor radius is not defined in the configuration." << std::endl;
            return 0.1;
        }
        return configJson["components"]["rotor"]["radius"].get<double>();
    }

    /* Thruster parameters */
    std::vector<RotorPosition> getCompThrusterRotorPositions() const {
        std::vector<RotorPosition> positions;
        for (const auto& item : configJson["components"]["thruster"]["rotorPositions"]) {
            RotorPosition pos;
            pos.position = item["position"].get<std::vector<double>>();
            pos.rotationDirection = item["rotationDirection"].get<double>();
            positions.push_back(pos);
        }
        return positions;
    }

    double getCompThrusterParameter(const std::string& param_name) const {
        if (configJson["components"]["thruster"].contains(param_name)) {
            return configJson["components"]["thruster"][param_name].get<double>();
        } else {
            return 0.0;
        }
    }

    std::string getCompThrusterVendor() const {
        if (configJson["components"]["thruster"].contains("vendor")) {
            return configJson["components"]["thruster"]["vendor"].get<std::string>();
        } else {
            return "None";
        }
    }
    std::string getLastDirectoryName(const std::string& pathStr) const {
        fs::path pathObj(pathStr);

        if (!pathObj.empty()) {
            if (pathObj.filename() == "." || pathObj.filename() == ".." || pathObj.filename() == fs::path()) {
                pathObj = pathObj.parent_path();
            }
            return pathObj.filename().string();
        } else {
            return "";
        }
    }
    std::string getCompSensorVendor(const std::string& sensor_name) const {
        if (configJson["components"]["sensors"][sensor_name].contains("vendor")) {
            std::string moduleDirectory = configJson["components"]["sensors"][sensor_name]["vendor"].get<std::string>();
            if (moduleDirectory.back() != '/' && moduleDirectory.back() != '\\') {
                moduleDirectory += "/";
            }
            std::string moduleName = getCompSensorContextModuleName(sensor_name);
            if (moduleName.empty()) {
                moduleName = getLastDirectoryName(moduleDirectory);
            }
#if WIN32
            return moduleDirectory + moduleName + SHARED_LIB_EXT;
#else
            return moduleDirectory + "lib" + moduleName + SHARED_LIB_EXT;
#endif
        } else {
            return "";
        }
    }
    std::string getCompSensorContextModuleName(const std::string& sensor_name) const
    {
        return getCompSensorContext(sensor_name, "moduleName");
    }

    std::string getCompSensorContext(const std::string& sensor_name, const std::string& param) const
    {
         if (configJson["components"]["sensors"][sensor_name].contains("context")) {
            if (configJson["components"]["sensors"][sensor_name]["context"].contains(param)) {
                return configJson["components"]["sensors"][sensor_name]["context"][param];
            }
        }
        return "";
    }

    int getCompSensorSampleCount(const std::string& sensor_name) const {
        return configJson["components"]["sensors"][sensor_name]["sampleCount"].get<int>();
    }
    double getCompSensorNoise(const std::string& sensor_name) const {
        return configJson["components"]["sensors"][sensor_name]["noise"].get<double>();
    }
    bool isExistController(const std::string& param)
    {
        if (!configJson.contains("controller")) {
            std::cerr << "WARING: can not find controller on drone_config" << std::endl;
            return false;
        }
        if (!configJson["controller"].contains(param)) {
            std::cerr << "WARING: can not find controller[ " << param << " ] on drone_config" << std::endl;
            return false;
        }
        return true;
    }
    double getControllerPid(const std::string& param1, const std::string& param2, const std::string& param3)
    {
        return configJson["controller"]["pid"][param1][param2][param3].get<double>();
    }
    std::string getControllerModuleName() const
    {
        if (configJson["controller"].contains("moduleName")) {
            return configJson["controller"]["moduleName"];
        }
        else {
            return getRoboName();
        }
    }
    std::string getControllerContext(const std::string& param) const
    {
        if (configJson["controller"].contains("context")) {
            if (configJson["controller"]["context"].contains(param)) {
                return configJson["controller"]["context"][param];
            }
        }
        return "";
    }
    std::string getControllerModuleFilePath() const
    {
        if (configJson["controller"].contains("moduleDirectory")) {
            std::string moduleDirectory = configJson["controller"]["moduleDirectory"].get<std::string>();
            if (moduleDirectory.back() != '/' && moduleDirectory.back() != '\\') {
                moduleDirectory += "/";
            }
#if WIN32
            return moduleDirectory + getControllerModuleName() + SHARED_LIB_EXT;
#else
            return moduleDirectory + "lib" + getControllerModuleName() + SHARED_LIB_EXT;
#endif
        }
        else {
            return "";
        }
    }
    std::string getControllerParamFilePath() const
    {
        if (configJson["controller"].contains("paramFilePath")) {
            std::string paramFilePath = configJson["controller"]["paramFilePath"].get<std::string>();
            return paramFilePath;
        }
        else {
            return "";
        }
    }
    std::string getControllerParamText() const
    {
        //std::cout << "controllerParamText: " << controllerParamText << std::endl;
        if (!controllerParamText.empty()) {
            return controllerParamText;
        }
        if (configJson["controller"].contains("paramText")) {
            std::string paramText = configJson["controller"]["paramText"].get<std::string>();
            return paramText;
        }
        else {
            return "";
        }
    }
    void setControllerParamText(const std::string& paramText)
    {
        controllerParamText = paramText;
    }
    struct MixerInfo {
        bool enable;
        std::string vendor;
        bool enableDebugLog;
        bool enableErrorLog;

        // not config info
        double K;
        double R;
        double Cq;
        double V_bat;
    };

    bool getControllerMixerInfo(MixerInfo& info) const
    {
        if (configJson["controller"].contains("mixer")) {
            info.vendor = configJson["controller"]["mixer"]["vendor"];
            info.enableDebugLog = configJson["controller"]["mixer"]["enableDebugLog"];
            info.enableErrorLog = configJson["controller"]["mixer"]["enableErrorLog"];
            info.enable = true;
            return true;
        }
        else {
            return false;
        }
    }

    bool getControllerDirectRotorControl() const
    {
        if (configJson["controller"].contains("direct_rotor_control")) {
            return configJson["controller"]["direct_rotor_control"];
        }
        else {
            return false;
        }
    }
};


class DroneConfigManager {
private:
    std::vector<DroneConfig> configs;

public:
    DroneConfigManager() {}

    int loadConfigFromText(const std::string& config_text)
    {
        DroneConfig drone_config;
        if (!drone_config.init_from_text(config_text)) {
            std::cerr << "ERROR: can not find drone config path: " << config_text << std::endl;
            return 0;
        }
        //std::cout << "INFO: LOADED drone config file: " << config_text << std::endl;
        configs.push_back(drone_config);
        return 0;
    }

    int loadConfigsFromDirectory(const std::string& directoryPath) {
        namespace fs = std::filesystem;
        std::regex pattern("drone_config_(\\d+)\\.json");

        std::vector<std::pair<int, std::string>> filesWithIndex;

        try {
            for (const auto& entry : fs::directory_iterator(directoryPath)) {
                if (entry.is_regular_file()) {
                    std::smatch matches;
                    std::string filename = entry.path().filename().string();

                    if (std::regex_match(filename, matches, pattern) && matches.size() == 2) {
                        int index = std::stoi(matches[1].str());
                        filesWithIndex.emplace_back(index, entry.path().string());
                    }
                }
            }
        } catch (const fs::filesystem_error& e) {
            std::cerr << "Filesystem error: " << e.what() << std::endl;
            return 0;
        } catch (const std::exception& e) {
            std::cerr << "Standard exception: " << e.what() << std::endl;
            return 0;
        } catch (...) {
            std::cerr << "Unknown error occurred during directory traversal." << std::endl;
            return 0;
        }

        std::sort(filesWithIndex.begin(), filesWithIndex.end(), [](const auto& a, const auto& b) {
            return a.first < b.first;
        });

        int loadedCount = 0;
        for (const auto& [index, filePath] : filesWithIndex) {
            if (loadConfigFromFile(filePath)) {
                loadedCount++;
            } else {
                std::cerr << "Failed to load config from: " << filePath << std::endl;
            }
        }

        return loadedCount;
    }
    bool loadConfigFromFile(const std::string& drone_config_path) {
        DroneConfig drone_config;
        if (!drone_config.init(drone_config_path)) {
            std::cerr << "ERROR: can not find drone config path: " << drone_config_path << std::endl;
            return false;
        }
        //std::cout << "INFO: LOADED drone config file: " << drone_config_path << std::endl;
        configs.push_back(drone_config);
        return true;
    }


    bool getConfig(size_t index, DroneConfig& config) {
        if (index >= configs.size()) {
            return false;
        }
        config = configs[index];
        return true;
    }
    DroneConfig& getConfig(size_t index) {
        if (index >= configs.size()) {
            throw std::out_of_range("Index out of range: getConfig on DroneConfigManager");
        }
        return configs[index];
    }
    int getConfigCount() {
        return (int)configs.size();
    }
};

extern class DroneConfigManager drone_config_manager;

}

