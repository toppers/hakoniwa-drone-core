cmake_minimum_required(VERSION 3.10...3.25)

include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
)
FetchContent_MakeAvailable(googletest)

set(PROJECT_ROOT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../../..")
include(${PROJECT_ROOT_DIR}/src/cmake-options/linux-cmake-options.cmake)

add_executable(test_comm_tcp_compose test_comm_tcp_compose.cpp)
add_executable(test_comm_udp_compose test_comm_udp_compose.cpp)
target_include_directories(test_comm_tcp_compose PRIVATE ${PROJECT_ROOT_DIR}/include)
target_include_directories(test_comm_udp_compose PRIVATE ${PROJECT_ROOT_DIR}/include)
target_compile_features(test_comm_tcp_compose PRIVATE cxx_std_17)
target_compile_features(test_comm_udp_compose PRIVATE cxx_std_17)

add_executable(comm_server_tcp server_tcp.cpp)
add_executable(comm_server_udp server_udp.cpp)
target_include_directories(comm_server_tcp PRIVATE ${PROJECT_ROOT_DIR}/include)
target_include_directories(comm_server_udp PRIVATE ${PROJECT_ROOT_DIR}/include)
target_compile_features(comm_server_tcp PRIVATE cxx_std_17)
target_compile_features(comm_server_udp PRIVATE cxx_std_17)

set(LIBS hako_comm)
if (NOT ${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
    list(APPEND LIBS pthread)
endif()

target_link_libraries(test_comm_tcp_compose PRIVATE gtest_main ${LIBS})
target_link_libraries(test_comm_udp_compose PRIVATE gtest_main ${LIBS})
target_link_libraries(comm_server_tcp PRIVATE ${LIBS})
target_link_libraries(comm_server_udp PRIVATE ${LIBS})
target_link_directories(test_comm_tcp_compose PRIVATE ${PROJECT_ROOT_DIR}/lib)
target_link_directories(test_comm_udp_compose PRIVATE ${PROJECT_ROOT_DIR}/lib)
target_link_directories(comm_server_tcp PRIVATE ${PROJECT_ROOT_DIR}/lib)
target_link_directories(comm_server_udp PRIVATE ${PROJECT_ROOT_DIR}/lib)

add_test(
    NAME comm_compose_tcp
    COMMAND bash ${CMAKE_CURRENT_SOURCE_DIR}/test_comm_compose.sh tcp
)
add_test(
    NAME comm_compose_udp
    COMMAND bash ${CMAKE_CURRENT_SOURCE_DIR}/test_comm_compose.sh udp
)

