#pragma once


#include "drone/impl/drone_service.hpp"
#include "service/drone/idrone_service.hpp"
#include "service/iservice_pdu_syncher.hpp"
#include <array>

namespace hako::service::impl {

class IDroneServiceOperation {
public:
    virtual ~IDroneServiceOperation() = default;

    virtual void reset() = 0;

    virtual void setup_controller_inputs(mi_aircraft_control_in_t& in) = 0;

    virtual bool can_advanceTimeStep_for_controller() = 0;

    virtual void write_controller_pdu() = 0;

    virtual void setServicePduSyncher(std::shared_ptr<IServicePduSyncher> pdu_syncher) = 0;
};

}

