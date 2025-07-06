cmake_minimum_required(VERSION 3.10...3.25)
project(hakoniwa_drone_tests LANGUAGES C CXX)

set(PROJECT_ROOT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/..")
include(${PROJECT_ROOT_DIR}/src/cmake-options/linux-cmake-options.cmake)

enable_testing()

add_subdirectory(comm)
