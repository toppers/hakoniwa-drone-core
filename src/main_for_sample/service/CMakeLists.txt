cmake_minimum_required(VERSION 3.10...3.25)

# プロジェクトの定義
project(hakoniwa-drone-core-service-sample VERSION 1.0 LANGUAGES C CXX)

# OSの判定
if(CMAKE_SYSTEM_NAME STREQUAL "Windows")
    set(OS_TYPE "win")
else()
    set(OS_TYPE "posix")
endif()

set(TARGETS 
    drone_service_rc
)

add_executable(drone_service_rc main_drone_service_rc.cpp)

foreach(TARGET ${TARGETS})
    MESSAGE(STATUS "TARGET: ${TARGET}")
    if(OS_TYPE STREQUAL "posix")
        target_compile_options(${TARGET} PRIVATE
            -Wno-pedantic
            -Wno-address-of-packed-member
            -Wno-unused-function
            -Wno-missing-field-initializers
        )
    else()
        target_compile_options(${TARGET} PRIVATE
            /wd4200  # Zero-sized array
            /wd4706  # Assignment within conditional expression
            /wd4996  # Deprecated API
            /wd4244  # 'double'から'float'への変換の警告を抑制
            /wd4309  # 定数値の切り捨ての警告を抑制
            /wd4267  # Suppress warning C4267: size_t to int conversion
        )
    endif()


    target_include_directories(${TARGET} 
        PRIVATE ${PROJECT_ROOT_DIR}/include
        PRIVATE ${HAKO_SOURCE_DIR}
        PRIVATE ${GLM_SOURCE_DIR}
        PRIVATE ${nlohmann_json_SOURCE_DIR}/single_include
        PRIVATE ${ROS2PDU_SOURCE_DIR}/pdu/types
    )
    target_compile_features(${TARGET} PRIVATE cxx_std_17)
    target_link_libraries(${TARGET} PRIVATE drone_physics  hako_aircraft hako_controller hako_logger hako_service  )
    target_link_directories(${TARGET} PRIVATE ${PROJECT_ROOT_DIR}/lib)
endforeach()

