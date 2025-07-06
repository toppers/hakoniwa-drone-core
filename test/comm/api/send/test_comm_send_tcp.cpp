// CommIOTcpTest_refactored.cpp
// Refactored version of the original CommIOTcp test
// Focus: eliminate globals, RAII for cleanup, clearer intent, less duplication

#include <gtest/gtest.h>
#include <thread>
#include <memory>
#include <atomic>
#include <condition_variable>
#include "comm.hpp"

namespace {

/**
 * @brief Minimal RAII wrapper that runs a TCP echo‑like server in a background thread for each test.
 *        ‑ Listens on 127.0.0.1:port, waits for exactly @p expectedDataLength bytes, then replies
 *        with the hard‑coded string "Response from TCP Server".
 */
class TcpTestServer {
public:
    TcpTestServer(int port, int expectedDataLength)
        : port_{port}, expectedDataLength_{expectedDataLength}
    {
        server_ = hako::comm::ICommServer::create(hako::comm::CommIoType::TCP);
        if (!server_) {
            throw std::runtime_error("Failed to create server");
        }
        // Launch server loop
        thread_ = std::thread(&TcpTestServer::run, this);

        // Wait until the listening socket is up
        std::unique_lock<std::mutex> lk(m_);
        cv_.wait(lk, [this] { return ready_.load(); });
    }

    // Non‑copyable / non‑movable (keeps life‑time simple)
    TcpTestServer(const TcpTestServer&)            = delete;
    TcpTestServer& operator=(const TcpTestServer&) = delete;

    ~TcpTestServer()
    {
        if (serverCommIO_) {
            serverCommIO_->close();
        }
        if (thread_.joinable()) {
            thread_.join();
        }
    }

private:
    void run()
    {
        hako::comm::ICommEndpointType ep{"127.0.0.1", port_};

        {
            std::lock_guard<std::mutex> lk(m_);
            ready_ = true;
            cv_.notify_all();
        }

        serverCommIO_ = server_->server_open(&ep);
        ASSERT_NE(serverCommIO_, nullptr) << "Server failed to open.";

        if (expectedDataLength_ <= 0) {
            return; // nothing more to do for tests that don't send payload
        }

        char buffer[256]{};
        int recvLen = 0;
        ASSERT_TRUE(serverCommIO_->recv(buffer, expectedDataLength_, &recvLen));

        constexpr char kResponse[] = "Response from TCP Server";
        int sentLen = 0;
        serverCommIO_->send(kResponse, static_cast<int>(strlen(kResponse)), &sentLen);
    }

    const int port_;
    const int expectedDataLength_;

    std::unique_ptr<hako::comm::ICommServer> server_;
    std::shared_ptr<hako::comm::ICommIO>     serverCommIO_;

    std::thread          thread_;
    std::atomic<bool>    ready_{false};
    std::condition_variable cv_;
    std::mutex           m_;
};

/**
 * @brief Helper that opens a TCP client connection to the given IP & port.
 */
std::shared_ptr<hako::comm::ICommIO> createClientIO(const char* ip, int port)
{
    auto client = hako::comm::ICommClient::create(hako::comm::CommIoType::TCP);
    if (!client) {
        throw std::runtime_error("Failed to create client");
    }
    hako::comm::ICommEndpointType serverEp{ip, port};
    auto io = client->client_open(nullptr, &serverEp);
    if (!io) {
        throw std::runtime_error("Failed to open client IO");
    }
    return io;
}

class CommIOTcpTest : public ::testing::Test {
protected:
    static inline int nextPort_ = 54001; // simple port pool per process run

    int                                 port_      = 0;
    std::unique_ptr<TcpTestServer>      server_;
    std::shared_ptr<hako::comm::ICommIO> clientIO_;

    static void SetUpTestSuite()
    {
        ASSERT_EQ(hako::comm::comm_init(), 0) << "Failed to init comm library";
    }

    void TearDown() override
    {
        if (clientIO_) {
            clientIO_->close();
            clientIO_.reset();
        }
        server_.reset(); // joins underlying thread & closes server IO
    }
};

// ────────────────────────────────────────────────────────────────────────────────
// TEST001: 正常なデータ送受信
// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST001
TEST_F(CommIOTcpTest, ValidData)
{
    constexpr char kPayload[]   = "Hello TCP Server";
    constexpr char kResponse[]  = "Response from TCP Server";
    const int datalen           = static_cast<int>(strlen(kPayload));

    port_   = nextPort_++;
    server_ = std::make_unique<TcpTestServer>(port_, datalen);
    clientIO_ = createClientIO("127.0.0.1", port_);

    int sentLen = 0;
    ASSERT_TRUE(clientIO_->send(kPayload, datalen, &sentLen));
    EXPECT_EQ(sentLen, datalen);

    char response[256]{};
    int  recvLen = 0;
    ASSERT_TRUE(clientIO_->recv(response, static_cast<int>(strlen(kResponse)), &recvLen));
    response[recvLen] = '\0';

    EXPECT_STREQ(response, kResponse);
}

// TEST002: data == nullptr
// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST002
TEST_F(CommIOTcpTest, NullDataPointer)
{
    port_   = nextPort_++;
    server_ = std::make_unique<TcpTestServer>(port_, 0);
    clientIO_ = createClientIO("127.0.0.1", port_);

    const char* data    = nullptr;
    int         datalen = 10;
    int         sentLen = 0;

    EXPECT_FALSE(clientIO_->send(data, datalen, &sentLen));
    EXPECT_EQ(sentLen, 0);
}

// TEST003: 負の長さ
// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST003
TEST_F(CommIOTcpTest, NegativeDataLength)
{
    port_   = nextPort_++;
    server_ = std::make_unique<TcpTestServer>(port_, 0);
    clientIO_ = createClientIO("127.0.0.1", port_);

    const char* data    = "Invalid";
    int         datalen = -1;
    int         sentLen = 0;

    EXPECT_FALSE(clientIO_->send(data, datalen, &sentLen));
    EXPECT_EQ(sentLen, 0);
}

// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST004
TEST_F(CommIOTcpTest, TEST004_NullSendDataLenPointer)
{
    constexpr char kPayload[]   = "Hello TCP Server";
    constexpr char kResponse[]  = "Response from TCP Server";
    const int datalen = static_cast<int>(strlen(kPayload));

    port_   = nextPort_++;
    server_ = std::make_unique<TcpTestServer>(port_, datalen);
    clientIO_ = createClientIO("127.0.0.1", port_);

    ASSERT_TRUE(clientIO_->send(kPayload, datalen, nullptr));

    char response[256]{};
    int  recvLen = 0;
    ASSERT_TRUE(clientIO_->recv(response, static_cast<int>(strlen(kResponse)), &recvLen));
    response[recvLen] = '\0';

    EXPECT_STREQ(response, kResponse);
}

} // namespace
