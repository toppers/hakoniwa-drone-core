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

# Pre-built libraries for hakoniwa-drone-core
include(FetchContent)

# 1. Determine the asset based on the OS
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    set(HAKO_DRONE_LIB_ASSET "lnx.zip")
elseif(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
    set(HAKO_DRONE_LIB_ASSET "mac.zip")
elseif(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    set(HAKO_DRONE_LIB_ASSET "win.zip")
else()
    message(FATAL_ERROR "Unsupported OS: ${CMAKE_SYSTEM_NAME}")
endif()

# 2. Get the latest release tag name from GitHub API
set(HAKO_DRONE_LIB_REPO "toppers/hakoniwa-drone-core")
set(LATEST_RELEASE_API_URL "https://api.github.com/repos/${HAKO_DRONE_LIB_REPO}/releases/latest")
set(JSON_FILE "${CMAKE_BINARY_DIR}/latest_release.json")

# Use curl to fetch the latest release info
execute_process(
    COMMAND curl -L -s -o ${JSON_FILE} ${LATEST_RELEASE_API_URL}
    RESULT_VARIABLE CURL_RESULT
)

if(NOT CURL_RESULT EQUAL 0)
    message(FATAL_ERROR "Failed to fetch latest release info from GitHub API.")
endif()

# Parse the JSON to get the tag_name
file(READ ${JSON_FILE} JSON_CONTENT)
string(JSON LATEST_TAG GET ${JSON_CONTENT} "tag_name")

if(NOT LATEST_TAG)
    message(FATAL_ERROR "Could not parse tag_name from GitHub API response.")
endif()

message(STATUS "Latest release tag: ${LATEST_TAG}")

# 3. Construct the final download URL and fetch the content
set(HAKO_DRONE_LIB_URL "https://github.com/${HAKO_DRONE_LIB_REPO}/releases/download/${LATEST_TAG}/${HAKO_DRONE_LIB_ASSET}")

FetchContent_Declare(
    prebuilt_libs
    URL ${HAKO_DRONE_LIB_URL}
)

FetchContent_MakeAvailable(prebuilt_libs)

# Add the downloaded library directory directly to the link and include paths
link_directories(${prebuilt_libs_SOURCE_DIR})
message(STATUS "Linking against pre-built libraries in ${prebuilt_libs_SOURCE_DIR}")

# OS とアーキテクチャを使ったディレクトリ設定
set(LIB_OUTPUT_DIR "${CMAKE_BINARY_DIR}/lib/${CMAKE_SYSTEM_NAME}/${CMAKE_SYSTEM_PROCESSOR}")
message(STATUS "CMAKE_BINARY_DIR: ${CMAKE_BINARY_DIR}")
message(STATUS "LIB_OUTPUT_DIR: ${LIB_OUTPUT_DIR}")


set(HAKO_CORE_DIR "${PROJECT_SOURCE_DIR}/../thirdparty/hakoniwa-core-cpp-client")

if (NOT ANDROID_BUILD)

add_subdirectory(main_for_sample)
endif()
