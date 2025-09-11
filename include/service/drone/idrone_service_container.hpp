#pragma once

#include "aircraft/iaircraft.hpp"
#include "controller/iaircraft_controller.hpp"
#include "service/iservice_container.hpp"
#include <memory>

namespace hako::service {

class IDroneServiceContainer : public IServiceContainer {
public:
    static std::shared_ptr<IDroneServiceContainer> create(std::shared_ptr<aircraft::IAirCraftContainer> aircraft_container, std::shared_ptr<controller::IAircraftControllerContainer> controller_container);
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

    virtual bool flushSensorData(uint32_t ) override { return false;}
};
}

