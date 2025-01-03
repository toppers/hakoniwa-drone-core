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
    drone/impl/drone_service_rc_api.cpp
)
# Static Library
add_library(hako_service STATIC ${SOURCE_FILES})

target_include_directories(hako_service
    PRIVATE ${PROJECT_ROOT_DIR}/include
    PRIVATE ${HAKO_SOURCE_DIR}/service
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

# Shared Library
add_library(hako_service_c SHARED ${SOURCE_FILES})

target_include_directories(hako_service_c 
    PRIVATE ${PROJECT_ROOT_DIR}/include
    PRIVATE ${HAKO_SOURCE_DIR}/service
    PRIVATE ${GLM_SOURCE_DIR}
    PRIVATE ${nlohmann_json_SOURCE_DIR}/single_include
    PRIVATE ${MAVLINK_SOURCE_DIR}/all
    PRIVATE ${ROS2PDU_SOURCE_DIR}/pdu/types
    )

target_compile_features(hako_service_c PRIVATE cxx_std_17)

target_link_libraries(hako_service_c PRIVATE 
    hako_controller
    hako_aircraft
    hako_mavlink
    )

# Add custom target for shared library publishing
add_custom_target(
    service_publish
    COMMAND ${CMAKE_COMMAND} -E make_directory "${HAKONIWA_PUBLIC_LIB_DIR}/${CMAKE_SYSTEM_NAME}/${CMAKE_SYSTEM_PROCESSOR}/"
    COMMAND ${CMAKE_COMMAND} -E copy  $<TARGET_FILE:hako_service> "${HAKONIWA_PUBLIC_LIB_DIR}/${CMAKE_SYSTEM_NAME}/${CMAKE_SYSTEM_PROCESSOR}/"
    COMMAND ${CMAKE_COMMAND} -E copy  $<TARGET_FILE:hako_service_c> "${HAKONIWA_PUBLIC_LIB_DIR}/${CMAKE_SYSTEM_NAME}/${CMAKE_SYSTEM_PROCESSOR}/"
)
