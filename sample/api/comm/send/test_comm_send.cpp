#include <gtest/gtest.h>
#include <thread>
#include <chrono>
#include <memory>
#include "comm.hpp"

namespace hako::comm::test {

class CommSendTest : public ::testing::Test {
protected:
    std::unique_ptr<ICommServer> server_;
    std::unique_ptr<ICommClient> client_;
    ICommIO* server_io_;
    ICommIO* client_io_;
    std::thread server_thread_;
    
    void SetUp() override {
        // 通信初期化
        ASSERT_EQ(0, comm_init());
        
        // サーバー作成
        server_ = ICommServer::create(COMM_IO_TYPE_TCP);
        ASSERT_NE(nullptr, server_);
        
        // クライアント作成
        client_ = ICommClient::create(COMM_IO_TYPE_TCP);
        ASSERT_NE(nullptr, client_);
        
        // サーバーエンドポイント設定
        ICommEndpointType server_endpoint = {
            .ipaddr = "127.0.0.1",
            .portno = 8080
        };
        
        // サーバースレッド起動
        server_thread_ = std::thread([this, server_endpoint]() {
            server_io_ = server_->server_open(&server_endpoint);
        });
        
        // サーバー起動待ち
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        
        // クライアント接続
        ICommEndpointType client_src = {
            .ipaddr = "127.0.0.1",
            .portno = 0  // 自動割当
        };
        ICommEndpointType client_dst = {
            .ipaddr = "127.0.0.1",
            .portno = 8080
        };
        client_io_ = client_->client_open(&client_src, &client_dst);
        ASSERT_NE(nullptr, client_io_);
    }
    
    void TearDown() override {
        if (client_io_) {
            client_io_->close();
        }
        if (server_io_) {
            server_io_->close();
        }
        if (server_thread_.joinable()) {
            server_thread_.join();
        }
    }
};

TEST_F(CommSendTest, TEST001_NormalCase) {
    // Arrange
    const char* test_data = "test data";
    int datalen = 9;
    int send_datalen = 0;
    
    // Act
    bool result = client_io_->send(test_data, datalen, &send_datalen);
    
    // Assert
    EXPECT_TRUE(result);
    EXPECT_GT(send_datalen, 0);
    EXPECT_LE(send_datalen, datalen);
}

TEST_F(CommSendTest, TEST002_NullDataPointer) {
    // Arrange
    int datalen = 10;
    int send_datalen = 0;
    
    // Act
    bool result = client_io_->send(nullptr, datalen, &send_datalen);
    
    // Assert
    EXPECT_FALSE(result);
    EXPECT_EQ(send_datalen, 0);
}

TEST_F(CommSendTest, TEST003_NegativeDataLength) {
    // Arrange
    const char* test_data = "test data";
    int datalen = -1;
    int send_datalen = 0;
    
    // Act
    bool result = client_io_->send(test_data, datalen, &send_datalen);
    
    // Assert
    EXPECT_FALSE(result);
    EXPECT_EQ(send_datalen, 0);
}

TEST_F(CommSendTest, TEST004_NullSendDataLen) {
    // Arrange
    const char* test_data = "test data";
    int datalen = 10;
    
    // Act
    bool result = client_io_->send(test_data, datalen, nullptr);
    
    // Assert
    EXPECT_FALSE(result);
}

}  // namespace hako::comm::test