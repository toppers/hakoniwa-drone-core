cmake_minimum_required(VERSION 3.10...3.25)

include(FetchContent)
FetchContent_Declare(
    googletest
    URL https://github.com/google/googletest/archive/refs/tags/v1.14.0.zip
)
FetchContent_MakeAvailable(googletest)

add_executable(test_comm_recv_udp test_comm_recv_udp.cpp)

# use headers from project
target_include_directories(test_comm_recv_udp PRIVATE ${PROJECT_ROOT_DIR}/include)

# compile options
target_compile_features(test_comm_recv_udp PRIVATE cxx_std_17)

# link libs
set(LIBS
    hako_aircraft
    hako_controller
    hako_logger
    hako_service
    hako_comm
    drone_physics
    pthread
)

target_link_libraries(test_comm_recv_udp PRIVATE gtest_main ${LIBS})

target_link_directories(test_comm_recv_udp PRIVATE ${PROJECT_ROOT_DIR}/lib)

add_test(NAME comm_recv_udp COMMAND test_comm_recv_udp)
