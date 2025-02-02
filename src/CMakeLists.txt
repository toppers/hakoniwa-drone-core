cmake_minimum_required(VERSION 3.10...3.25)

project(hakoniwa-px4sim-root
    VERSION 1.0.0
    DESCRIPTION "hakoniwa-drone-core project"
    LANGUAGES C CXX
)
if (DEFINED HAKO_DRONE_OPTION_FILEPATH)
    message(STATUS "HAKO_DRONE_OPTION_FILEPATH=${HAKO_DRONE_OPTION_FILEPATH}")
    include(${HAKO_DRONE_OPTION_FILEPATH})
else()
    message(STATUS "HAKO_DRONE_OPTION_FILEPATH is not defined. Use default options.")
    set(HAKO_DRONE_OPTION_FILEPATH "${PROJECT_SOURCE_DIR}/cmake-options/default-cmake-options.cmake")
    include(cmake-options/default-cmake-options.cmake)
endif()

set(PROJECT_ROOT_DIR "${PROJECT_SOURCE_DIR}/..")
set(HAKO_SOURCE_DIR "${PROJECT_SOURCE_DIR}")
#set(MAVLINK_SOURCE_DIR "${PROJECT_SOURCE_DIR}/../thirdparty/mavlink_c_library_v2")
set(ROS2PDU_SOURCE_DIR "${PROJECT_SOURCE_DIR}/../thirdparty/hakoniwa-ros2pdu")
set(GLM_SOURCE_DIR "${PROJECT_SOURCE_DIR}/../thirdparty/glm")
set(HAKO_CORE_SOURCE_DIR "${PROJECT_SOURCE_DIR}/../thirdparty/hakoniwa-core-cpp-client/src")

include(FetchContent)
if(CMAKE_SYSTEM_NAME STREQUAL "Linux" AND EXISTS "/etc/os-release")
    FetchContent_Declare(
        json
        URL https://github.com/nlohmann/json/releases/download/v3.11.3/json.tar.xz
    )
else()
    FetchContent_Declare(
        json
        URL https://github.com/nlohmann/json/releases/download/v3.11.3/json.tar.xz
        DOWNLOAD_EXTRACT_TIMESTAMP TRUE
    )
endif()
FetchContent_MakeAvailable(json)

# OS とアーキテクチャを使ったディレクトリ設定
set(LIB_OUTPUT_DIR "${CMAKE_BINARY_DIR}/lib/${CMAKE_SYSTEM_NAME}/${CMAKE_SYSTEM_PROCESSOR}")
message(STATUS "CMAKE_BINARY_DIR: ${CMAKE_BINARY_DIR}")
message(STATUS "LIB_OUTPUT_DIR: ${LIB_OUTPUT_DIR}")


set(HAKO_CORE_DIR "${PROJECT_SOURCE_DIR}/../thirdparty/hakoniwa-core-cpp-client")

if (NOT ANDROID_BUILD)
add_subdirectory(
    ${HAKO_CORE_DIR}
    ${CMAKE_BINARY_DIR}/thirdparty/hakoniwa-core-cpp-client
    )

add_subdirectory(main_for_sample)
endif()
