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
void runServer() {
    hako::comm::ICommEndpointType endpoint;
    endpoint.ipaddr = "127.0.0.1";
    endpoint.portno = 8080;

    serverCommIO = server->server_open(&endpoint);
    ASSERT_NE(serverCommIO, nullptr) << "Server failed to open.";

    {
        std::lock_guard<std::mutex> lk(cv_m);
        serverReady = true;
        cv.notify_all();
    }

    // サーバー側の受信待ち
    const int bufferSize = 256;
    char buffer[bufferSize];
    int receivedLen = 0;

    bool received = serverCommIO->recv(buffer, bufferSize, &receivedLen);
    if (received) {
        std::cout << "Server received data: " << std::string(buffer, receivedLen) << std::endl;
    } else {
        std::cerr << "Server failed to receive data." << std::endl;
    }

    // レスポンスを送信
    const char* response = "Response from Server";
    int responseLen = strlen(response);
    serverCommIO->send(response, responseLen, &receivedLen);
}

// テストの初期化処理
bool initializeCommunication() {
    if (hako::comm::comm_init() != 0) {
        std::cerr << "Initialization failed." << std::endl;
        return false;
    }

    server = hako::comm::ICommServer::create(hako::comm::CommIoType::TCP);
    if (!server) {
        std::cerr << "Failed to create server." << std::endl;
        return false;
    }

    // サーバーを別スレッドで起動
    std::thread serverThread(runServer);
    serverThread.detach();

    // サーバー準備待ち
    std::unique_lock<std::mutex> lk(cv_m);
    cv.wait(lk, [] { return serverReady.load(); });

    client = hako::comm::ICommClient::create(hako::comm::CommIoType::TCP);
    if (!client) {
        std::cerr << "Failed to create client." << std::endl;
        return false;
    }

    hako::comm::ICommEndpointType serverEndpoint;
    serverEndpoint.ipaddr = "127.0.0.1";
    serverEndpoint.portno = 8080;

    hako::comm::ICommEndpointType clientEndpoint;
    clientEndpoint.ipaddr = "127.0.0.1";
    clientEndpoint.portno = 8081;

    clientCommIO = client->client_open(&clientEndpoint, &serverEndpoint);
    if (!clientCommIO) {
        std::cerr << "Failed to connect to server." << std::endl;
        return false;
    }

    return true;
}

// テスト終了時のクリーンアップ処理
void cleanup() {
    if (clientCommIO) {
        clientCommIO->close();
    }
    if (serverCommIO) {
        serverCommIO->close();
    }
}

class CommIOTest : public ::testing::Test {
protected:
    void SetUp() override {
        ASSERT_TRUE(initializeCommunication());
    }
    void TearDown() override {
        cleanup();
    }
};

// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST001
TEST_F(CommIOTest, TEST001_ValidData) {
    const char* data = "Hello Server";
    int datalen = strlen(data);
    int sentLen = 0;

    ASSERT_TRUE(clientCommIO->send(data, datalen, &sentLen));
    EXPECT_EQ(sentLen, datalen);

    char response[256];
    int responseLen = 0;

    ASSERT_TRUE(clientCommIO->recv(response, 256, &responseLen));
    EXPECT_GT(responseLen, 0);
    std::cout << "Client received response: " << std::string(response, responseLen) << std::endl;
}

// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST002
TEST_F(CommIOTest, TEST002_NullDataPointer) {
    const char* data = nullptr;
    int datalen = 10;
    int sentLen = 0;

    EXPECT_FALSE(clientCommIO->send(data, datalen, &sentLen));
    EXPECT_EQ(sentLen, 0);
}

// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST003
TEST_F(CommIOTest, TEST003_NegativeDataLength) {
    const char* data = "Invalid";
    int datalen = -1;
    int sentLen = 0;

    EXPECT_FALSE(clientCommIO->send(data, datalen, &sentLen));
    EXPECT_EQ(sentLen, 0);
}

// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST004
TEST_F(CommIOTest, TEST004_NullSendDataLenPointer) {
    const char* data = "Hello";
    int datalen = 5;
    int* sentLen = nullptr;

    EXPECT_FALSE(clientCommIO->send(data, datalen, sentLen));
}
