#include "comm.hpp"
#include <iostream>
#include <cstring>
#include <cstdlib>

int main() {
    if (hako::comm::comm_init() != 0) {
        std::cerr << "comm_init failed" << std::endl;
        return 1;
    }

    auto server = hako::comm::ICommServer::create(hako::comm::CommIoType::UDP);
    if (!server) {
        std::cerr << "failed to create server" << std::endl;
        return 1;
    }

    int port = 60000;
    if (const char* p = std::getenv("PORT")) {
        port = std::atoi(p);
    }
    hako::comm::ICommEndpointType ep{"0.0.0.0", port};

    auto io = server->server_open(&ep);
    if (!io) {
        std::cerr << "server_open failed" << std::endl;
        return 1;
    }

    while (true) {

        char buf[256]{};
        int recvLen = 0;
        if (!io->recv(buf, sizeof(buf), &recvLen)) {
            std::cerr << "recv failed" << std::endl;
            continue;
        }
        std::string msg(buf, recvLen);
        std::cout << "Server received: " << msg << std::endl;

        const char *resp = "ACK";
        int sent = 0;
        io->send(resp, static_cast<int>(strlen(resp)), &sent);

        if (msg == "SHUTDOWN") {
            break;
        }
    }
    io->close();
    return 0;
}
