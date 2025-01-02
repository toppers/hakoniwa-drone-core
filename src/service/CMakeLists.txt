cmake_minimum_required(VERSION 3.10...3.25)

# プロジェクトの定義
project(hakoniwa-drone-core-service VERSION 1.0 LANGUAGES C CXX)

# OSの判定
if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    set(OS_TYPE "win")
else()
    set(OS_TYPE "posix")
endif()

# ソースファイルの定義
set(SOURCE_FILES
    aircraft/impl/aircraft_service_container.cpp
    drone/impl/drone_service.cpp
)
add_library(hako_service ${SOURCE_FILES})


target_include_directories(hako_service 
    PRIVATE ${PROJECT_ROOT_DIR}/include/comm
    PRIVATE ${PROJECT_ROOT_DIR}/include/mavlink
    PRIVATE ${PROJECT_ROOT_DIR}/include/controller
    PRIVATE ${PROJECT_ROOT_DIR}/include/config
    PRIVATE ${PROJECT_ROOT_DIR}/include/logger
    PRIVATE ${HAKO_SOURCE_DIR}
    PRIVATE ${GLM_SOURCE_DIR}
    PRIVATE ${nlohmann_json_SOURCE_DIR}/single_include
    PRIVATE ${MAVLINK_SOURCE_DIR}/all
    PRIVATE ${ROS2PDU_SOURCE_DIR}/pdu/types
    )

target_compile_features(hako_service PRIVATE cxx_std_17)

target_link_libraries(hako_service PRIVATE 
    hako_controller
    hako_aircraft
    hako_mavlink
    )
