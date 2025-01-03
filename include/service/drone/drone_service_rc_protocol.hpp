#pragma once

#include "service/drone/idrone_service_container.hpp"

namespace hako::service {

#define GAME_CTRL_BUTTON_NUM    4
#define GAME_CTRL_AXIS_NUM      4
#define GAME_CTRL_BUTTON_ALIVE_TIME_USEC 100000
class DroneServiceRcProtocol {
private:
    const uint32_t GAME_CTRL_AXIS_LR_RR = 0;
    const uint32_t GAME_CTRL_AXIS_UP_DOWN = 1;
    const uint32_t GAME_CTRL_AXIS_LEFT_RIGHT = 2;
    const uint32_t GAME_CTRL_AXIS_FORWARD_BACK = 3;
    const uint32_t GAME_CTRL_BUTTON_RADIO_CONTROL = 0;
    const uint32_t GAME_CTRL_BUTTON_MAGNET_CONTROL = 1;
    const uint32_t GAME_CTRL_BUTTON_CAMERA_CONTROL = 2;
    const uint32_t GAME_CTRL_BUTTON_HOME_CONTROL = 3;
    const double stick_value_auto_decrease_value_ = 0.01;
    std::array<uint64_t, GAME_CTRL_BUTTON_NUM> button_alive_timeout_usec_ = { 0, 0, 0, 0 };
    bool keyboard_control_ = false;
    ServicePduDataType pdu = {};
    std::shared_ptr<IDroneServiceContainer> drone_service_container_;
    void stick_op(uint32_t index, uint32_t stick_index, double value)
    {
        pdu.pdu.game_ctrl.axis[stick_index] = value;
        drone_service_container_->write_pdu(index, pdu);
    }
    void button_op(uint32_t index, uint32_t button_index, bool value)
    {
        if (keyboard_control_ && value) {
            button_alive_timeout_usec_[button_index] = drone_service_container_->getSimulationTimeUsec(index) + GAME_CTRL_BUTTON_ALIVE_TIME_USEC;
        }
        pdu.pdu.game_ctrl.button[button_index] = value ? 1 : 0;
        drone_service_container_->write_pdu(index, pdu);
    }
    void run_stick_auto_decrease(uint32_t index)
    {
        for (auto i = 0; i < GAME_CTRL_AXIS_NUM; i++) {
            if (pdu.pdu.game_ctrl.axis[i] > 0.0) {
                pdu.pdu.game_ctrl.axis[i] -= stick_value_auto_decrease_value_;
            } else if (pdu.pdu.game_ctrl.axis[i] < 0.0) {
                pdu.pdu.game_ctrl.axis[i] += stick_value_auto_decrease_value_;
            }
            stick_op(0, i, pdu.pdu.game_ctrl.axis[i]);
        }
    }
    void run_button_auto_decrease(uint32_t index)
    {
        uint64_t current_time = drone_service_container_->getSimulationTimeUsec(index);
        for (auto i = 0; i < GAME_CTRL_BUTTON_NUM; i++) {
            if (pdu.pdu.game_ctrl.button[i] == 1) {
                if (current_time > button_alive_timeout_usec_[i])
                {
                    button_op(index, i, false);
                    button_alive_timeout_usec_[i] = 0;
                }
            }
        }
    }
public:
    DroneServiceRcProtocol(std::shared_ptr<IDroneServiceContainer> drone_service_container, bool keyboard_control) 
    : drone_service_container_(drone_service_container), keyboard_control_(keyboard_control) 
    {
        pdu.id = SERVICE_PDU_DATA_ID_TYPE_GAME_CTRL;
    }
    virtual ~DroneServiceRcProtocol() = default;
    void drone_vertical_op(uint32_t index, double value)
    {
        stick_op(index, GAME_CTRL_AXIS_UP_DOWN, value);
    }
    void drone_heading_op(uint32_t index, double value)
    {
        stick_op(index, GAME_CTRL_AXIS_LR_RR, value);
    }
    void drone_horizontal_op(uint32_t index, double value)
    {
        stick_op(index, GAME_CTRL_AXIS_LEFT_RIGHT, value);
    }
    void drone_forward_op(uint32_t index, double value)
    {
        stick_op(index, GAME_CTRL_AXIS_FORWARD_BACK, value);
    }
    void drone_radio_control_button(uint32_t index, bool value)
    {
        button_op(index, GAME_CTRL_BUTTON_RADIO_CONTROL, value);
    }
    void drone_magnet_control_button(uint32_t index, bool value)
    {
        button_op(index, GAME_CTRL_BUTTON_MAGNET_CONTROL, value);
    }
    void drone_camera_control_button(uint32_t index, bool value)
    {
        button_op(index, GAME_CTRL_BUTTON_CAMERA_CONTROL, value);
    }
    void drone_home_control_button(uint32_t index, bool value)
    {
        button_op(index, GAME_CTRL_BUTTON_HOME_CONTROL, value);
    }
    void run()
    {
        if (keyboard_control_) {
            for (auto index = 0; index < drone_service_container_->getNumServices(); index++) {
                run_stick_auto_decrease(index);
                run_button_auto_decrease(index);
            }
        }
    }
};
}