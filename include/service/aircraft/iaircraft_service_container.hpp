#pragma once

#include "aircraft/iaircraft.hpp"
#include "config/drone_config_types.hpp"
#include "service/iservice_container.hpp"
#include "mavlink.hpp"
#include <memory>

namespace hako::service {

typedef struct {
    hako::mavlink::MavlinkMsgType msg_id;
    uint64_t send_cycle_usec;
    mavlink::MavLinkServiceDesitinationType destination;
    bool (*user_custom_encode) (aircraft::IAirCraft& aircraft, hako::mavlink::MavlinkHakoMessage& message, uint64_t time_usec);
} HakoMavLinkProtocolTxConfigType;

typedef struct {
    hako::mavlink::MavlinkMsgType msg_id;
    bool (*user_custom_decode) (int index, const void* data, int detalen, hako::mavlink::MavlinkHakoMessage& message);
} HakoMavLinkProtocolRxConfigType;

typedef struct {
    HakoMavLinkProtocolRxConfigType rx;
    std::vector<HakoMavLinkProtocolTxConfigType> tx;
} HakoMavLinkProtocolConfigType;

class IAircraftServiceContainer : public IServiceContainer {
public:
    static std::shared_ptr<IAircraftServiceContainer> create(std::shared_ptr<mavlink::MavLinkServiceContainer> mavlink_service_container, std::shared_ptr<aircraft::IAirCraftContainer> aircraft_container);
    virtual ~IAircraftServiceContainer() = default;
    virtual bool startService(uint64_t deltaTimeUsec) = 0;
    virtual bool startService(bool lockStep, uint64_t deltaTimeUsec) = 0;
    virtual bool setRealTimeStepUsec(uint64_t deltaTimeUsec) = 0;
    virtual void setSitlConfig(const hako::config::SitlConfig& config) = 0;
    virtual bool setProtocolConfig(const HakoMavLinkProtocolConfigType& config) = 0;
    // PX4 only (simulation.sitl.sensor_period_msec): sets the HIL_SENSOR period of the default
    // transmission path and holds each actuator over the physics steps up to the next sensor.
    // Not called: 3 ms sensors and one physics step per actuator, as before.
    virtual bool setSitlSensorPeriodUsec(uint32_t index, uint64_t period_usec) = 0;
    // PX4 HIL sensor update metadata. Zero keeps the historical behavior for that sensor.
    virtual bool setSitlSensorUpdatePeriodsUsec(
        uint32_t index,
        uint64_t baro_period_usec,
        uint64_t mag_period_usec,
        uint64_t gps_period_usec) = 0;
    // Optional: where to record the SITL time base (sitl_time.json) at start, so that a log of the
    // autopilot (PX4 takes HIL_SENSOR time_usec = simulation time + this base as its clock) can be
    // put on the service clock exactly. Not called: nothing is written.
    virtual void setSitlTimeRecordPath(uint32_t index, const std::string& path) = 0;
    // IServiceContainer retains advanceTimeStep() for tick-driven services.
    // Aircraft SITL is receiver-event-driven; its implementation rejects these
    // calls to prevent a duplicate physics step.
    virtual void stopService() = 0;
    virtual void resetService() = 0;
    virtual uint64_t getSimulationTimeUsec(uint32_t index) = 0;
    virtual uint64_t getSitlTimeUsec(uint32_t index) = 0;

    virtual void enableReceiveEvent(uint32_t index) = 0;
    virtual bool hasReceivedActuator(uint32_t index) const = 0;

    virtual bool write_pdu(uint32_t index, ServicePduDataType& pdu) = 0;
    virtual bool read_pdu(uint32_t index, ServicePduDataType& pdu) = 0;
    virtual void peek_pdu(uint32_t index, ServicePduDataType& pdu) = 0;

    virtual uint32_t getNumServices() = 0;
    virtual std::string getRobotName(uint32_t index) = 0;

    virtual void setPduSyncher(std::shared_ptr<IServicePduSyncher> pdu_syncher) = 0;
    /*
     * Set extended options for the drone service
     */
    virtual void setExtendedOptions(uint32_t index, const DroneServiceExtendedOptions& options) = 0;
    /*
     * Get extended options for the drone service
     */
    virtual DroneServiceExtendedOptions getExtendedOptions(uint32_t index) const = 0;

    virtual bool flushSensorData(uint32_t index) = 0;

};

} // namespace hako::service::aircraft
