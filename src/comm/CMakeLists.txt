cmake_minimum_required(VERSION 3.10...3.25)

# プロジェクトの定義
project(hakoniwa-drone-core-comm VERSION 1.0 LANGUAGES C CXX)

# OSの判定
if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    set(OS_TYPE "win")
else()
    set(OS_TYPE "posix")
endif()

# ソースファイルの定義
set(SOURCE_FILES
    impl/tcp_connector.cpp
    impl/udp_connector.cpp
    impl/comm_connector.cpp
)

# ライブラリの作成
add_library(hako_comm ${SOURCE_FILES})

if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    target_link_libraries(hako_comm ws2_32)
else()
    target_include_directories(hako_comm PRIVATE /usr/local/include)
endif()

target_include_directories(hako_comm 
    PRIVATE ${PROJECT_ROOT_DIR}/include/comm
    PRIVATE ${PROJECT_SOURCE_DIR}
)
target_compile_features(hako_comm PRIVATE cxx_std_17)

set(PUBLIC_HEADERS
    ${PROJECT_SOURCE_DIR}/icomm_connector.hpp
)

add_custom_target(
    comm_publish
    COMMAND ${CMAKE_COMMAND} -E make_directory "${HAKONIWA_PUBLIC_HEADER_DIR}/comm/"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${HAKONIWA_PUBLIC_LIB_DIR}/${CMAKE_SYSTEM_NAME}/${CMAKE_SYSTEM_PROCESSOR}/"
    COMMAND ${CMAKE_COMMAND} -E copy  $<TARGET_FILE:hako_comm> "${HAKONIWA_PUBLIC_LIB_DIR}/${CMAKE_SYSTEM_NAME}/${CMAKE_SYSTEM_PROCESSOR}/"
)
