// CommIO UDP Receive Tests – Minimal
// -----------------------------------------------------------------------------
// UDP 受信 API のみを検証するテストファイル。
// TCP との共通化や Send テストは含めません。
//
// Build example:
//   add_executable(comm_io_udp_recv_tests CommIOUdpRecvTests.cpp)
//   target_link_libraries(comm_io_udp_recv_tests PRIVATE gtest_main hako_comm)

#include <gtest/gtest.h>
#include <thread>
#include <memory>
#include <atomic>
#include <condition_variable>
#include "comm.hpp"

namespace {
using hako::comm::ICommClient;
using hako::comm::ICommEndpointType;
using hako::comm::ICommIO;
using hako::comm::ICommServer;
using hako::comm::CommIoType;

// -----------------------------------------------------------------------------
// シンプルな UDP テストサーバ
//   - 最初の datagram を受信したら固定レスポンスを返して終了。
// -----------------------------------------------------------------------------
class UdpTestServer {
public:
    explicit UdpTestServer(int port) : port_{port}
    {
        server_ = ICommServer::create(CommIoType::UDP);
        if (!server_) throw std::runtime_error("UdpTestServer: create failed");
        thr_ = std::thread(&UdpTestServer::run, this);
        std::unique_lock lk(m_);
        cv_.wait(lk, [this] { return ready_.load(); });
    }
    ~UdpTestServer()
    {
        if (io_) io_->close();
        if (thr_.joinable()) thr_.join();
    }

    static constexpr const char *kResp = "Response from UDP Server";

private:
    void run()
    {
        ICommEndpointType ep{"127.0.0.1", port_};
        io_ = server_->server_open(&ep);
        ASSERT_NE(io_, nullptr);
        {
            std::lock_guard lg(m_);
            ready_ = true;
            cv_.notify_all();
        }
        char buf[256]{};
        int  recvLen = 0;
        if (!io_->recv(buf, sizeof(buf), &recvLen)) return; // wait for first packet
        int sent = 0;
        io_->send(kResp, static_cast<int>(strlen(kResp)), &sent);
    }

    int                           port_;
    std::unique_ptr<ICommServer>  server_;
    std::shared_ptr<ICommIO>      io_;
    std::thread                   thr_;
    std::atomic<bool>             ready_{false};
    std::condition_variable       cv_;
    std::mutex                    m_;
};

// -----------------------------------------------------------------------------
// テストスイート (Receive 専用)
// -----------------------------------------------------------------------------
class CommIOUdpRecvTest : public ::testing::Test {
protected:
    static void SetUpTestSuite() { ASSERT_EQ(hako::comm::comm_init(), 0); }

    static inline int nextPort_ = 56001;
    int                              port_{};
    std::unique_ptr<UdpTestServer>   server_;
    std::shared_ptr<ICommIO>         clientIO_;

    void SetUp() override
    {
        port_   = nextPort_++;
        server_ = std::make_unique<UdpTestServer>(port_);

        // クライアント側ソケット生成（送信元ポート 0: OS 任せ）
        auto client = ICommClient::create(CommIoType::UDP);
        ASSERT_NE(client, nullptr);

        ICommEndpointType src{"127.0.0.1", 0};
        ICommEndpointType dst{"127.0.0.1", port_};
        clientIO_ = client->client_open(&src, &dst);
        ASSERT_NE(clientIO_, nullptr);
    }
    void TearDown() override
    {
        if (clientIO_) clientIO_->close();
        server_.reset();
    }
};

// SPEC: docs/test/comm/io/test_comm_io_recv.md#TEST001
TEST_F(CommIOUdpRecvTest, ReceiveSuccess)
{
    constexpr char kMsg[] = "Hello Server";
    int sent = 0;
    ASSERT_TRUE(clientIO_->send(kMsg, static_cast<int>(strlen(kMsg)), &sent));

    char buf[256]{};
    int  recvLen = 0;
    ASSERT_TRUE(clientIO_->recv(buf, sizeof(buf), &recvLen));
    buf[recvLen] = '\0';
    EXPECT_STREQ(buf, UdpTestServer::kResp);

    // optional Ack back to server (not verified)
    constexpr char kAck[] = "Ack";
    clientIO_->send(kAck, static_cast<int>(strlen(kAck)), &sent);
}

// SPEC: docs/test/comm/io/test_comm_io_recv.md#TEST002
TEST_F(CommIOUdpRecvTest, NullDataPointer)
{
    // まずサーバが応答できるようダミー送信
    constexpr char kHello[] = "Ping";
    int sent = 0;
    clientIO_->send(kHello, static_cast<int>(strlen(kHello)), &sent);

    char *buf = nullptr;
    int   recvLen = 0;
    EXPECT_FALSE(clientIO_->recv(buf, 10, &recvLen));
    EXPECT_EQ(recvLen, 0);

    // サーバループを終了させるため dummy 送信
    constexpr char kDummy[] = "dummy";
    clientIO_->send(kDummy, static_cast<int>(strlen(kDummy)), &sent);
}

// SPEC: docs/test/comm/io/test_comm_io_recv.md#TEST003
TEST_F(CommIOUdpRecvTest, NegativeDataLength)
{
    constexpr char kHello[] = "Ping";
    int sent = 0;
    clientIO_->send(kHello, static_cast<int>(strlen(kHello)), &sent);

    char buf[10];
    int  recvLen = 0;
    EXPECT_FALSE(clientIO_->recv(buf, -1, &recvLen));
    EXPECT_EQ(recvLen, 0);

    constexpr char kDummy[] = "dummy";
    clientIO_->send(kDummy, static_cast<int>(strlen(kDummy)), &sent);
}

// SPEC: docs/test/comm/io/test_comm_io_recv.md#TEST004
TEST_F(CommIOUdpRecvTest, NullRecvLenPointer)
{
    constexpr char kHello[] = "Hello Server";
    int sent = 0;
    clientIO_->send(kHello, static_cast<int>(strlen(kHello)), &sent);

    char buf[10];
    EXPECT_TRUE(clientIO_->recv(buf, 10, nullptr));

    constexpr char kDummy[] = "dummy";
    clientIO_->send(kDummy, static_cast<int>(strlen(kDummy)), &sent);
}

} // anonymous namespace
