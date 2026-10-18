#pragma once

#include <memory>
#include <cstddef>

namespace hako::comm {

    enum class CommIoType {
        TCP,
        UDP,
        NUM,
    };

    typedef struct {
        const char *ipaddr;
        int portno;
    } ICommEndpointType;

    class ICommIO {
    public:
        virtual ~ICommIO() = default;
        virtual bool send(const char* data, int datalen, int* send_datalen) = 0;
        virtual bool recv(char* data, int datalen, int* recv_datalen) = 0;
        virtual bool recv_latest(char* data, int datalen, int* recv_datalen, std::size_t* dropped_count,
            int min_valid_datalen = 0) {
            (void)min_valid_datalen;
            if (dropped_count) {
                *dropped_count = 0;
            }
            return recv(data, datalen, recv_datalen);
        }
        virtual bool close() = 0;
    };

    class ICommServer {
    public:
        static std::unique_ptr<ICommServer> create(CommIoType type);
        virtual ~ICommServer() = default;
        virtual std::shared_ptr<ICommIO> server_open(ICommEndpointType *endpoint) = 0;
    };

    class ICommClient {
    public:
        static std::unique_ptr<ICommClient> create(CommIoType type);
        virtual ~ICommClient() = default;
        virtual std::shared_ptr<ICommIO> client_open(ICommEndpointType *src, ICommEndpointType *dst) = 0;
    };
    extern int comm_init();

}
