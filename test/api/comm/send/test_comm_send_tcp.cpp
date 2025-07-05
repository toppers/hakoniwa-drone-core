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

std::atomic<bool> serverReady(false);
std::condition_variable cv;
std::mutex cv_m;

// サーバースレッド
void runServer(int portno, int expectedDataLength = 0) {
    hako::comm::ICommEndpointType endpoint;
    endpoint.ipaddr = "127.0.0.1";
    endpoint.portno = portno;

    std::cout << "[TCP] Server starting..." << std::endl;
    {
        std::lock_guard<std::mutex> lk(cv_m);
        serverReady = true;
        cv.notify_all();
    }
    //print endpoint info
    std::cout << "[TCP] Server endpoint: " << endpoint.ipaddr << ":" << endpoint.portno << std::endl;
    serverCommIO = server->server_open(&endpoint);
    ASSERT_NE(serverCommIO, nullptr) << "Server failed to open.";
    std::cout << "[TCP] Server opened." << std::endl;

    if (expectedDataLength > 0) {
        char buffer[256];
        int totalReceivedLen = 0;

        std::cout << "[TCP] Server waiting for data..." << std::endl;
        ASSERT_TRUE(serverCommIO->recv(buffer, expectedDataLength, &totalReceivedLen));
        std::cout << "[TCP] Server received data. totalReceivedLen = " << totalReceivedLen << std::endl;
        
        const char* response = "Response from TCP Server";
        int responseLen = strlen(response);
        std::cout << "[TCP] Server preparing response. responselen = " << responseLen << std::endl;
        int sentLen = 0;
        serverCommIO->send(response, responseLen, &sentLen);
        std::cout << "[TCP] Server sent response." << std::endl;

    }
}

bool initializeCommunication(int portno, int expectedDataLength = 0) {
    if (hako::comm::comm_init() != 0) {
        return false;
    }

    server = hako::comm::ICommServer::create(hako::comm::CommIoType::TCP);
    if (!server) return false;

    std::thread serverThread(runServer, portno, expectedDataLength);
    serverThread.detach();

    std::unique_lock<std::mutex> lk(cv_m);
    cv.wait(lk, [] { return serverReady.load(); });

    client = hako::comm::ICommClient::create(hako::comm::CommIoType::TCP);
    if (!client) return false;

    hako::comm::ICommEndpointType serverEndpoint{"127.0.0.1", portno};
    //hako::comm::ICommEndpointType clientEndpoint{"127.0.0.1", portno + 1000};

    clientCommIO = client->client_open(nullptr, &serverEndpoint);
    EXPECT_NE(clientCommIO, nullptr);
    std::cout << "[TCP] Client opened." << std::endl;
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
}

class CommIOTcpTest : public ::testing::Test {
protected:
    static inline int basePort = 54001;
    int portno = 0;
    void SetUp() override {
        portno = basePort;
    }
    void TearDown() override {
        cleanup();
        serverReady = false;
    }
};
// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST001
TEST_F(CommIOTcpTest, TEST001_ValidData) {
    std::cout << "[TEST001] Starting test with port: " << portno << std::endl;
    const char* data = "Hello TCP Server";
    int datalen = strlen(data);
    ASSERT_TRUE(initializeCommunication(portno, datalen));


    std::cout << "[TEST001] Client initialized, sending data." << std::endl;
    int sentLen = 0;
    ASSERT_TRUE(clientCommIO->send(data, datalen, &sentLen));
    EXPECT_EQ(sentLen, datalen);

    int expected_response_len = strlen("Response from TCP Server");
    char response[256];
    int responseLen = 0;
    std::cout << "[TEST001] Client waiting for response." << std::endl;
    ASSERT_TRUE(clientCommIO->recv(response, expected_response_len, &responseLen));
    EXPECT_GT(responseLen, 0);
    response[responseLen] = '\0'; // Null-terminate the response
    std::cout << "[TEST001] Client received response: " << response << std::endl;
}

#if 0

// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST002
TEST_F(CommIOTcpTest, TEST002_NullDataPointer) {
    ASSERT_TRUE(initializeCommunication(portno, 0));

    const char* data = nullptr;
    int datalen = 10;
    int sentLen = 0;

    EXPECT_FALSE(clientCommIO->send(data, datalen, &sentLen));
    EXPECT_EQ(sentLen, 0);
}

// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST003
TEST_F(CommIOTcpTest, TEST003_NegativeDataLength) {
    ASSERT_TRUE(initializeCommunication(portno, 0));

    const char* data = "Invalid";
    int datalen = -1;
    int sentLen = 0;

    EXPECT_FALSE(clientCommIO->send(data, datalen, &sentLen));
    EXPECT_EQ(sentLen, 0);
}



// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST004
TEST_F(CommIOTcpTest, TEST004_NullSendDataLenPointer) {
    std::cout << "[TEST001] Starting test with port: " << portno << std::endl;
    const char* data = "Hello TCP Server";
    int datalen = strlen(data);
    ASSERT_TRUE(initializeCommunication(portno, datalen));

    //sleep 0.1sec
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    std::cout << "[TEST001] Client initialized, sending data." << std::endl;
    int sentLen = 0;
    ASSERT_TRUE(clientCommIO->send(data, datalen, &sentLen));
    EXPECT_EQ(sentLen, datalen);

    int expected_response_len = strlen("Response from TCP Server");
    char response[256];
    int responseLen = 0;
    std::cout << "[TEST001] Client waiting for response." << std::endl;
    ASSERT_TRUE(clientCommIO->recv(response, expected_response_len, &responseLen));
    EXPECT_GT(responseLen, 0);
    response[responseLen] = '\0'; // Null-terminate the response
    std::cout << "[TEST001] Client received response: " << response << std::endl;    
}

#endif