#include "service/aircraft/impl/aircraft_service.hpp"
#include "logger/impl/hako_logger.hpp"

using namespace hako::service;
using namespace hako::logger;


int main(int argc, const char* argv[])
{
    const char* server_ip = "127.0.0.1";
    const int server_port = 4560;

    // MAVLINK サーバーの設定
    IcommEndpointType server_endpoint = {server_ip, server_port};
    auto mavlink_service = MavLinkService(0, MAVLINK_SERVICE_IO_TYPE_TCP, &server_endpoint, nullptr);
    MavLinkServiceContainer mavlink_service_container;
    mavlink_service_container.addService(mavlink_service);

    // Aircraft サービスの設定
    DroneConfigManager configManager;
    configManager.loadConfigsFromDirectory("./drone_config");

    AirCraftContainer aircraft_container;
    aircraft_container.createAirCrafts(configManager);

    auto aircraft_service = std::make_unique<hako::service::impl::AircraftService>(mavlink_service_container, aircraft_container);
    aircraft_service->startService(true, 3000);
    HakoLogger::enable();

    while (true) {
        uint64_t time_usec = aircraft_service->getSimulationTimeUsec(0);
        HakoLogger::set_time_usec(time_usec);
        std::cout << "INFO: simulation time(usec)=" << time_usec << std::endl;
        aircraft_service->advanceTimeStep(0);
        //sleep 3msec
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    return 0;
}