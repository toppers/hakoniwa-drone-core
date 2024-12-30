cmake_minimum_required(VERSION 3.10...3.25)

project(drone_physics
    VERSION 1.0.0
    DESCRIPTION "drone_physics project"
    LANGUAGES C CXX
)

if (NOT DEFINED HAKO_DRONE_OPTION_FILEPATH)
    MESSAGE(STATUS "HAKO_DRONE_OPTION_FILEPATH is not defined. Use default options.")
    include(default-cmake-options.cmake)
endif()

add_library(
    drone_physics
    drone_frames.cpp
    rotor_physics.cpp
    body_physics.cpp
)

add_library(
    drone_physics_c
    drone_physics_c.cpp
    drone_frames.cpp
    body_physics.cpp
    rotor_physics.cpp
)

add_executable(utest utest.cpp)
target_link_libraries(utest drone_physics)

#if (NOT CMAKE_SYSTEM_NAME MATCHES "Linux")
add_executable(ctest ctest.c)
target_link_libraries(ctest drone_physics_c)
#endif()

add_executable(examples examples.cpp)
target_link_libraries(examples drone_physics)

add_executable(cexamples cexamples.c)
target_link_libraries(cexamples drone_physics_c)


enable_testing()
add_test(NAME utest COMMAND ./utest)
add_test(NAME ctest COMMAND ./ctest)

#add_executable(glmtest glmtest.cpp)
#target_include_directories(glmtest PRIVATE ../hakoniwa/third-party/glm)
#add_test(NAME glmtest COMMAND ./glmtest)

add_custom_target(vtest COMMAND ${CMAKE_CTEST_COMMAND} --verbose)

set(PUBLIC_HEADERS
    ${PROJECT_SOURCE_DIR}/drone_frames.hpp
    ${PROJECT_SOURCE_DIR}/drone_physics.hpp
    ${PROJECT_SOURCE_DIR}/rotor_physics.hpp
    ${PROJECT_SOURCE_DIR}/body_physics.hpp
    ${PROJECT_SOURCE_DIR}/drone_physics_c.h
)


add_custom_target(
    physics_publish
    COMMAND ${CMAKE_COMMAND} -E make_directory "${HAKONIWA_PUBLIC_HEADER_DIR}/physics/"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${HAKONIWA_PUBLIC_LIB_DIR}/${CMAKE_SYSTEM_NAME}/${CMAKE_SYSTEM_PROCESSOR}/"
    COMMAND ${CMAKE_COMMAND} -E copy ${PUBLIC_HEADERS} "${HAKONIWA_PUBLIC_HEADER_DIR}/physics/"
    COMMAND ${CMAKE_COMMAND} -E copy  $<TARGET_FILE:drone_physics> "${HAKONIWA_PUBLIC_LIB_DIR}/${CMAKE_SYSTEM_NAME}/${CMAKE_SYSTEM_PROCESSOR}/"
    COMMAND ${CMAKE_COMMAND} -E copy  $<TARGET_FILE:drone_physics_c> "${HAKONIWA_PUBLIC_LIB_DIR}/${CMAKE_SYSTEM_NAME}/${CMAKE_SYSTEM_PROCESSOR}/"
)
