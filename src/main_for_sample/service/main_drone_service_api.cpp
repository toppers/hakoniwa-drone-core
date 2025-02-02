#include "service.hpp"
#include <iostream>
#include <thread>
#include <sstream>
#include <vector>
#include <string>

using namespace hako::aircraft;
using namespace hako::controller;
using namespace hako::service;
using namespace hako::logger;
using namespace hako::config;


static std::vector<std::string> split_by_space(const std::string& str) {
    std::istringstream iss(str);
    std::vector<std::string> result;
    std::string word;

    while (iss >> word) {
        result.push_back(word);
    }

    return result;
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

    DroneConfigManager configManager;
    configManager.loadConfigsFromDirectory(drone_config_dir_path);

    auto aircraft_container = IAirCraftContainer::create();
    aircraft_container->createAirCrafts(configManager);

    std::shared_ptr<IAircraftControllerContainer> controller_container = IAircraftControllerContainer::create();
    controller_container->createAircraftControllers(configManager, false);

    std::shared_ptr<IDroneServiceContainer> service_container = IDroneServiceContainer::create(aircraft_container, controller_container);

    auto ret = service_container->startService(1000);
    if (!ret) {
        std::cerr << "Failed to start service" << std::endl;
        return 1;
    }
    std::thread th([&service_container, real_sleep_msec]() {
        std::cout << "Start service" << std::endl;
        while (service_container->isServiceAvailable()) {
            IHakoLogger::set_time_usec(service_container->getSimulationTimeUsec(0));
            service_container->advanceTimeStep();
            std::this_thread::sleep_for(std::chrono::milliseconds(real_sleep_msec));
        }
        std::cout << "Finish service" << std::endl;
    });
    DroneServiceApiProtocol api(service_container);

    while (true) {
        std::cout << "> ";

        std::string line;
        std::getline(std::cin, line);
        std::vector<std::string> words = split_by_space(line);
        if (line.find("takeoff") == 0) {
            if (words.size() < 2) {
                std::cout << "Usage: takeoff <height>" << std::endl;
                continue;
            }
            float height = std::stof(words[1]);
            api.takeoff(0, height);
        }
        else if (line.find("land") == 0) {
            api.land(0);
        }
        else if (line.find("move") == 0) {
            float x, y, z;
            if (words.size() < 4) {
                std::cout << "Usage: move <x> <y> <z>" << std::endl;
                continue;
            }
            std::sscanf(line.c_str(), "move %f %f %f", &x, &y, &z);
            api.move(0, x, y, z);
        }
        else if (line.find("pos") == 0) {
            auto pos = api.get_position(0);
            std::cout << "position x=" << std::fixed << std::setprecision(1) << pos.x << " y=" << pos.y << " z=" << pos.z << std::endl;
        }
        else if (line.find("quit") == 0) {
            break;
        }
        else {
            std::cout << "Usage: takeoff <height> | land | move <x> <y> <z> | quit" << std::endl;
        }
    }
    service_container->stopService();
    th.join();
    return 0;
}