#pragma once

#include "iaircraft.hpp"
#include "iaircraft_controller.hpp"
#include "iservice_container.hpp"
#include "iservice_pdu_types.hpp"
#include <cstdint>
#include <atomic>
#include <memory>

namespace hako::service {


extern bool drone_pdu_data_deep_copy(const ServicePduDataType& source, ServicePduDataType& dest);
class IDroneService {
public:
    static std::shared_ptr<IDroneService> create(std::shared_ptr<aircraft::IAirCraft> aircraft, std::shared_ptr<controller::IAircraftController> controller);
    virtual ~IDroneService() = default;
    virtual bool startService(uint64_t deltaTimeUsec) = 0;
    virtual void advanceTimeStep() = 0;
    virtual void stopService() = 0;
    virtual bool isServiceAvailable() = 0;
    virtual void resetService() = 0;
    virtual uint64_t getSimulationTimeUsec() = 0;

    virtual bool write_pdu(ServicePduDataType& pdu) = 0;
    virtual bool read_pdu(ServicePduDataType& pdu) = 0;
    virtual void peek_pdu(ServicePduDataType& pdu) = 0;

    virtual std::string getRobotName() = 0;

    virtual void setPduSyncher(std::shared_ptr<IServicePduSyncher> pdu_syncher) = 0;

};

}

