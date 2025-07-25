cmake_minimum_required(VERSION 3.16)
project(turing-bench LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_subdirectory(turingdb-sdk-cpp)

add_executable(turing-bench main.cpp)
target_link_libraries(turing-bench PRIVATE turing_client_cpp_s)

