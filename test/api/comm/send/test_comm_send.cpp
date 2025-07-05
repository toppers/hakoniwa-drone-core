#include <gtest/gtest.h>
#include <thread>
#include <memory>
#include <atomic>
#include <condition_variable>
#include "comm.hpp" // Include your provided comm.hpp file

static std::unique_ptr<hako::comm::ICommServer> server;
static std::shared_ptr<hako::comm::ICommIO> serverCommIO;
static std::unique_ptr<hako::comm::ICommClient> client;
static std::shared_ptr<hako::comm::ICommIO> clientCommIO;

std::atomic<bool> serverReady(false);
std::condition_variable cv;
std::mutex cv_m;

// サーバーを別スレッドで起動し、受信待機を行う
void runServer(int portno) {

    hako::comm::ICommEndpointType endpoint;
    endpoint.ipaddr = "127.0.0.1";
    endpoint.portno = portno;

    std::cout << "Server is starting open..." << std::endl;
    serverCommIO = server->server_open(&endpoint);
    ASSERT_NE(serverCommIO, nullptr) << "Server failed to open.";

    std::cout << "Server opened connection." << std::endl;

    // サーバー側の受信待ち
    const int bufferSize = 256;
    char buffer[bufferSize];
    int receivedLen = 0;

    {
        std::lock_guard<std::mutex> lk(cv_m);
        serverReady = true;
        std::cout << "Notifying server thread started." << std::endl;
        cv.notify_all();
    }
    std::cout << "Server is waiting to receive data..." << std::endl;
    bool received = serverCommIO->recv(buffer, bufferSize, &receivedLen);
    if (received) {
        std::cout << "Server received data: " << std::string(buffer, receivedLen) << std::endl;
    } else {
        std::cerr << "Server failed to receive data." << std::endl;
    }

    const char* response = "Response from Server";
    int responseLen = strlen(response);
    serverCommIO->send(response, responseLen, &receivedLen);
    std::cout << "Server sent response: " << response << std::endl;
    std::cout << "Server thread finished." << std::endl;
}


// テストの初期化処理
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

    // サーバーを別スレッドで起動
    //set argument for portno on runServer
    std::thread serverThread(runServer, portno);
    serverThread.detach();


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
    // サーバー準備待ち
    std::unique_lock<std::mutex> lk(cv_m);
    cv.wait(lk, [] { return serverReady.load(); });

    std::cout << "Client connected to server." << std::endl;

    return true;
}

// テスト終了時のクリーンアップ処理
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

class CommIOTest : public ::testing::Test {
protected:
    static inline int basePort = 18080;
    int portno;
    void SetUp() override {
        portno = basePort++;
        ASSERT_TRUE(initializeCommunication(portno));
    }
    void TearDown() override {
        cleanup();
    }
};

// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST001
TEST_F(CommIOTest, TEST001_ValidData) {
    std::cout << "TEST001: Sending valid data from client to server." << std::endl;
    const char* data = "Hello Server";
    int datalen = strlen(data);
    int sentLen = 0;

    ASSERT_TRUE(clientCommIO->send(data, datalen, &sentLen));
    std::cout << "Client sent data: " << data << std::endl;
    EXPECT_EQ(sentLen, datalen);

    char response[256];
    int responseLen = 0;

    ASSERT_TRUE(clientCommIO->recv(response, 256, &responseLen));
    EXPECT_GT(responseLen, 0);
    std::cout << "Client received response: " << std::string(response, responseLen) << std::endl;
}

// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST002
TEST_F(CommIOTest, TEST002_NullDataPointer) {
    std::cout << "TEST002: Sending null data pointer." << std::endl;
    const char* data = nullptr;
    int datalen = 10;
    int sentLen = 0;

    EXPECT_FALSE(clientCommIO->send(data, datalen, &sentLen));
    EXPECT_EQ(sentLen, 0);
}

// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST003
TEST_F(CommIOTest, TEST003_NegativeDataLength) {
    std::cout << "TEST003: Sending data with negative length." << std::endl;
    const char* data = "Invalid";
    int datalen = -1;
    int sentLen = 0;

    EXPECT_FALSE(clientCommIO->send(data, datalen, &sentLen));
    EXPECT_EQ(sentLen, 0);
}

// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST004
TEST_F(CommIOTest, TEST004_NullSendDataLenPointer) {
    std::cout << "TEST004: Sending data with null sent length pointer." << std::endl;
    const char* data = "Hello";
    int datalen = 5;
    int* sentLen = nullptr;

    EXPECT_TRUE(clientCommIO->send(data, datalen, sentLen));
}
