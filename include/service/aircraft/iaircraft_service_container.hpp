#pragma once

#include "aircraft/iaircraft.hpp"
#include "service/iservice_container.hpp"
#include "mavlink.hpp"
#include <memory>

namespace hako::service {

class IAircraftServiceContainer : public IServiceContainer {
public:
    static std::shared_ptr<IAircraftServiceContainer> create(std::shared_ptr<mavlink::MavLinkServiceContainer> mavlink_service_container, std::shared_ptr<aircraft::IAirCraftContainer> aircraft_container);
    virtual ~IAircraftServiceContainer() = default;
    virtual bool startService(uint64_t deltaTimeUsec) = 0;
    virtual bool startService(bool lockStep, uint64_t deltaTimeUsec) = 0;
    virtual bool setRealTimeStepUsec(uint64_t deltaTimeUsec) = 0;
    virtual void advanceTimeStep(uint32_t index) = 0;
    virtual void advanceTimeStep() = 0;
    virtual void stopService() = 0;
    virtual void resetService() = 0;
    virtual uint64_t getSimulationTimeUsec(uint32_t index) = 0;
    virtual uint64_t getSitlTimeUsec(uint32_t index) = 0;

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

};

} // namespace hako::service::aircraft


