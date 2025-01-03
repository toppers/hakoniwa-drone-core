cmake_minimum_required(VERSION 3.10...3.25)

# プロジェクトの定義
project(hakoniwa-drone-core-logger VERSION 1.0 LANGUAGES C CXX)

# OSの判定
if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    set(OS_TYPE "win")
else()
    set(OS_TYPE "posix")
endif()

# ソースファイルの定義
set(SOURCE_FILES
    impl/hako_logger.cpp
)
add_library(hako_logger ${SOURCE_FILES})

target_include_directories(hako_logger 
    PRIVATE ${PROJECT_ROOT_DIR}/include
    PRIVATE ${HAKO_SOURCE_DIR}/logger
    )
target_compile_features(hako_logger PRIVATE cxx_std_17)

target_link_libraries(hako_logger PRIVATE hako_comm)

add_custom_target(
    logger_publish
    COMMAND ${CMAKE_COMMAND} -E make_directory "${HAKONIWA_PUBLIC_LIB_DIR}/${CMAKE_SYSTEM_NAME}/${CMAKE_SYSTEM_PROCESSOR}/"
    COMMAND ${CMAKE_COMMAND} -E copy  $<TARGET_FILE:hako_logger> "${HAKONIWA_PUBLIC_LIB_DIR}/${CMAKE_SYSTEM_NAME}/${CMAKE_SYSTEM_PROCESSOR}/"
)    