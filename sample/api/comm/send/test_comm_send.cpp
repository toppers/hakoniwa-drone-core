#include <gtest/gtest.h>
#include <thread>
#include <memory>
#include <atomic>
#include <condition_variable>
#include "comm.hpp" // Include your provided comm.hpp file

std::unique_ptr<hako::comm::ICommServer> server;
std::unique_ptr<hako::comm::ICommIO> serverCommIO;
std::unique_ptr<hako::comm::ICommClient> client;
std::unique_ptr<hako::comm::ICommIO> clientCommIO;

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

    server = hako::comm::ICommServer::create(hako::comm::COMM_IO_TYPE_TCP);
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

    client = hako::comm::ICommClient::create(hako::comm::COMM_IO_TYPE_TCP);
    if (!client) {
        std::cerr << "Failed to create client." << std::endl;
        return false;
    }

    hako::comm::ICommEndpointType serverEndpoint;
    serverEndpoint.ipaddr = "127.0.0.1";
    serverEndpoint.portno = 8080;

    clientCommIO = client->client_open(&serverEndpoint);
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

// TEST001: クライアントからサーバーへの正常なデータ送信
TEST(ICommIOTest, TEST001_ValidData) {
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

// TEST002: クライアントからNULLデータ送信時のエラー処理
TEST(ICommIOTest, TEST002_NullDataPointer) {
    const char* data = nullptr;
    int datalen = 10;
    int sentLen = 0;

    EXPECT_FALSE(clientCommIO->send(data, datalen, &sentLen));
    EXPECT_EQ(sentLen, 0);
}

// TEST003: クライアントから負のデータ長送信時のエラー処理
TEST(ICommIOTest, TEST003_NegativeDataLength) {
    const char* data = "Invalid";
    int datalen = -1;
    int sentLen = 0;

    EXPECT_FALSE(clientCommIO->send(data, datalen, &sentLen));
    EXPECT_EQ(sentLen, 0);
}

// TEST004: NULLポインタをsend_datalenに指定した場合のエラー処理
TEST(ICommIOTest, TEST004_NullSendDataLenPointer) {
    const char* data = "Hello";
    int datalen = 5;
    int* sentLen = nullptr;

    EXPECT_FALSE(clientCommIO->send(data, datalen, sentLen));
}
