cmake_minimum_required(VERSION 3.14)
project(MessengerServer CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

file(GLOB_RECURSE SOURCES "src/*.cpp")
add_executable(messenger_server ${SOURCES})

target_include_directories(messenger_server PRIVATE src)
