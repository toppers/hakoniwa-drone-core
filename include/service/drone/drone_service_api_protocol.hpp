#pragma once

#include "service/drone/idrone_service_container.hpp"
#include "service/drone/drone_service_protocol.hpp"
#include <thread>

namespace hako::service {

class DroneServiceApiProtocol {
private:
    std::shared_ptr<IDroneServiceContainer> drone_service_container_;
    void set_header(ServicePduDataType& pdu, bool request, bool result, int result_code)
    {
        pdu.pdu.takeoff.header.request = request;
        pdu.pdu.takeoff.header.result = result;
        pdu.pdu.takeoff.header.result_code = result_code;
    }
    void wait_response(int index, ServicePduDataType& pdu)
    {
        while (true) {
            drone_service_container_->peek_pdu(index, pdu);
            if (!pdu.pdu.takeoff.header.request) {
                break;
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(500));
            auto pos = get_position(index);
            std::cout << "INFO: position x=" << std::fixed << std::setprecision(1) << pos.x << " y=" << pos.y << " z=" << pos.z << std::endl;


        }
    }
public:
    DroneServiceApiProtocol(std::shared_ptr<IDroneServiceContainer> drone_service_container) : drone_service_container_(drone_service_container) {}
    virtual ~DroneServiceApiProtocol() = default;
    bool takeoff(int index, double height) 
    {
        ServicePduDataType pdu = {};
        pdu.id = SERVICE_PDU_DATA_ID_TYPE_TAKEOFF;
        //prepare
        set_header(pdu, true, false, 0);
        pdu.pdu.takeoff.height = height;
        pdu.pdu.takeoff.speed = 5.0;
        pdu.pdu.takeoff.yaw_deg = get_yaw_deg(index);
        drone_service_container_->write_pdu(index, pdu);

        std::cout << "INFO: takeoff write done" << std::endl;
        //do wait
        wait_response(index, pdu);
        //done
        pdu.pdu.takeoff.header.request = false;
        drone_service_container_->write_pdu(index, pdu);
        return true;
    }
    bool land(int index)
    {
        ServicePduDataType pdu = {};
        pdu.id = SERVICE_PDU_DATA_ID_TYPE_LAND;
        //prepare
        set_header(pdu, true, false, 0);
        pdu.pdu.land.height = 0.0;
        pdu.pdu.land.speed = 5.0;
        pdu.pdu.land.yaw_deg = get_yaw_deg(index);
        drone_service_container_->write_pdu(index, pdu);
        //do wait
        wait_response(index, pdu);
        //done
        pdu.pdu.land.header.request = false;
        drone_service_container_->write_pdu(index, pdu);
        return true;
    }
    bool move(int index, float x, float y, float z)
    {
        ServicePduDataType pdu = {};
        pdu.id = SERVICE_PDU_DATA_ID_TYPE_MOVE;
        //prepare
        set_header(pdu, true, false, 0);
        pdu.pdu.move.x = x;
        pdu.pdu.move.y = y;
        pdu.pdu.move.z = z;
        pdu.pdu.move.yaw_deg = get_yaw_deg(index);
        pdu.pdu.move.speed = 5.0;
        drone_service_container_->write_pdu(index, pdu);
        //do wait
        wait_response(index, pdu);
        //done
        pdu.pdu.move.header.request = false;
        drone_service_container_->write_pdu(index, pdu);
        
        return true;
    }
    double get_yaw_deg(int index)
    {
        ServicePduDataType pdu = {};
        pdu.id = SERVICE_PDU_DATA_ID_TYPE_POSITION;
        drone_service_container_->peek_pdu(index, pdu);
        return radian_to_degree(pdu.pdu.position.angular.z);
    }

    Vector3Type get_position(int index)
    {
        ServicePduDataType pdu = {};
        pdu.id = SERVICE_PDU_DATA_ID_TYPE_POSITION;
        drone_service_container_->peek_pdu(index, pdu);
        return { pdu.pdu.position.linear.x, pdu.pdu.position.linear.y, pdu.pdu.position.linear.z };
    }
    Vector3Type get_attitude(int index)
    {
        ServicePduDataType pdu = {};
        pdu.id = SERVICE_PDU_DATA_ID_TYPE_POSITION;
        drone_service_container_->peek_pdu(index, pdu);
        return { pdu.pdu.position.angular.x, pdu.pdu.position.angular.y, pdu.pdu.position.angular.z };
    }   
};
} // namespace hako::service


