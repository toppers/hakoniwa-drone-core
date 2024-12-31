#include <gtest/gtest.h>
#include <thread>
#include "mavlink/impl/mavlink_comm_tcp.hpp"
#include "mavlink/impl/mavlink_comm_udp.hpp"
#include "comm/impl/udp_connector.hpp"
#include "comm/impl/tcp_connector.hpp"

using namespace hako::mavlink;
using namespace hako::comm;

#include <cstring>
#include <iostream>
#include <vector>


std::vector<char> createMavlinkMessage(const char* payload, int payload_len) {
    std::vector<char> message(MAVLINK_TOTAL_HEADER_LEN + payload_len);

    message[0] = static_cast<char>(0xFE); 
    message[1] = static_cast<char>(payload_len);
    message[2] = 0x01;
    message[3] = 0x01;
    message[4] = 0x01;
    message[5] = 0x01;

    message[MAVLINK_TOTAL_HEADER_LEN - 2] = 0x00;
    message[MAVLINK_TOTAL_HEADER_LEN - 1] = 0x00;

    memcpy(message.data() + MAVLINK_HEADER_LEN, payload, payload_len);

    return message;
}

TEST(MavLinkCommUdpTest, SendReceiveDataWithMavlinkHeader) {
    const char* server_ip = "127.0.0.1";
    const int server_port = 12346;
    const char* payload = "Hello, MAVLink!";
    const int payload_len = static_cast<int>(strlen(payload));

    IcommEndpointType server_endpoint = {server_ip, server_port};
    impl::UdpServer udp_server;
    ICommIO* server_io = nullptr;

    impl::UdpClient udp_client;
    IcommEndpointType client_endpoint = {server_ip, server_port};
    MavLinkCommUdp mavlink_comm_udp;

    std::thread server_thread([&]() {
        server_io = udp_server.server_open(&server_endpoint);
        ASSERT_NE(server_io, nullptr) << "Failed to open UDP server";
        char recv_buffer[1024] = {0};
        int recv_len = 0;
        ASSERT_TRUE(mavlink_comm_udp.receiveMessage(server_io, recv_buffer, sizeof(recv_buffer), &recv_len));
        ASSERT_GE(recv_len, MAVLINK_HEADER_LEN);

        ASSERT_EQ(recv_buffer[1], payload_len);
        ASSERT_STREQ(recv_buffer + MAVLINK_HEADER_LEN, payload);

        const char* reply_payload = "Reply from Server";
        auto reply_message = createMavlinkMessage(reply_payload, static_cast<int>(strlen(reply_payload)));
        ASSERT_TRUE(mavlink_comm_udp.sendMessage(server_io, reply_message.data(), static_cast<int>(reply_message.size())));
        server_io->close();
    });

    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    ICommIO* client_io = udp_client.client_open(nullptr, &client_endpoint);
    ASSERT_NE(client_io, nullptr) << "Failed to open UDP client";

    auto message = createMavlinkMessage(payload, payload_len);
    ASSERT_TRUE(mavlink_comm_udp.sendMessage(client_io, message.data(), static_cast<int>(message.size())));
    char reply_buffer[1024] = {0};
    int recv_len = 0;
    ASSERT_TRUE(mavlink_comm_udp.receiveMessage(client_io, reply_buffer, sizeof(reply_buffer), &recv_len));
    ASSERT_GE(recv_len, MAVLINK_HEADER_LEN);
    ASSERT_STREQ(reply_buffer + MAVLINK_HEADER_LEN, "Reply from Server");
    client_io->close();
    server_thread.join();
}


TEST(MavLinkCommTcpTest, SendReceiveDataWithMavlinkHeader) {
    const char* server_ip = "127.0.0.1";
    const int server_port = 12346;
    const char* payload = "Hello, MAVLink!";
    const int payload_len = static_cast<int>(strlen(payload));

    IcommEndpointType server_endpoint = {server_ip, server_port};
    impl::TcpServer tcp_server;
    ICommIO* server_io = nullptr;

    impl::TcpClient tcp_client;
    IcommEndpointType client_endpoint = {server_ip, server_port};
    MavLinkCommTcp mavlink_comm_tcp;

    std::thread server_thread([&]() {
        server_io = tcp_server.server_open(&server_endpoint);
        ASSERT_NE(server_io, nullptr) << "Failed to open TCP server";

        char recv_buffer[1024] = {0};
        int recv_len = 0;
        ASSERT_TRUE(mavlink_comm_tcp.receiveMessage(server_io, recv_buffer, sizeof(recv_buffer), &recv_len));
        ASSERT_GE(recv_len, MAVLINK_HEADER_LEN);

        ASSERT_EQ(recv_buffer[1], payload_len);
        ASSERT_STREQ(recv_buffer + MAVLINK_HEADER_LEN, payload);

        const char* reply_payload = "Reply from Server";
        auto reply_message = createMavlinkMessage(reply_payload, static_cast<int>(strlen(reply_payload)));
        ASSERT_TRUE(mavlink_comm_tcp.sendMessage(server_io, reply_message.data(), static_cast<int>(reply_message.size())));
        server_io->close();
    });

    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    ICommIO* client_io = tcp_client.client_open(nullptr, &client_endpoint);
    ASSERT_NE(client_io, nullptr) << "Failed to open TCP client";

    auto message = createMavlinkMessage(payload, payload_len);
    ASSERT_TRUE(mavlink_comm_tcp.sendMessage(client_io, message.data(), static_cast<int>(message.size())));

    char reply_buffer[1024] = {0};
    int recv_len = 0;
    ASSERT_TRUE(mavlink_comm_tcp.receiveMessage(client_io, reply_buffer, sizeof(reply_buffer), &recv_len));
    ASSERT_GE(recv_len, MAVLINK_HEADER_LEN);
    ASSERT_STREQ(reply_buffer + MAVLINK_HEADER_LEN, "Reply from Server");

    client_io->close();
    server_thread.join();
}
