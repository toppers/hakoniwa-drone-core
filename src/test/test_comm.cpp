#include <gtest/gtest.h>
#include <thread>
#include "comm/impl/udp_connector.hpp"
#include "comm/impl/tcp_connector.hpp"

namespace hako::comm {

TEST(UdpCommTest, SendReceiveData) {
    const char* server_ip = "127.0.0.1";
    const int server_port = 12345;
    const int client_port = 54321;
    const char* test_message = "Hello, UDP!";
    char buffer[1024] = {0};

    IcommEndpointType server_endpoint = {server_ip, server_port};
    impl::UdpServer server;
    ICommIO* server_io = nullptr;

    IcommEndpointType client_src = {server_ip, client_port};
    IcommEndpointType client_dst = {server_ip, server_port};
    impl::UdpClient client;

    std::thread server_thread([&]() {
        server_io = server.server_open(&server_endpoint);
        ASSERT_NE(server_io, nullptr) << "Failed to open server";

        int recv_len = 0;
        ASSERT_TRUE(server_io->recv(buffer, sizeof(buffer), &recv_len));
        ASSERT_EQ(recv_len, strlen(test_message));
        ASSERT_STREQ(buffer, test_message);

        const char* reply_message = "Hello, Client!";
        int sent_len = 0;
        ASSERT_TRUE(server_io->send(reply_message, static_cast<int>(strlen(reply_message)), &sent_len));
        ASSERT_EQ(sent_len, strlen(reply_message));

        server_io->close();
    });

    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    ICommIO* client_io = client.client_open(&client_src, &client_dst);
    ASSERT_NE(client_io, nullptr) << "Failed to open client";

    int sent_len = 0;
    ASSERT_TRUE(client_io->send(test_message, static_cast<int>(strlen(test_message)), &sent_len));
    ASSERT_EQ(sent_len, strlen(test_message));

    int recv_len = 0;
    char reply_buffer[1024] = {0};
    ASSERT_TRUE(client_io->recv(reply_buffer, sizeof(reply_buffer), &recv_len));
    ASSERT_STREQ(reply_buffer, "Hello, Client!");

    client_io->close();
    server_thread.join();
}


TEST(TcpCommTest, SendReceiveData) {
    const char* server_ip = "127.0.0.1";
    const int server_port = 12345;
    const char* test_message = "Hello, TCP!";
    hako::comm::comm_init();
    
    IcommEndpointType server_endpoint = {server_ip, server_port};
    impl::TcpServer server;
    ICommIO* server_io = nullptr;

    IcommEndpointType client_src = {nullptr, 0}; 
    IcommEndpointType client_dst = {server_ip, server_port};
    impl::TcpClient client;

    std::thread server_thread([&]() {
        server_io = server.server_open(&server_endpoint);
        ASSERT_NE(server_io, nullptr) << "Failed to open server";

        char buffer[1024] = {0};
        int recv_len = 0;
        ASSERT_TRUE(server_io->recv(buffer, static_cast<int>(strlen(test_message)), &recv_len));
        ASSERT_EQ(recv_len, strlen(test_message));
        ASSERT_STREQ(buffer, test_message);
        
        const char* reply_message = "Hello, Client!";
        int sent_len = 0;
        ASSERT_TRUE(server_io->send(reply_message, static_cast<int>(strlen(reply_message)), &sent_len));
        ASSERT_EQ(sent_len, strlen(reply_message));

        server_io->close();
    });

    ICommIO* client_io = client.client_open(&client_src, &client_dst);
    ASSERT_NE(client_io, nullptr) << "Failed to open client";

    int sent_len = 0;
    ASSERT_TRUE(client_io->send(test_message, static_cast<int>(strlen(test_message)), &sent_len));
    ASSERT_EQ(sent_len, strlen(test_message));

    char reply_buffer[1024] = {0};
    int recv_len = 0;
    ASSERT_TRUE(client_io->recv(reply_buffer, static_cast<int>(strlen("Hello, Client!")), &recv_len));
    ASSERT_EQ(recv_len, strlen("Hello, Client!"));
    ASSERT_STREQ(reply_buffer, "Hello, Client!");
    
    client_io->close();
    server_thread.join();
}

} // namespace hako::comm
