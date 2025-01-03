#pragma once


#include "service/drone/idrone_service_container.hpp"
#include "service/drone/idrone_service.hpp"
#include "controller/iaircraft_controller.hpp"

using namespace hako::aircraft;
using namespace hako::controller;

namespace hako::service::impl {

class DroneServiceContainer : public IDroneServiceContainer {
public:
    DroneServiceContainer(std::shared_ptr<IAirCraftContainer> aircraft_container, std::shared_ptr<IAircraftControllerContainer> controller_container) {
        if (aircraft_container->getAllAirCrafts().size() != controller_container->getControllers().size()) {
            throw std::runtime_error("aircraft and controller size mismatch");
        }
        for (std::shared_ptr<IAirCraft> aircraft : aircraft_container->getAllAirCrafts()) {
            std::shared_ptr<IDroneService> drone_service = IDroneService::create(aircraft, controller_container->getControllers()[aircraft->get_index()]);
            drone_services_.push_back(drone_service);
        }
    };
    ~DroneServiceContainer() = default;

    bool startService(uint64_t deltaTimeUsec) override {
        for (auto& drone_service : drone_services_) {
            drone_service->startService(deltaTimeUsec);
        }
        return true;
    }
    bool setRealTimeStepUsec(uint64_t deltaTimeUsec) override {
        (void)deltaTimeUsec;
        return true;
    }

    void advanceTimeStep(uint32_t index) override {
        if (index >= drone_services_.size()) {
            throw std::runtime_error("advanceTimeStep index out of range");
        }
        drone_services_[index]->advanceTimeStep();
    }
    void advanceTimeStep() override {
        for (auto& drone_service : drone_services_) {
            drone_service->advanceTimeStep();
        }
    }
    bool isServiceAvailable() override {
        for (auto& drone_service : drone_services_) {
            if (!drone_service->isServiceAvailable()) {
                return false;
            }
        }
        return true;
    }

    void stopService() override {
        for (auto& drone_service : drone_services_) {
            drone_service->stopService();
        }
    }

    void resetService() override {
        for (auto& drone_service : drone_services_) {
            drone_service->resetService();
        }
    }

    uint64_t getSimulationTimeUsec(uint32_t index) override {
        if (index >= drone_services_.size()) {
            throw std::runtime_error("getSimulationTimeUsec index out of range");
        }
        return drone_services_[index]->getSimulationTimeUsec();
    }

    bool write_pdu(uint32_t index, ServicePduDataType& pdu) override {
        if (index >= drone_services_.size()) {
            throw std::runtime_error("write_pdu index out of range");
        }
        return drone_services_[index]->write_pdu(pdu);
    }

    bool read_pdu(uint32_t index, ServicePduDataType& pdu) override {
        if (index >= drone_services_.size()) {
            throw std::runtime_error("read_pdu index out of range");
        }
        return drone_services_[index]->read_pdu(pdu);
    };
    void peek_pdu(uint32_t index, ServicePduDataType& pdu) override {
        if (index >= drone_services_.size()) {
            throw std::runtime_error("peek_pdu index out of range");
        }
        drone_services_[index]->peek_pdu(pdu);
    }

    uint32_t getNumServices() override {
        return static_cast<uint32_t>(drone_services_.size());
    }
    std::string getRobotName(uint32_t index) override {
        if (index >= drone_services_.size()) {
            throw std::runtime_error("getRobotName index out of range");
        }
        return drone_services_[index]->getRobotName();
    }

    void setPduSyncher(std::shared_ptr<IServicePduSyncher> pdu_syncher) override {
        for (auto& drone_service : drone_services_) {
            drone_service->setPduSyncher(pdu_syncher);
        }

    }
private:
    std::vector<std::shared_ptr<IDroneService>> drone_services_;
};
}

