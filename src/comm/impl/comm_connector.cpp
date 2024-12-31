#include "impl/tcp_connector.hpp"
#include "impl/udp_connector.hpp"

using namespace hako::comm;

std::unique_ptr<ICommServer> hako::comm::ICommServer::create(CommIoType type)
{
    if (type == COMM_IO_TYPE_TCP) {
        return std::make_unique<hako::comm::impl::TcpServer>();
    }
    else if (type == COMM_IO_TYPE_UDP) {
        return std::make_unique<hako::comm::impl::UdpServer>();
    }
    else {
        throw std::runtime_error("Invalid type: " + std::to_string(static_cast<int>(type)));
    }
}


#ifdef WIN32
int hako::comm::comm_init()
{
    WSADATA wsaData;
    int result = WSAStartup(MAKEWORD(2, 2), &wsaData);
    if (result != 0) {
        std::cerr << "WSAStartup failed: " << result << std::endl;
        return -1;
    }
    return 0;
}
#else
int hako::comm::comm_init()
{
    return 0;
}
#endif
