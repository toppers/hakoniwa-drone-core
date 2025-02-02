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
    void trigger_collision(int index, Vector3Type& contact_position, double restitution_coefficient)
    {
        ServicePduDataType col_pdu = {};
        col_pdu.id = SERVICE_PDU_DATA_ID_TYPE_COLLISION;
        col_pdu.pdu.collision.collision = true;
        col_pdu.pdu.collision.contact_num = 1;
        col_pdu.pdu.collision.relative_velocity = {0, 0, 0};
        col_pdu.pdu.collision.contact_position[0].x = contact_position.x;
        col_pdu.pdu.collision.contact_position[0].y = contact_position.y;
        col_pdu.pdu.collision.contact_position[0].z = contact_position.z;
        col_pdu.pdu.collision.restitution_coefficient = restitution_coefficient;
        
        drone_service_container_->write_pdu(index, col_pdu);
    }
    //trigger_impulse_collision
    void trigger_impulse_collision(int index, 
        bool is_target_static,
        Vector3Type& target_velocity, 
        Vector3Type& target_angular_velocity, 
        Vector3Type& target_euler,
        Vector3Type& self_contact_vector, 
        Vector3Type& target_contact_vector, 
        Vector3Type& target_inertia,
        Vector3Type& normal,
        double target_mass, 
        double restitution_coefficient)
    {
        ServicePduDataType impulse_col_pdu = {};
        impulse_col_pdu.id = SERVICE_PDU_DATA_ID_TYPE_IMPULSE_COLLISION;
        impulse_col_pdu.pdu.impulse_collision.collision = true;
        impulse_col_pdu.pdu.impulse_collision.is_target_static = is_target_static;
        impulse_col_pdu.pdu.impulse_collision.target_velocity = { target_velocity.x, target_velocity.y, target_velocity.z };
        impulse_col_pdu.pdu.impulse_collision.target_angular_velocity = { target_angular_velocity.x, target_angular_velocity.y, target_angular_velocity.z };
        impulse_col_pdu.pdu.impulse_collision.target_euler = { target_euler.x, target_euler.y, target_euler.z };
        impulse_col_pdu.pdu.impulse_collision.self_contact_vector = { self_contact_vector.x, self_contact_vector.y, self_contact_vector.z };
        impulse_col_pdu.pdu.impulse_collision.target_contact_vector = { target_contact_vector.x, target_contact_vector.y, target_contact_vector.z };
        impulse_col_pdu.pdu.impulse_collision.target_inertia = { target_inertia.x, target_inertia.y, target_inertia.z };
        impulse_col_pdu.pdu.impulse_collision.normal = { normal.x, normal.y, normal.z };

        impulse_col_pdu.pdu.impulse_collision.target_mass = target_mass;
        impulse_col_pdu.pdu.impulse_collision.restitution_coefficient = restitution_coefficient;

        drone_service_container_->write_pdu(index, impulse_col_pdu);
    }
};
} // namespace hako::service


