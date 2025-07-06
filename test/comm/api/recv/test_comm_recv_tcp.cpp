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

class TcpTestServer {
public:
    TcpTestServer(int port, int expectedLen) : port_{port}, expectedLen_{expectedLen}
    {
        server_ = ICommServer::create(CommIoType::TCP);
        if (!server_) throw std::runtime_error("TcpTestServer: create failed");
        thr_ = std::thread(&TcpTestServer::run, this);
        std::unique_lock lk(m_);
        cv_.wait(lk, [this] { return ready_.load(); });
    }
    ~TcpTestServer()
    {
        if (io_) io_->close();
        if (thr_.joinable()) thr_.join();
    }

    static constexpr const char* kResp = "Response from TCP Server";

private:
    void run()
    {
        ICommEndpointType ep{"127.0.0.1", port_};
        {
            std::lock_guard lg(m_);
            ready_ = true;
            cv_.notify_all();
        }
        io_ = server_->server_open(&ep);
        ASSERT_NE(io_, nullptr);
        char buf[256]{};
        int  recvLen = 0;
        if (!io_->recv(buf, expectedLen_, &recvLen)) return;
        int sent = 0;
        io_->send(kResp, static_cast<int>(strlen(kResp)), &sent);
    }

    int                          port_;
    int                          expectedLen_;
    std::unique_ptr<ICommServer> server_;
    std::shared_ptr<ICommIO>     io_;
    std::thread                  thr_;
    std::atomic<bool>            ready_{false};
    std::condition_variable      cv_;
    std::mutex                   m_;
};

class CommIOTcpRecvTest : public ::testing::Test {
protected:
    static void SetUpTestSuite() { ASSERT_EQ(hako::comm::comm_init(), 0); }

    static inline int nextPort_ = 57001;
    int                           port_{};
    std::unique_ptr<TcpTestServer> server_;
    std::shared_ptr<ICommIO>       clientIO_;

    void TearDown() override
    {
        if (clientIO_) clientIO_->close();
        server_.reset();
    }
};

// SPEC: docs/test/comm/io/test_comm_io_recv.md#TEST001
TEST_F(CommIOTcpRecvTest, ReceiveSuccess)
{
    constexpr char kHello[] = "Hello Server";
    port_   = nextPort_++;
    server_ = std::make_unique<TcpTestServer>(port_, static_cast<int>(strlen(kHello)));

    auto client = ICommClient::create(CommIoType::TCP);
    ASSERT_NE(client, nullptr);
    ICommEndpointType dst{"127.0.0.1", port_};
    clientIO_ = client->client_open(nullptr, &dst);
    ASSERT_NE(clientIO_, nullptr);

    int sent = 0;
    ASSERT_TRUE(clientIO_->send(kHello, static_cast<int>(strlen(kHello)), &sent));

    char buf[256]{};
    int  recvLen = 0;
    ASSERT_TRUE(clientIO_->recv(buf, static_cast<int>(strlen(TcpTestServer::kResp)), &recvLen));
    buf[recvLen] = '\0';
    EXPECT_STREQ(buf, TcpTestServer::kResp);
}

// SPEC: docs/test/comm/io/test_comm_io_recv.md#TEST002
TEST_F(CommIOTcpRecvTest, NullDataPointer)
{
    constexpr char kHello[] = "Ping";
    port_   = nextPort_++;
    server_ = std::make_unique<TcpTestServer>(port_, static_cast<int>(strlen(kHello)));

    auto client = ICommClient::create(CommIoType::TCP);
    ASSERT_NE(client, nullptr);
    ICommEndpointType dst{"127.0.0.1", port_};
    clientIO_ = client->client_open(nullptr, &dst);
    ASSERT_NE(clientIO_, nullptr);

    int sent = 0;
    clientIO_->send(kHello, static_cast<int>(strlen(kHello)), &sent);

    char* buf = nullptr;
    int   recvLen = 0;
    EXPECT_FALSE(clientIO_->recv(buf, 10, &recvLen));
    EXPECT_EQ(recvLen, 0);

    constexpr char kDummy[] = "dummy";
    clientIO_->send(kDummy, static_cast<int>(strlen(kDummy)), &sent);
}

// SPEC: docs/test/comm/io/test_comm_io_recv.md#TEST003
TEST_F(CommIOTcpRecvTest, NegativeDataLength)
{
    constexpr char kHello[] = "Ping";
    port_   = nextPort_++;
    server_ = std::make_unique<TcpTestServer>(port_, static_cast<int>(strlen(kHello)));

    auto client = ICommClient::create(CommIoType::TCP);
    ASSERT_NE(client, nullptr);
    ICommEndpointType dst{"127.0.0.1", port_};
    clientIO_ = client->client_open(nullptr, &dst);
    ASSERT_NE(clientIO_, nullptr);

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
TEST_F(CommIOTcpRecvTest, NullRecvLenPointer)
{
    constexpr char kHello[] = "Hello Server";
    port_   = nextPort_++;
    server_ = std::make_unique<TcpTestServer>(port_, static_cast<int>(strlen(kHello)));

    auto client = ICommClient::create(CommIoType::TCP);
    ASSERT_NE(client, nullptr);
    ICommEndpointType dst{"127.0.0.1", port_};
    clientIO_ = client->client_open(nullptr, &dst);
    ASSERT_NE(clientIO_, nullptr);

    int sent = 0;
    clientIO_->send(kHello, static_cast<int>(strlen(kHello)), &sent);

    char buf[10];
    ASSERT_TRUE(clientIO_->recv(buf, sizeof(buf), nullptr));
}

} // anonymous namespace
