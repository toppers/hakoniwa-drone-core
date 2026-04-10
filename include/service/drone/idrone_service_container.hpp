#pragma once

#include "aircraft/iaircraft.hpp"
#include "config/drone_config.hpp"
#include "controller/iaircraft_controller.hpp"
#include "service/iservice_container.hpp"
#include <memory>

namespace hako::service {

namespace impl {
class IDroneServicePort;
}

class IDroneServiceContainer : public IServiceContainer {
public:
    enum class OperationMode {
        Rc,
        Api,
    };
    enum class ApiServiceMode {
        LegacyApi,
        Rpc,
    };

    static std::shared_ptr<IDroneServiceContainer> create(
        std::shared_ptr<aircraft::IAirCraftContainer> aircraft_container,
        std::shared_ptr<controller::IAircraftControllerContainer> controller_container,
        config::DroneConfigManager* config_manager = nullptr);
    virtual ~IDroneServiceContainer() = default;
    virtual bool startService(uint64_t deltaTimeUsec) override = 0;
    virtual bool setRealTimeStepUsec(uint64_t deltaTimeUsec) override = 0;
    virtual void advanceTimeStep(uint32_t index) override = 0;
    virtual void advanceTimeStep() override = 0;
    virtual void stopService() override = 0;
    virtual void resetService() override = 0;
    virtual bool isServiceAvailable() = 0;
    virtual uint64_t getSimulationTimeUsec(uint32_t index) override = 0;

    virtual bool write_pdu(uint32_t index, ServicePduDataType& pdu) override = 0;
    virtual bool read_pdu(uint32_t index, ServicePduDataType& pdu) override = 0;
    virtual void peek_pdu(uint32_t index, ServicePduDataType& pdu) override = 0;

    virtual uint32_t getNumServices() override = 0;
    virtual std::string getRobotName(uint32_t index) override = 0;
    virtual void setServicePort(uint32_t index, std::shared_ptr<impl::IDroneServicePort> service_port) = 0;
    virtual std::string getFleetServiceConfigPath() const = 0;
    virtual OperationMode getOperationMode(uint32_t index) const = 0;
    virtual ApiServiceMode getApiServiceMode(uint32_t index) const = 0;

    virtual void setPduSyncher(std::shared_ptr<IServicePduSyncher> pdu_syncher) override = 0;
    /*
     * Set extended options for the drone service
     */
    virtual void setExtendedOptions(uint32_t index, const DroneServiceExtendedOptions& options) override = 0;
    /*
     * Get extended options for the drone service
     */
    virtual DroneServiceExtendedOptions getExtendedOptions(uint32_t index) const override = 0;
    /*
     * Get flight mode for the drone service
     */
    virtual int get_flight_mode(uint32_t index) const = 0;
    /*
     * Get internal state for the drone service
     */
    virtual int get_internal_state(uint32_t index) const = 0;

    /*
     * Tuning helpers
     */
    virtual void set_position(uint32_t index, const aircraft::DronePositionType& pos) = 0;
    virtual void set_velocity(uint32_t index, const aircraft::DroneVelocityType& vel) = 0;
    virtual void set_direct_thrust_override(uint32_t index, bool enabled, double thrust) = 0;
    virtual void set_target_roll_deg(uint32_t index, double roll_deg) = 0;
    virtual void set_target_pitch_deg(uint32_t index, double pitch_deg) = 0;
    virtual void set_target_yaw_deg(uint32_t index, double yaw_deg) = 0;
    virtual void set_target_altitude_m(uint32_t index, double altitude_m) = 0;
    virtual void set_target_position_xy_m(uint32_t index, double x_m, double y_m) = 0;
    virtual void set_target_velocity_xy_m_s(uint32_t index, double vx_m_s, double vy_m_s) = 0;

    virtual bool flushSensorData(uint32_t ) override { return false;}
};
}
