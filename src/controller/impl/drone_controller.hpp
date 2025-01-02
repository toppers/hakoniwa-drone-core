#pragma once


#include "drone_alt_controller.hpp"
#include "drone_pos_controller.hpp"
#include "drone_heading_controller.hpp"
#include "drone_angle_controller.hpp"
#include "hako_controller_param_loader.hpp"
#include <stdexcept>
#include <memory>

namespace hako::controller::impl {

class DroneController {
public:
    std::unique_ptr<DroneAltController> alt;
    std::unique_ptr<DronePosController> pos;
    std::unique_ptr<DroneHeadingController> head;
    std::unique_ptr<DroneAngleController> angle;
    HakoControllerParamLoader loader;
    bool is_param_text = false;
    std::string data_;
    
    DroneController(bool is_param_text_base, std::string& data) : 
        loader() 
    {
        is_param_text = is_param_text_base;
        data_ = data;
        reload();
        alt = std::make_unique<DroneAltController>(loader);
        pos = std::make_unique<DronePosController>(loader);
        head = std::make_unique<DroneHeadingController>(loader);
        angle = std::make_unique<DroneAngleController>(loader);
    }
    void reset() {
        reload();
        alt->reset();
        pos->reset();
        head->reset();
        angle->reset();
    }
private:
    void reload()
    {
        if (!is_param_text) {
            auto param_data = loader.get_controller_param_filedata(data_);
            loader.reload(param_data);
        } 
        else 
        {
            loader.reload(data_);
        }
    }

};
}