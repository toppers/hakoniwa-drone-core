#include "service/drone/drone_service_rc_protocol.hpp"
#include "logger/impl/hako_logger.hpp"
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


int main(int argc, const char* argv[])
{
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << "<real_sleep_msec> <drone_config_dir_path>" << std::endl;
        return 1;
    }
    int real_sleep_msec = std::stoi(argv[1]);
    const char* drone_config_dir_path = argv[2];

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
    std::shared_ptr<IDroneServiceContainer> service_container = IDroneServiceContainer::create(aircraft_container, controller_container);

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
        return 1;
    }
    IHakoLogger::enable();


    /*
     * Setup Radio Control Protocol
     * keyboard control is enabled
     */
    DroneServiceRcProtocol rc(service_container, true);

    /*
     * Main loop
     */
    std::thread th([&service_container, real_sleep_msec]() {
        std::cout << "Start service" << std::endl;
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
            char c;
            std::cin >> c;
            //c = getch();
            if (isalpha(c)) {
                c = tolower(c);
                std::cout << "c: " << c << std::endl;
                queue_keyboard.push(c);
            }
            else {
                c = 0;
            }
        }
    });
    char event_c = 0;
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
            break;
        case 'd':
            rc.drone_heading_op(0, 1.0);
            break;
        case 'i':
            rc.drone_forward_op(0, 1.0);
            break;
        case 'k':
            rc.drone_forward_op(0, -1.0);
            break;
        case 'j':
            rc.drone_horizontal_op(0, -1.0);
            break;
        case 'l':
            rc.drone_horizontal_op(0, 1.0);
            break;
        case 'x':
            rc.drone_radio_control_button(0, true);
            break;
        case 'p':
            {
                auto pos = rc.get_position(0);
                std::cout << "position x=" << std::fixed << std::setprecision(1) << pos.x << " y=" << pos.y << " z=" << pos.z << std::endl;
            }
            break;
        case 't':
            std::cout << "simtime usec: " << service_container->getSimulationTimeUsec(0) << std::endl;
            break;
        default:
            break;
        }
        rc.run();
        std::this_thread::sleep_for(std::chrono::milliseconds(real_sleep_msec));
    }

    /*
     * Stop service
     */
    service_container->stopService();
    th.join();
    return 0;
}