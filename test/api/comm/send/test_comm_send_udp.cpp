// CommIO UDP Tests – Refactored and Minimal
// -----------------------------------------------------------------------------
// UDP 専用の送受信ユニットテスト。TCP 共通部分をすべて排除し、
// シンプルな RAII サーバで echo ライクな挙動を検証します。
//
// Build example:
//   add_executable(comm_io_udp_tests CommIOUdpTests.cpp)
//   target_link_libraries(comm_io_udp_tests PRIVATE gtest_main hako_comm)

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
// ヘルパ: UDP クライアント IO を生成
// -----------------------------------------------------------------------------
std::shared_ptr<ICommIO> createUdpClientIO(const char *srcIp,
                                           int         srcPort,
                                           const char *dstIp,
                                           int         dstPort)
{
    auto client = ICommClient::create(CommIoType::UDP);
    if (!client) throw std::runtime_error("UDP client create failed");

    ICommEndpointType src{srcIp, srcPort};
    ICommEndpointType dst{dstIp, dstPort};
    auto io = client->client_open(&src, &dst);
    if (!io) throw std::runtime_error("client_open failed");
    return io;
}

// -----------------------------------------------------------------------------
// UDP テストサーバ (1 datagram → 応答送信)
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
        ASSERT_TRUE(io_->recv(buf, sizeof(buf), &recvLen));
        constexpr char kResp[] = "Response from UDP Server";
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
// テストスイート
// -----------------------------------------------------------------------------
class CommIOUdpTest : public ::testing::Test {
protected:
    static void SetUpTestSuite()
    {
        ASSERT_EQ(hako::comm::comm_init(), 0);
    }

    static inline int nextPort_ = 55001;
    int                              port_{};
    std::unique_ptr<UdpTestServer>   server_;
    std::shared_ptr<ICommIO>         clientIO_;

    void SetUp() override
    {
        port_   = nextPort_++;
        server_ = std::make_unique<UdpTestServer>(port_);
        clientIO_ = createUdpClientIO("127.0.0.1", 0, "127.0.0.1", port_);
    }
    void TearDown() override
    {
        if (clientIO_) clientIO_->close();
        server_.reset();
    }
};

// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST001
TEST_F(CommIOUdpTest, ValidData)
{
    constexpr char kMsg[]  = "Hello UDP Server";
    constexpr char kResp[] = "Response from UDP Server";
    int sent = 0;
    ASSERT_TRUE(clientIO_->send(kMsg, static_cast<int>(strlen(kMsg)), &sent));
    EXPECT_EQ(sent, static_cast<int>(strlen(kMsg)));

    char buf[256]{};
    int  recvLen = 0;
    ASSERT_TRUE(clientIO_->recv(buf, sizeof(buf), &recvLen));
    buf[recvLen] = '\0';
    EXPECT_STREQ(buf, kResp);
}

// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST002
TEST_F(CommIOUdpTest, NullDataPointer)
{
    int sent = 0;
    EXPECT_FALSE(clientIO_->send(nullptr, 10, &sent));
    EXPECT_EQ(sent, 0);
}

// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST003
TEST_F(CommIOUdpTest, NegativeDataLength)
{
    const char *msg = "Invalid";
    int sent = 0;
    EXPECT_FALSE(clientIO_->send(msg, -1, &sent));
    EXPECT_EQ(sent, 0);
}

// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST004
TEST_F(CommIOUdpTest, SendLenNull)
{
    constexpr char kMsg[] = "Hello";
    EXPECT_TRUE(clientIO_->send(kMsg, static_cast<int>(strlen(kMsg)), nullptr));
}

} // anonymous namespace
