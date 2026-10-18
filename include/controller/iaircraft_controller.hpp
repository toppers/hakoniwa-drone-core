#pragma once

#include <cstdint>
#include <functional>
#include <optional>
#include <memory>
#include <string>

#include "config/drone_config.hpp"
#include "controller/aircraft_controller_types.h"
#include "logger.hpp"

namespace hakoniwa::drone::control_adapter {
class IControlAdapterContext;
struct ControlAllocationStatus;
}

namespace hako::controller {

// The phase of flight a caller requests: the API service from its command state,
// the tuning runner from its scenario. The 3D position adapter shapes the takeoff and the landing.
enum class FlightPhase : std::uint8_t {
    Normal = 0,
    Takeoff = 1,
    Landing = 2,
};

using ControlStageSkip = hako::config::ControlStageSkip;

enum class AircraftControlMode {
    ATTI,
    GPS
};


struct PwmDuty {
    double d[HAKO_AIRCRAFT_MAX_ROTOR_NUM];
};


class IAircraftMixer {
public:
    virtual ~IAircraftMixer() {}
    virtual void set_control_adapter_context(
        const hakoniwa::drone::control_adapter::IControlAdapterContext* context)
    {
        (void)context;
    }
    // Receives the allocation status of every run, so the controller can feed
    // allocation saturation back to RateControl on the next cycle
    // (AllocationFeedbackPolicy, pro-docs/control-link/interface-spec.md).
    using AllocationStatusSink =
        std::function<void(const hakoniwa::drone::control_adapter::ControlAllocationStatus&)>;
    virtual void set_allocation_status_sink(AllocationStatusSink sink)
    {
        (void)sink;
    }
    // Receives the body torque [N*m] that each allocation actually produced,
    // reconstructed from the normalized rotor thrust and the rotor geometry
    // (adapter-independent; logged in controller.csv).
    using AllocationTorqueSink = std::function<void(double x_nm, double y_nm, double z_nm)>;
    virtual void set_allocation_torque_sink(AllocationTorqueSink sink)
    {
        (void)sink;
    }
    virtual PwmDuty run(mi_aircraft_control_out_t& in) = 0;
};
class IAircraftController: public logger::ILog {
private:
    std::shared_ptr<IAircraftMixer> mixer_;
    int index_;
protected:
    std::shared_ptr<logger::IHakoLogger> logger;
public:
    virtual ~IAircraftController() {
        if (logger != nullptr) {
            logger->close();
        }
    }
    virtual void set_logger(std::shared_ptr<logger::IHakoLogger> logger)
    {
        this->logger = logger;
        if (logger != nullptr) {
            std::cout << "Logger set successfully for controller index " << index_ << std::endl;
        }
        else {
            std::cout << "Logger is null for controller index " << index_ << std::endl;
        }
    }
    virtual bool is_radio_control() = 0;
    // Whether the vehicle is flying, from the controller's own takeoff/landing
    // state (RC).  std::nullopt when the controller does not track it.
    virtual std::optional<bool> is_airborne() const
    {
        return std::nullopt;
    }
    // Landed state from the operating mode (the same source as the EKF
    // flight state), passed to RateControl as RateControlInput::landed.
    // std::nullopt when the operating mode does not know it.
    virtual void set_landed(std::optional<bool> landed)
    {
        (void)landed;
    }
    // Clears the control state (PID integrators, previous stage outputs)
    // without touching logs, configuration or targets.  DroneService calls it
    // when a flight starts, so a new takeoff does not inherit the last one.
    virtual void reset_control_state() {}
    // Skips due stage runs with a seeded probability (timing disturbance); default: never.
    virtual void set_stage_skip(const ControlStageSkip& skip) { (void)skip; }
    virtual void reset() = 0;
    virtual void set_index(int index) {
        index_ = index;
    }
    virtual void set_mixer(std::unique_ptr<IAircraftMixer> mixer) {
        mixer_ = std::move(mixer);
    }
    virtual void set_control_adapter_context(
        const hakoniwa::drone::control_adapter::IControlAdapterContext* context)
    {
        if (mixer_ != nullptr) {
            mixer_->set_control_adapter_context(context);
        }
    }
    virtual std::shared_ptr<IAircraftMixer> mixer() {
        return mixer_;
    }
    virtual mi_aircraft_control_out_t run(mi_aircraft_control_in_t& in) = 0;

    virtual void set_mode(AircraftControlMode mode) = 0;

    virtual void set_flip_control(bool enabled) = 0;

    virtual AircraftControlMode get_mode() = 0;

    virtual int get_internal_state() = 0;

    virtual bool is_flip_control_enabled() = 0;

    virtual void set_target_roll_deg(double roll_deg) = 0;
    virtual void set_target_pitch_deg(double pitch_deg) = 0;
    virtual void set_target_yaw_deg(double yaw_deg) = 0;
    virtual void set_target_altitude_m(double altitude_m) = 0;
    virtual void set_target_position_xy_m(double x_m, double y_m) = 0;
    virtual void set_target_velocity_xy_m_s(double vx_m_s, double vy_m_s) = 0;
    virtual void set_target_vertical_speed_m_s(double vz_m_s) = 0;
    virtual void set_target_roll_rate_rad_s(double p_rad_s) = 0;
    virtual void set_target_pitch_rate_rad_s(double q_rad_s) = 0;
    virtual void set_target_yaw_rate_rad_s(double r_rad_s) = 0;
    virtual void clear_all_target() {}
    // Kept until the next call (clear_all_target does not reset it). Controllers without a 3D position
    // stage (radio) ignore it.
    virtual void set_flight_phase(FlightPhase) {}
};

class IAircraftControllerContainer {
public:
    static std::shared_ptr<IAircraftControllerContainer> create();
    virtual ~IAircraftControllerContainer() = default;
    virtual std::vector<std::shared_ptr<IAircraftController>>& getControllers() = 0;
    virtual void createAircraftControllers(config::DroneConfigManager& configManager, bool is_param_text_base) = 0;
};

}
