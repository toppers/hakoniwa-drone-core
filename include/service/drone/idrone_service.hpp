#pragma once

#include "aircraft/iaircraft.hpp"
#include "controller/iaircraft_controller.hpp"
#include "service/iservice_container.hpp"
#include "service/iservice_pdu_types.hpp"
#include <cstdint>
#include <atomic>
#include <memory>

namespace hako::service {


extern bool drone_pdu_data_deep_copy(const ServicePduDataType& source, ServicePduDataType& dest);
/*
 * Drone service interface
 */
class IDroneService {
public:
    /*
     * Create drone service
     */
    static std::shared_ptr<IDroneService> create(std::shared_ptr<aircraft::IAirCraft> aircraft, std::shared_ptr<controller::IAircraftController> controller);
    /*
     * Destructor
     */
    virtual ~IDroneService() = default;
    /*
     * Start service
     */
    virtual bool startService(uint64_t deltaTimeUsec) = 0;
    /*
     * Advance time step
     */
    virtual void advanceTimeStep() = 0;
    /*
     * Stop service
     */
    virtual void stopService() = 0;
    /*
     * Check if service is available
     */
    virtual bool isServiceAvailable() = 0;
    /*
     * Reset service
     */
    virtual void resetService() = 0;
    /*
     * Get simulation time in microseconds
     */
    virtual uint64_t getSimulationTimeUsec() = 0;

    /*
     * Write PDU
     */
    virtual bool write_pdu(ServicePduDataType& pdu) = 0;
    /*
     * Read PDU
     */
    virtual bool read_pdu(ServicePduDataType& pdu) = 0;
    /*
     * Peek PDU
     */
    virtual void peek_pdu(ServicePduDataType& pdu) = 0;

    /*
     * Get robot name
     */
    virtual std::string getRobotName() = 0;

    /*
     * Set PDU syncher
     */
    virtual void setPduSyncher(std::shared_ptr<IServicePduSyncher> pdu_syncher) = 0;

    /*
     * Set extended options for the drone service
     */
    virtual void setExtendedOptions(const DroneServiceExtendedOptions& options) = 0;
    /*
     * Get extended options for the drone service
     */
    virtual DroneServiceExtendedOptions getExtendedOptions() const = 0;

    /*
     * Get flight mode for the drone service
     */
    virtual int get_flight_mode() const = 0;

    /*
     * Get internal state for the drone service
     */
    virtual int get_internal_state() const = 0;
};

}

