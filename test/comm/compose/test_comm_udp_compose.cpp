#include <gtest/gtest.h>
#include "comm.hpp"
#include <cstring>
#include <memory>
#include <cstdlib>

using hako::comm::CommIoType;
using hako::comm::ICommClient;
using hako::comm::ICommEndpointType;
using hako::comm::ICommIO;

namespace {

const char* server_host()
{
    const char* h = std::getenv("SERVER_HOST");
    return h ? h : "server";
}

int server_port()
{
    const char* p = std::getenv("PORT");
    return p ? std::atoi(p) : 60000;
}

class CommComposeIOUdpTest : public ::testing::Test {
protected:
    static void SetUpTestSuite() { ASSERT_EQ(hako::comm::comm_init(), 0); }

    void SetUp() override
    {
        auto client = ICommClient::create(CommIoType::UDP);
        ASSERT_NE(client, nullptr);
        ICommEndpointType src{"0.0.0.0", 0};
        ICommEndpointType dst{server_host(), server_port()};
        io_ = client->client_open(&src, &dst);
        ASSERT_NE(io_, nullptr);
    }

    void TearDown() override
    {
        if (io_) io_->close();
    }

    std::shared_ptr<ICommIO> io_;
};

// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST001
TEST_F(CommComposeIOUdpTest, SendValidData)
{
    const char* msg = "Hello TCP Server";
    const int   datalen = static_cast<int>(strlen(msg));
    int         sent = 0;
    ASSERT_TRUE(io_->send(msg, datalen, &sent));
    EXPECT_EQ(sent, datalen);

    char buf[64]{};
    int  recvLen = 0;
    ASSERT_TRUE(io_->recv(buf, sizeof(buf), &recvLen));
    buf[recvLen] = '\0';
    EXPECT_STREQ(buf, "ACK");
}

// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST002
TEST_F(CommComposeIOUdpTest, SendNullDataPointer)
{
    const char* data = nullptr;
    int         datalen = 10;
    int         sent = 0;
    EXPECT_FALSE(io_->send(data, datalen, &sent));
    EXPECT_EQ(sent, 0);
}

// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST003
TEST_F(CommComposeIOUdpTest, SendNegativeLength)
{
    const char* data = "Invalid";
    int         datalen = -1;
    int         sent = 0;
    EXPECT_FALSE(io_->send(data, datalen, &sent));
    EXPECT_EQ(sent, 0);
}

// SPEC: docs/test/comm/io/test_comm_io_send.md#TEST004
TEST_F(CommComposeIOUdpTest, SendNullSendLenPointer)
{
    const char* msg = "Hello TCP Server";
    const int   datalen = static_cast<int>(strlen(msg));
    ASSERT_TRUE(io_->send(msg, datalen, nullptr));
}

// SPEC: docs/test/comm/io/test_comm_io_recv.md#TEST001
TEST_F(CommComposeIOUdpTest, RecvSuccess)
{
    const char* msg = "Hello Server";
    int         sent = 0;
    ASSERT_TRUE(io_->send(msg, static_cast<int>(strlen(msg)), &sent));

    char buf[64]{};
    int  recvLen = 0;
    ASSERT_TRUE(io_->recv(buf, sizeof(buf), &recvLen));
    buf[recvLen] = '\0';
    EXPECT_STREQ(buf, "ACK");
}

// SPEC: docs/test/comm/io/test_comm_io_recv.md#TEST002
TEST_F(CommComposeIOUdpTest, RecvNullDataPointer)
{
    const char* msg = "Ping";
    int         sent = 0;
    io_->send(msg, static_cast<int>(strlen(msg)), &sent);

    char* buf = nullptr;
    int   recvLen = 0;
    EXPECT_FALSE(io_->recv(buf, 10, &recvLen));
    EXPECT_EQ(recvLen, 0);
}

// SPEC: docs/test/comm/io/test_comm_io_recv.md#TEST003
TEST_F(CommComposeIOUdpTest, RecvNegativeLength)
{
    const char* msg = "Ping";
    int         sent = 0;
    io_->send(msg, static_cast<int>(strlen(msg)), &sent);

    char buf[10];
    int  recvLen = 0;
    EXPECT_FALSE(io_->recv(buf, -1, &recvLen));
    EXPECT_EQ(recvLen, 0);
}

// SPEC: docs/test/comm/io/test_comm_io_recv.md#TEST004
TEST_F(CommComposeIOUdpTest, RecvNullRecvLenPointer)
{
    const char* msg = "Hello Server";
    int         sent = 0;
    io_->send(msg, static_cast<int>(strlen(msg)), &sent);

    char buf[10];
    ASSERT_TRUE(io_->recv(buf, sizeof(buf), nullptr));
}

} // namespace

int main(int argc, char** argv)
{
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
