#pragma once

#include "comm/icomm_connector.hpp"
#include "impl/icomm_osdep.hpp"

namespace hako::comm::impl {

class TcpCommIO : public ICommIO {
private:
    ICOMM_SOCKET sockfd;
public:
    TcpCommIO(ICOMM_SOCKET sockfd);
    ~TcpCommIO() override;

    bool send(const char* data, int datalen, int* send_datalen) override;
    bool recv(char* data, int datalen, int* recv_datalen) override;
    bool close() override;
};

class TcpClient : public ICommClient {
private:

public:
    TcpClient();
    ~TcpClient() override;

    ICommIO* client_open(ICommEndpointType *src, ICommEndpointType *dst) override;
};

class TcpServer : public ICommServer {
private:

public:
    TcpServer();
    ~TcpServer() override;

    ICommIO* server_open(ICommEndpointType *endpoint) override;
};


}

