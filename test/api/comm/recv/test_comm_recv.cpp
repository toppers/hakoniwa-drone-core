#include <gtest/gtest.h>
#include <thread>
#include <memory>
#include <atomic>
#include <condition_variable>
#include "comm.hpp"

static std::unique_ptr<hako::comm::ICommServer> server;
static std::shared_ptr<hako::comm::ICommIO> serverCommIO;
static std::unique_ptr<hako::comm::ICommClient> client;
static std::shared_ptr<hako::comm::ICommIO> clientCommIO;
static std::thread serverThread;

std::atomic<bool> serverReady(false);
std::condition_variable cv;
std::mutex cv_m;

// サーバーを別スレッドで起動し、クライアントからのデータを受信後に返信する
void runServer(int portno) {
    hako::comm::ICommEndpointType endpoint;
    endpoint.ipaddr = "127.0.0.1";
    endpoint.portno = portno;

    std::cout << "Server is starting open..." << std::endl;
    serverCommIO = server->server_open(&endpoint);
    ASSERT_NE(serverCommIO, nullptr) << "Server failed to open.";

    std::cout << "Server opened connection." << std::endl;

    const int bufferSize = 256;
    char buffer[bufferSize];
    int recvLen = 0;

    {
        std::lock_guard<std::mutex> lk(cv_m);
        serverReady = true;
        std::cout << "Notifying server thread started." << std::endl;
        cv.notify_all();
    }

    std::cout << "Server is waiting to receive data..." << std::endl;
    bool received = serverCommIO->recv(buffer, bufferSize, &recvLen);
    if (received) {
        std::cout << "Server received data: " << std::string(buffer, recvLen) << std::endl;
    } else {
        std::cerr << "Server failed to receive data." << std::endl;
    }

    if (received) {
        const char* message = "Response from Server";
        int messageLen = strlen(message);
        serverCommIO->send(message, messageLen, &recvLen);
        std::cout << "Server sent response: " << message << std::endl;
    }
    std::cout << "Server thread finished." << std::endl;
}

bool initializeCommunication(int portno) {
    if (hako::comm::comm_init() != 0) {
        std::cerr << "Initialization failed." << std::endl;
        return false;
    }

    server = hako::comm::ICommServer::create(hako::comm::CommIoType::UDP);
    if (!server) {
        std::cerr << "Failed to create server." << std::endl;
        return false;
    }

    serverThread = std::thread(runServer, portno);

    client = hako::comm::ICommClient::create(hako::comm::CommIoType::UDP);
    if (!client) {
        std::cerr << "Failed to create client." << std::endl;
        return false;
    }

    hako::comm::ICommEndpointType serverEndpoint;
    serverEndpoint.ipaddr = "127.0.0.1";
    serverEndpoint.portno = portno;

    hako::comm::ICommEndpointType clientEndpoint;
    clientEndpoint.ipaddr = "127.0.0.1";
    clientEndpoint.portno = portno + 100;

    std::cout << "Client: Connecting to server at "
              << serverEndpoint.ipaddr << ":" << serverEndpoint.portno << std::endl;
    clientCommIO = client->client_open(&clientEndpoint, &serverEndpoint);
    if (!clientCommIO) {
        std::cerr << "Failed to connect to server." << std::endl;
        return false;
    }

    std::unique_lock<std::mutex> lk(cv_m);
    cv.wait(lk, [] { return serverReady.load(); });

    std::cout << "Client connected to server." << std::endl;
    return true;
}

void cleanup() {
    if (clientCommIO) {
        std::cout << "Closing client communication IO." << std::endl;
        clientCommIO->close();
    }
    if (serverCommIO) {
        std::cout << "Closing server communication IO." << std::endl;
        serverCommIO->close();
    }
    if (serverThread.joinable()) {
        serverThread.join();
    }
}

class CommIORecvTest : public ::testing::Test {
protected:
    static inline int basePort = 8200;
    int portno;
    void SetUp() override {
        portno = basePort++;
        ASSERT_TRUE(initializeCommunication(portno));
    }
    void TearDown() override {
        cleanup();
    }
};

// SPEC: docs/test/comm/io/test_comm_io_recv.md#TEST001
TEST_F(CommIORecvTest, TEST001_ReceiveSuccess) {
    const char* data = "Hello Server";
    int datalen = strlen(data);
    int sentLen = 0;
    ASSERT_TRUE(clientCommIO->send(data, datalen, &sentLen));

    char buffer[256];
    int recvLen = 0;
    ASSERT_TRUE(clientCommIO->recv(buffer, sizeof(buffer), &recvLen));
    EXPECT_GT(recvLen, 0);
    std::cout << "Client received: " << std::string(buffer, recvLen) << std::endl;

    const char* resp = "Ack";
    int respLen = strlen(resp);
    clientCommIO->send(resp, respLen, &sentLen);
}

// SPEC: docs/test/comm/io/test_comm_io_recv.md#TEST002
TEST_F(CommIORecvTest, TEST002_NullDataPointer) {
    char* buffer = nullptr;
    int recvLen = 0;
    EXPECT_FALSE(clientCommIO->recv(buffer, 10, &recvLen));
    EXPECT_EQ(recvLen, 0);
    const char* dummy = "dummy";
    int sentLen = 0;
    clientCommIO->send(dummy, strlen(dummy), &sentLen);
}

// SPEC: docs/test/comm/io/test_comm_io_recv.md#TEST003
TEST_F(CommIORecvTest, TEST003_NegativeDataLength) {
    char buffer[10];
    int recvLen = 0;
    EXPECT_FALSE(clientCommIO->recv(buffer, -1, &recvLen));
    EXPECT_EQ(recvLen, 0);
    const char* dummy = "dummy";
    int sentLen = 0;
    clientCommIO->send(dummy, strlen(dummy), &sentLen);
}

// SPEC: docs/test/comm/io/test_comm_io_recv.md#TEST004
TEST_F(CommIORecvTest, TEST004_NullRecvDataLenPointer) {
    char buffer[10];
    int* recvLen = nullptr;
    EXPECT_FALSE(clientCommIO->recv(buffer, 10, recvLen));
    const char* dummy = "dummy";
    int sentLen = 0;
    clientCommIO->send(dummy, strlen(dummy), &sentLen);
}

