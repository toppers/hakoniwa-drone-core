#include "service.hpp"

using namespace hako::service;
using namespace hako::aircraft;
using namespace hako::mavlink;
using namespace hako::logger;
using namespace hako::config;

int main(int argc, const char* argv[])
{
    const char* server_ip = "127.0.0.1";
    const int server_port = 4560;

    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << "<real_sleep_msec> <drone_config_dir_path>" << std::endl;
        return 1;
    }
    int real_sleep_msec = std::stoi(argv[1]);
    const char* drone_config_dir_path = argv[2];

    IHakoLogger::enable();
    DroneConfigManager configManager;
    configManager.loadConfigsFromDirectory(drone_config_dir_path);
    int aircraft_num = configManager.getConfigCount();

    auto aircraft_container = IAirCraftContainer::create();
    aircraft_container->createAirCrafts(configManager);
    auto mavlink_service_container = std::make_shared<MavLinkServiceContainer>();
    for (int i = 0; i < aircraft_num; i++) {
        std::cout << "INFO: aircraft_num=" << i << std::endl;
        IMavlinkCommEndpointType server_endpoint = {server_ip, server_port + i};
        auto mavlink_service = IMavLinkService::create(i, MavlinkServiceIoType::TCP, &server_endpoint, nullptr);
        mavlink_service_container->addService(mavlink_service);
    }

    auto aircraft_service = IAircraftServiceContainer::create(mavlink_service_container, aircraft_container);
    aircraft_service->startService(true, 3000);

    aircraft_service->setRealTimeStepUsec(real_sleep_msec * 1000);

    while (true) {
        IHakoLogger::set_time_usec(aircraft_service->getSitlTimeUsec(0));
        aircraft_service->advanceTimeStep();
    }
    return 0;
}