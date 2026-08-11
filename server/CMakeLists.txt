cmake_minimum_required(VERSION 3.14)
project(MessengerServer CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Threads REQUIRED)

add_executable(messenger_server
    src/main.cpp
    src/config/Config.cpp
    src/crypto/Sha256Hasher.cpp
    src/database/JsonDatabase.cpp
    src/network/Server.cpp
    src/network/Session.cpp
    src/routing/Handlers.cpp
    src/routing/Router.cpp
)

target_include_directories(messenger_server PRIVATE src)
target_link_libraries(messenger_server Threads::Threads)
