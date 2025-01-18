#pragma once

#include <memory>

namespace hako::comm {

    typedef enum {
        COMM_IO_TYPE_TCP,
        COMM_IO_TYPE_UDP,
        COMM_IO_TYPE_NUM,
    } CommIoType;

    typedef struct {
        const char *ipaddr;
        int portno;
    } ICommEndpointType;

    class ICommIO {
    public:
        virtual ~ICommIO() = default;
        virtual bool send(const char* data, int datalen, int* send_datalen) = 0;
        virtual bool recv(char* data, int datalen, int* recv_datalen) = 0;
        virtual bool close() = 0;
    };

    class ICommServer {
    public:
        static std::unique_ptr<ICommServer> create(CommIoType type);
        virtual ~ICommServer() = default;
        virtual ICommIO* server_open(ICommEndpointType *endpoint) = 0;
    };

    class ICommClient {
    public:
        virtual ~ICommClient() = default;
        virtual ICommIO* client_open(ICommEndpointType *src, ICommEndpointType *dst) = 0;
    };
    extern int comm_init();

}
