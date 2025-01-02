cmake_minimum_required(VERSION 3.10...3.25)

# プロジェクトの定義
project(hakoniwa-drone-core-sample VERSION 1.0 LANGUAGES C CXX)

# OSの判定
if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    set(OS_TYPE "win")
else()
    set(OS_TYPE "posix")
endif()

set(TARGETS
    hako_aircraft_service
    hako_drone_service
)

add_executable(hako_aircraft_service main_hako_aircraft_service.cpp)
add_executable(hako_drone_service main_hako_drone_service.cpp)

foreach(TARGET ${TARGETS})
    MESSAGE(STATUS "HAKO_SOURCE_DIR: ${HAKO_SOURCE_DIR}")
    MESSAGE(STATUS "nlohmann_json_SOURCE_DIR: ${nlohmann_json_SOURCE_DIR}")
    target_include_directories(${TARGET} 
        PRIVATE ${PROJECT_ROOT_DIR}/include
        PRIVATE ${HAKO_SOURCE_DIR}
        PRIVATE ${GLM_SOURCE_DIR}
        PRIVATE ${nlohmann_json_SOURCE_DIR}/single_include
        PRIVATE ${ROS2PDU_SOURCE_DIR}/pdu/types
        PRIVATE ${HAKO_CORE_SOURCE_DIR}
    )
    target_compile_features(${TARGET} PRIVATE cxx_std_17)
    target_link_libraries(${TARGET} 
        PRIVATE hako_drone_core
        PRIVATE assets
        PRIVATE conductor
        )
endforeach()

