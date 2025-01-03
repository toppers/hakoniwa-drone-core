#include "udp_connector.hpp"
#include <cstring>

#ifdef _WIN32
#define close_socket closesocket
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#else
#define close_socket ::close
#include <unistd.h>
#include <arpa/inet.h>
#endif
#include <iostream>

namespace hako::comm::impl {

UdpCommIO::UdpCommIO(ICOMM_SOCKET sockfd, const sockaddr_in& remote_addr) : sockfd(sockfd), remote_addr_(remote_addr) 
{
}
UdpCommIO::~UdpCommIO() {
    close();
}

bool UdpCommIO::recv(char* data, int datalen, int* recv_datalen) {
    if(sockfd < 0 || !data || datalen <= 0) return false;
    socklen_t addr_len = sizeof(remote_addr_);
    struct sockaddr_in addr;
    int bytes_received = recvfrom(sockfd, data, datalen, 0, (struct sockaddr*)&addr, &addr_len);
    if(bytes_received < 0) {
        return false;
    }
    {
        std::lock_guard<std::mutex> lock(mtx_);
        remote_addr_ = addr;
    }

    //std::cout << "recv sockfd: " << sockfd << std::endl;
    //std::cout << "Received message from " << inet_ntoa(remote_addr_.sin_addr) << ":" << ntohs(remote_addr_.sin_port) << std::endl;
    if(recv_datalen) {
        *recv_datalen = bytes_received;
    }

    return true;
}

bool UdpCommIO::send(const char* data, int datalen, int* send_datalen) {
    //std::cout << "send sockfd: " << sockfd << std::endl;
    //std::cout << "Remote  " << inet_ntoa(remote_addr_.sin_addr) << ":" << ntohs(remote_addr_.sin_port) << std::endl;
    if(sockfd < 0 || !data || datalen <= 0) return false;
    struct sockaddr_in addr;
    {
        std::lock_guard<std::mutex> lock(mtx_);
        addr = remote_addr_;
    }
    if (!addr.sin_port || !addr.sin_addr.s_addr) {
        std::cerr << "Remote address is not set" << std::endl;
        return false;
    }
    int bytes_sent = sendto(sockfd, data, datalen, 0, (struct sockaddr*)&remote_addr_, sizeof(remote_addr_));
    if(bytes_sent < 0) {
        return false;
    }

    if(send_datalen) {
        *send_datalen = bytes_sent;
    }

    return true;
}

bool UdpCommIO::close() {
#ifdef _WIN32
#else
    ::shutdown(sockfd, SHUT_RDWR);
#endif
    if(sockfd >= 0) {
        close_socket(sockfd);
        sockfd = -1;
    }
    return true;
}

UdpClient::UdpClient() {
    #ifdef _WIN32
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);
    #endif
    std::memset(&local_addr, 0, sizeof(local_addr));
}

UdpClient::~UdpClient() {
    #ifdef _WIN32
    WSACleanup();
    #endif
}

ICommIO* UdpClient::client_open(ICommEndpointType* src, ICommEndpointType* dst) {
    if (dst == nullptr) {
        std::cerr << "Invalid destination endpoint" << std::endl;
        return nullptr;
    }

#ifdef _WIN32
    ICOMM_SOCKET sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd == INVALID_SOCKET) {
        std::cerr << "Failed to create socket: " << WSAGetLastError() << std::endl;
        return nullptr;
    }
#else
    ICOMM_SOCKET sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        std::cerr << "Failed to create socket: " << strerror(errno) << std::endl;
        return nullptr;
    }
#endif

    struct sockaddr_in local_addr;
    memset(&local_addr, 0, sizeof(local_addr));
    local_addr.sin_family = AF_INET;

    if (src != nullptr) {
        local_addr.sin_port = htons(src->portno);
        if (inet_pton(AF_INET, src->ipaddr, &local_addr.sin_addr) <= 0) {
            std::cerr << "Invalid source IP address: " << src->ipaddr << std::endl;
            close_socket(sockfd);
            return nullptr;
        }
    } else {
        local_addr.sin_port = 0;
        local_addr.sin_addr.s_addr = INADDR_ANY;
    }

    if (bind(sockfd, (struct sockaddr*)&local_addr, sizeof(local_addr)) < 0) {
#ifdef _WIN32
        char error_msg[256];
        strerror_s(error_msg, sizeof(error_msg), errno);
        std::cerr << "Failed to bind socket: " << error_msg << std::endl;
#else
        std::cerr << "Failed to bind socket: " << strerror(errno) << std::endl;
#endif
        close_socket(sockfd);
        return nullptr;
    }

    struct sockaddr_in remote_addr;
    memset(&remote_addr, 0, sizeof(remote_addr));
    remote_addr.sin_family = AF_INET;
    remote_addr.sin_port = htons(dst->portno);
    if (inet_pton(AF_INET, dst->ipaddr, &remote_addr.sin_addr) <= 0) {
        std::cerr << "Invalid destination IP address: " << dst->ipaddr << std::endl;
        close_socket(sockfd);
        return nullptr;
    }

    return new UdpCommIO(sockfd, remote_addr);
}


UdpServer::UdpServer() {
    #ifdef _WIN32
    WSADATA wsaData;
    WSAStartup(MAKEWORD(2, 2), &wsaData);
    #endif
    std::memset(&local_addr, 0, sizeof(local_addr));
}

UdpServer::~UdpServer() {
    #ifdef _WIN32
    WSACleanup();
    #endif
}

ICommIO* UdpServer::server_open(ICommEndpointType *endpoint) {
#ifdef _WIN32
    ICOMM_SOCKET sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if(sockfd == INVALID_SOCKET) {
        return nullptr;
    }
#else
    ICOMM_SOCKET sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if(sockfd < 0) {
        return nullptr;
    }
#endif
    local_addr.sin_family = AF_INET;
    local_addr.sin_port = htons(endpoint->portno);
    inet_pton(AF_INET, endpoint->ipaddr, &(local_addr.sin_addr));

    if(bind(sockfd, (struct sockaddr *)&local_addr, sizeof(local_addr)) < 0) {
        close_socket(sockfd);
        return nullptr;
    }

    return new UdpCommIO(sockfd);
}

} // namespace hako::comm
