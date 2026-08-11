#include "network/Server.hpp"
#include "network/Session.hpp"
#include "routing/Router.hpp"
#include "platform.hpp"
#include <iostream>
#include <cstring>

Server::Server(const std::string& host, int port, Router* router) : host_(host), port_(port), listenSocket_(INVALID_PLATFORM_SOCKET), router_(router), running_(false) {}

Server::~Server() {
    stop();
}

bool Server::start() {
    if (!init_winsock()) {
        std::cerr << "WSAStartup failed\n";
        return false;
    }

    listenSocket_ = socket(AF_INET, SOCK_STREAM, 0);
    if (listenSocket_ == INVALID_PLATFORM_SOCKET) {
        std::cerr << "socket failed (code: " << ERRNO << ")\n";
        return false;
    }

    int opt = 1;
    if (setsockopt(listenSocket_, SOL_SOCKET, SO_REUSEADDR,
                   SETSOCKOPT_PTR(&opt), sizeof(opt)) < 0) {
        std::cerr << "setsockopt failed (code: " << ERRNO << ")\n";
        CLOSE_SOCKET(listenSocket_);
        return false;
    }

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port_);
    if (inet_pton(AF_INET, host_.c_str(), &addr.sin_addr) <= 0) {
        std::cerr << "Invalid host: " << host_ << "\n";
        CLOSE_SOCKET(listenSocket_);
        return false;
    }

    if (bind(listenSocket_, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
        std::cerr << "bind failed (code: " << ERRNO << ")\n";
        CLOSE_SOCKET(listenSocket_);
        return false;
    }

    if (listen(listenSocket_, 128) < 0) {
        std::cerr << "listen failed (code: " << ERRNO << ")\n";
        CLOSE_SOCKET(listenSocket_);
        return false;
    }

    running_ = true;
    std::cout << "Server listening on " << host_ << ":" << port_ << "\n";
    return true;
}

void Server::stop() {
    if (!running_.exchange(false)) return;

    if (listenSocket_ != INVALID_PLATFORM_SOCKET) {
        CLOSE_SOCKET(listenSocket_);
        listenSocket_ = INVALID_PLATFORM_SOCKET;
    }

    std::unordered_map<PlatformSocket, std::shared_ptr<Session>> copy;
    {
        std::lock_guard<std::mutex> lock(sessionsMutex_);
        copy = std::move(sessions_);
    }

    for (auto& [fd, session] : copy) {
        session->stop();
    }

    cleanup_winsock();
}

void Server::run() {
    while (running_) {
        sockaddr_in clientAddr{};
        socklen_t addrLen = sizeof(clientAddr);
        PlatformSocket clientSocket = accept(listenSocket_, reinterpret_cast<sockaddr*>(&clientAddr), &addrLen);
        if (clientSocket_ == INVALID_PLATFORM_SOCKET) {
            if (ERRNO == ERR_EINTR) continue;
            if (running_) std::cerr << "accept failed (code: " << ERRNO << ")\n";
            break;
        }

        auto session = std::make_shared<Session>(
            clientSocket,
            router_,
            [this](std::shared_ptr<Session> s) { this->removeSession(s); }
        );

        {
            std::lock_guard<std::mutex> lock(sessionsMutex_);
            sessions_[clientSocket] = session;
        }

        session->start();
    }
}


void Server::removeSession(std::shared_ptr<Session> session) {
    {
        std::lock_guard<std::mutex> lock(sessionsMutex_);
        sessions_.erase(session->getSocket());
    }

    if (session && router_) {
        std::string username = session->getUsername();
        if (!username.empty()) {
            router_->onUserDisconnected(username);
        }
    }
}
