#pragma once

#include "service/iservice_pdu_types.hpp"
#include "service/iservice_pdu_syncher.hpp"
#include <memory>

namespace hako::service {

/*
 * Extended options for the drone service
 */
struct DroneServiceExtendedOptionCollision {
    bool enable_debuff_on_collision; // Enable debuff on collision
    uint32_t debuff_duration_msec; // Debuff duration in milliseconds
    static DroneServiceExtendedOptionCollision Default() {
        DroneServiceExtendedOptionCollision option;
        option.enable_debuff_on_collision = false;
        option.debuff_duration_msec = 0;
        return option;
    }
};
/*
 * Extended options for the drone service
 */
struct DroneServiceExtendedOptions {
    DroneServiceExtendedOptionCollision collision; // Collision options
    static DroneServiceExtendedOptions Default() {
        DroneServiceExtendedOptions options;
        options.collision = DroneServiceExtendedOptionCollision::Default();
        return options;
    }
};

class IServiceContainer {
public:
    virtual ~IServiceContainer() = default;
    virtual bool startService(uint64_t deltaTimeUsec) = 0;
    virtual bool setRealTimeStepUsec(uint64_t deltaTimeUsec) = 0;
    virtual void advanceTimeStep() = 0;
    virtual void advanceTimeStep(uint32_t index) = 0;
    virtual void stopService() = 0;
    virtual void resetService() = 0;
    virtual uint64_t getSimulationTimeUsec(uint32_t index) = 0;

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

} // namespace hako::service


