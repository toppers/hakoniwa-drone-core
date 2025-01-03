#include "service/drone/drone_service_rc_api.h"
#include "service/drone/drone_service_rc_protocol.hpp"
#include "logger/ilogger.hpp"
#include <memory>
#include <iostream>
#include <thread>
#include <chrono>
#include <atomic>

using namespace hako::aircraft;
using namespace hako::controller;
using namespace hako::service;
using namespace hako::logger;

static std::shared_ptr<IDroneServiceContainer> service_container = nullptr;
static std::shared_ptr<DroneServiceRcProtocol> rc = nullptr;

std::thread service_thread;
static std::atomic<bool> service_running = false;

int drone_service_rc_init(const char* drone_config_dir_path, const char* custom_json_path, int is_keyboard_control)
{
    //TODO
    (void)custom_json_path;
    if (service_container) {
        return -1;
    }
    try {
        /*
        * Load drone config 
        */
        DroneConfigManager configManager;
        configManager.loadConfigsFromDirectory(drone_config_dir_path);

        /*
        * Create aircraft container
        */
        auto aircraft_container = IAirCraftContainer::create();
        aircraft_container->createAirCrafts(configManager);

        /*
        * Create controller container
        */
        std::shared_ptr<IAircraftControllerContainer> controller_container = IAircraftControllerContainer::create();
        controller_container->createAircraftControllers(configManager);

        /*
        * Create service container
        */
        service_container = IDroneServiceContainer::create(aircraft_container, controller_container);
        if (service_container == nullptr) {
            std::cerr << "Failed to create service container" << std::endl;
            return -1;
        }

        /*
        * Setup Service
        */
        DroneConfig config;
        configManager.getConfig(0, config);
        uint64_t timestep_usec = (uint64_t)(config.getSimTimeStep() * 1000000.0);
        std::cout << "timestep_usec: " << timestep_usec << std::endl;
        auto ret = service_container->startService(timestep_usec);
        if (!ret) {
            std::cerr << "Failed to start service" << std::endl;
            return -1;
        }
        IHakoLogger::enable();
        /*
        * Setup Radio Control Protocol
        * keyboard control is enabled
        */
        rc = std::make_shared<DroneServiceRcProtocol>(service_container, is_keyboard_control);
        if (rc == nullptr) {
            return -1;
        }
    } catch (std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return -1;
    }
    std::cout << "Service initialized successfully:: service_container = " << service_container << std::endl;
    return 0;
}
int drone_service_rc_set_pdu_id_map(int pdu_id, int channel_id)
{
    //TODO: implement
    (void)pdu_id;
    (void)channel_id;
    return 0;
}

int drone_service_rc_start()
{
    if (service_thread.joinable()) {
        std::cerr << "Service is already running" << std::endl;
        return -1;
    }
    if (service_container == nullptr) {
        std::cerr << "Service container is not initialized" << std::endl;
        return -1;
    }

    service_running = true;

    service_thread = std::thread([]() {
        try {
            std::cout << "> Start service" << std::endl;
            while (service_running && service_container && service_container->isServiceAvailable()) {
                /*
                 * Advance time step
                 */
                IHakoLogger::set_time_usec(service_container->getSimulationTimeUsec(0));
                service_container->advanceTimeStep();
                std::this_thread::sleep_for(std::chrono::milliseconds(1)); // TODO: 
            }
            std::cout << "Finish service because : " << service_container.get() << std::endl;
            service_container = nullptr;
            rc = nullptr;
        } catch (std::exception& e) {
            std::cerr << "Exception in service thread: " << e.what() << std::endl;
        }
    });
    return 0;
}

int drone_service_rc_run()
{
    try {
        rc->run();
        return 0;
    } catch (std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return -1;
    }
}


int drone_service_rc_stop()
{
    try {
        if (!service_container) {
            std::cerr << "Service container is not initialized" << std::endl;
            return -1;
        }

        std::cout << "Stopping service..." << std::endl;
        service_running = false;
        service_container->stopService();

        if (service_thread.joinable()) {
            service_thread.join();
        }
        std::cout << "Service stopped successfully" << std::endl;
    } catch (std::exception& e) {
        std::cerr << "Exception during service stop: " << e.what() << std::endl;
        return -1;
    }
    return 0;
}

/*
 * stick operations
 */
int drone_service_rc_put_vertical(int index, double value)
{
    try {
        if (rc == nullptr) {
            return -1;
        }
        rc->drone_vertical_op(index, value);
    } catch (std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return -1;
    }
    return 0;
}
int drone_service_rc_put_horizontal(int index, double value)
{
    try {
        if (rc == nullptr) {
            return -1;
        }
        rc->drone_horizontal_op(index, value);
    } catch (std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return -1;
    }
    return 0;
}
int drone_service_rc_put_heading(int index, double value)
{
    try {
        if (rc == nullptr) {
            return -1;
        }
        rc->drone_heading_op(index, value);
    } catch (std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return -1;
    }
    return 0;
}
int drone_service_rc_put_forward(int index, double value)
{
    try {
        if (rc == nullptr) {
            return -1;
        }
        rc->drone_forward_op(index, value);
    } catch (std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return -1;
    }
    return 0;
}
/*
 * button operations
 */
int drone_service_rc_put_radio_control_button(int index, int value)
{
    try {
        if (rc == nullptr) {
            return -1;
        }
        rc->drone_radio_control_button(index, value);
    } catch (std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return -1;
    }
    return 0;
}
int drone_service_rc_put_magnet_control_button(int index, int value)
{
    //TODO: implment
    (void)index;
    (void)value;
    return 0;
}
int drone_service_rc_put_camera_control_button(int index, int value)
{
    //TODO: implment
    (void)index;
    (void)value;
    return 0;
}
int drone_service_rc_put_home_control_button(int index, int value)
{
    //TODO: implment
    (void)index;
    (void)value;
    return 0;
}
/*
 * get position and attitude
 */
int drone_service_rc_get_position(int index, double* x, double* y, double* z)
{
    try {
        if (rc == nullptr) {
            return -1;
        }
        auto pos = rc->get_position(index);
        *x = pos.x;
        *y = pos.y;
        *z = pos.z;
    } catch (std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return -1;
    }
    return 0;
}
int drone_service_rc_get_attitude(int index, double* x, double* y, double* z)
{
    try {
        if (rc == nullptr) {
            return -1;
        }
        auto att = rc->get_attitude(index);
        *x = att.x;
        *y = att.y;
        *z = att.z;
    } catch (std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return -1;
    }
    return 0;
}
int drone_service_rc_get_controls(int index, double* c1, double* c2, double* c3, double* c4, double* c5, double* c6, double* c7, double* c8)
{
    try {
        if (rc == nullptr) {
            return -1;
        }
        if (c1 == nullptr) {
            return -1;
        }
        if (c2 == nullptr) {
            return -1;
        }
        if (c3 == nullptr) {
            return -1;
        }
        if (c4 == nullptr) {
            return -1;
        }
        auto controls = rc->get_controls(index);
        *c1 = controls.duty_rate[0];
        *c2 = controls.duty_rate[1];
        *c3 = controls.duty_rate[2];
        *c4 = controls.duty_rate[3];
        if (c5 != nullptr) {
            *c5 = 0.0;
        }
        if (c6 != nullptr) {
            *c6 = 0.0;
        }
        if (c7 != nullptr) {
            *c7 = 0.0;
        }
        if (c8 != nullptr) {
            *c8 = 0.0;
        }
        return 0;
    }
    catch (std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return -1;
    }
}

/*
 * miscs
 */
unsigned long long drone_service_rc_get_time_usec(int index)
{
    try {
        return service_container->getSimulationTimeUsec(index);
    } catch (std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
        return 0;
    }
}
