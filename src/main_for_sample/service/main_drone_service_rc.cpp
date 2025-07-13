#include "service.hpp"
#include <iostream>
#include <thread>
#include <sstream>
#include <vector>
#include <string>
#include <queue>

using namespace hako::aircraft;
using namespace hako::controller;
using namespace hako::service;
using namespace hako::logger;
using namespace hako::config;

static void do_collision(DroneServiceRcProtocol& rc)
{
    bool is_target_static = false;
    Vector3Type target_velocity = {1, 2, 3};
    Vector3Type target_angular_velocity = {4, 5, 6};
    Vector3Type target_euler = {9, 99, 999};
    Vector3Type self_contact_vector = {7, 8, 9};
    Vector3Type target_contact_vector = {10, 11, 12};
    Vector3Type target_inertia = { 0.0061, 0.00653, 0.0116 };
    Vector3Type normal = {1, 2, 3};
    double target_mass = 0.71;
    double restitution_coefficient = 0.8;
    std::cout << "do_collision" << std::endl;
    rc.trigger_impulse_collision(0,
        is_target_static, 
        target_velocity, 
        target_angular_velocity, 
        target_euler,
        self_contact_vector, 
        target_contact_vector, 
        target_inertia, 
        normal, 
        target_mass, 
        restitution_coefficient);
}

int main(int argc, const char* argv[])
{
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << "<real_sleep_msec> <drone_config_dir_path>" << std::endl;
        return 1;
    }
    int real_sleep_msec = std::stoi(argv[1]);
    const char* drone_config_dir_path = argv[2];
    IHakoLogger::enable();

    /*
     * Load drone config 
     */
    DroneConfigManager configManager;
    std::string drone_config_file_path = drone_config_dir_path + std::string("/drone_config_0.json");
    //fileopen
    std::ifstream configFile(drone_config_file_path);
    if (!configFile.is_open()) {
        std::cerr << "Unable to open config file: " << drone_config_file_path << std::endl;
        return 1;
    }
    std::stringstream ss;
    ss << configFile.rdbuf();
    //load config
    configManager.loadConfigFromText(ss.str());

    /*
     * Create aircraft container
     */
    auto aircraft_container = IAirCraftContainer::create();
    aircraft_container->createAirCrafts(configManager);

    /*
     * Create controller container
     */
    //get controller file path
    DroneConfig& config = configManager.getConfig(0);
    std::string controller_config_file_path = config.getControllerParamFilePath();
    //fileopen
    std::ifstream controllerConfigFile(controller_config_file_path);
    if (!controllerConfigFile.is_open()) {
        std::cerr << "Unable to open controller config file: " << controller_config_file_path << std::endl;
        return 1;
    }
    std::stringstream controller_ss;
    controller_ss << controllerConfigFile.rdbuf();
    //load config
    config.setControllerParamText(controller_ss.str());

    std::shared_ptr<IAircraftControllerContainer> controller_container = IAircraftControllerContainer::create();
    controller_container->createAircraftControllers(configManager, true);

    /*
     * Create service container
     */
    std::shared_ptr<IDroneServiceContainer> service_container = IDroneServiceContainer::create(aircraft_container, controller_container);

    /*
     * Setup Service
     */
    configManager.getConfig(0, config);
    uint64_t timestep_usec = (uint64_t)(config.getSimTimeStep() * 1000000.0);
    std::cout << "timestep_usec: " << timestep_usec << std::endl;
    auto ret = service_container->startService(timestep_usec);
    if (!ret) {
        std::cerr << "Failed to start service" << std::endl;
        return 1;
    }


    /*
     * Setup Radio Control Protocol
     * keyboard control is enabled
     */
    DroneServiceRcProtocol rc(service_container, true);

    /*
     * Main loop
     */
    std::thread th([&service_container, real_sleep_msec]() {
        std::cout << "> Start service" << std::endl;
        while (service_container->isServiceAvailable()) {
            /*
            * Advance time step
            */
            IHakoLogger::set_time_usec(service_container->getSimulationTimeUsec(0));
            service_container->advanceTimeStep();
            std::this_thread::sleep_for(std::chrono::milliseconds(real_sleep_msec));
        }
        std::cout << "Finish service" << std::endl;
    });
    std::queue<char> queue_keyboard;
    std::thread keyboard_th([&queue_keyboard]() {
        while (true) {
            std::string line;
            std::getline(std::cin, line);
            char c = line[0];
            if (line.empty()) {
                c = 'h';
            }
            else if (line.size() > 1) {
                c = line[0];
            }
            //printf("c: 0x%x\n", c);
            queue_keyboard.push(c);
        }
    });
    char event_c = 0;
    int delayed_rotation_count = 0;
    hako::service::ServiceBatteryStatusType battery_status;
    while (true) {
        if (!queue_keyboard.empty()) {
            event_c = queue_keyboard.front();
            queue_keyboard.pop();
        }
        else {
            event_c = 0;
        }
        /*
         * Radio Control Protocol
         */
        /*
         * Usage:
         *  - w : up
         *  - s : down
         *  - a : turn left
         *  - d : turn right
         *  - i : forward
         *  - k : backward
         *  - j : left
         *  - l : right
         *  - x : radio control button
         *  - c : collision
         */
        //keyboard read
        switch (event_c) {
        case 'w':
            rc.drone_vertical_op(0, -1.0);
            break;
        case 's':
            rc.drone_vertical_op(0, 1.0);
            break;
        case 'a':
            rc.drone_heading_op(0, -1.0);
            delayed_rotation_count = 1000;
            break;
        case 'd':
            rc.drone_heading_op(0, 1.0);
            delayed_rotation_count = 1000;
            break;
        case 'i':
            rc.drone_forward_op(0, -0.8);
            break;
        case 'k':
            rc.drone_forward_op(0, 0.8);
            break;
        case 'j':
            rc.drone_horizontal_op(0, -0.8);
            break;
        case 'l':
            rc.drone_horizontal_op(0, 0.8);
            break;
        case 'x':
            rc.drone_radio_control_button(0, true);
            break;
        case 'm':
            rc.drone_mode_change_button(0, true);
            break;
        case 'g':
            {
                int mode = rc.get_flight_mode(0);
                if (mode == 0) {
                    std::cout << "Flight mode: ATTI" << std::endl;
                }
                else {
                    std::cout << "Flight mode: GPS" << std::endl;
                }
            }
            break;
        case 'b':
            battery_status = rc.get_battery_status(0);
            std::cout << "full_voltage: " << battery_status.full_voltage << std::endl;
            std::cout << "curr_voltage: " << battery_status.curr_voltage << std::endl;
            std::cout << "curr_temp: " << battery_status.curr_temp << std::endl;
            std::cout << "status: " << battery_status.status << std::endl;
            std::cout << "cycles: " << battery_status.cycles << std::endl;
            break;
        case 'p':
            {
                auto pos = rc.get_position(0);
                std::cout << "position x=" << std::fixed << std::setprecision(1) << pos.x << " y=" << pos.y << " z=" << pos.z << std::endl;
            }
            break;
        case 'r':
            {
                auto att = rc.get_attitude(0);
                std::cout << "attitude roll=" << std::fixed << std::setprecision(1) << att.x << " pitch=" << att.y << " yaw=" << att.z << std::endl;
            }
            break;
        case 't':
            std::cout << "simtime usec: " << service_container->getSimulationTimeUsec(0) << std::endl;
            break;
        case 'f':
            std::cout << "flip" << std::endl;
            for (int i = 0; i < 99; i++) {
                rc.drone_horizontal_op(0, 0.0);
                rc.run();
            }
            rc.drone_horizontal_op(0, 1.0);
            break;
        case 'c':
            do_collision(rc);
            break;
        case 0:
            break;
        default:
            std::cout  << " ----- USAGE -----" << std::endl;
            std::cout  << " ----- STICK -----" << std::endl;
            std::cout  << "|  LEFT  | RIGHT  |" << std::endl;
            std:: cout << "|   w    |   i    |" << std::endl;
            std:: cout << "| a   d  | j   l  |" << std::endl;
            std:: cout << "|   s    |   k    |" << std::endl;
            std::cout  << " ---- BUTTON ----" << std::endl;
            std::cout  << " x : radio control button" << std::endl;
            std::cout  << " m : mode change button" << std::endl;
            std::cout  << " g : get flight mode" << std::endl;
            std::cout  << " p : get position" << std::endl;
            std::cout  << " r : get attitude" << std::endl;
            std::cout  << " t : get simtime usec" << std::endl;
            std::cout  << " c : collision" << std::endl;
            std::cout  << " b : get battery status" << std::endl;
            break;
        }
        rc.run();
        static Vector3Type prev_pos = { 0.0, 0.0, 0.0 };
        auto pos = rc.get_position(0);
        if (fabs(pos.x - prev_pos.x) > 0.1 || fabs(pos.y - prev_pos.y) > 0.1 || fabs(pos.z - prev_pos.z) > 0.1) {
            std::cout << "position x=" << std::fixed << std::setprecision(1) << pos.x << " y=" << pos.y << " z=" << pos.z << std::endl;
            prev_pos = pos;
        }
        if (delayed_rotation_count > 0) {
            delayed_rotation_count--;
            if (delayed_rotation_count == 0)
            {
                auto att = rc.get_attitude(0);
                std::cout << "attitude roll=" << std::fixed << std::setprecision(1) << att.x << " pitch=" << att.y << " yaw=" << att.z << std::endl;
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(real_sleep_msec));
    }

    /*
     * Stop service
     */
    service_container->stopService();
    th.join();
    return 0;
}