#include "network/Session.hpp"
#include "routing/Router.hpp"
#include "utils/Json.hpp"
#include "platform.hpp"
#include <iostream>
#include <cstring>

Session::Session(int socket, Router* router, CloseCallback onClose) : socket_(socket), router_(router), running_(false), onClose_(std::move(onClose)) {}
Session::~Session() {
    stop();
    if (thread_.joinable()) {
        thread_.join();
    }
}
void Session::setUsername(const std::string& username) {
    std::lock_guard<std::mutex> lock(usernameMutex_);
    username_ = username;
}
std::string Session::getUsername() const {
    std::lock_guard<std::mutex> lock(usernameMutex_);
    return username_;
}
void Session::start() {
    running_ = true;
    thread_ = std::thread(&Session::run, this);
}
void Session::stop() {
    bool expected = true;
    if (!running_.compare_exchange_strong(expected, false)) return;
    if (socket_ >= 0) {
        shutdown(socket_, SHUT_RDWR);
        CLOSE_SOCKET(socket_);
        socket_ = -1;
    }
}
bool Session::deliver(const Json& message) {
    std::lock_guard<std::mutex> lock(sendMutex_);
    return sendJson(message.dump());
}
void Session::run() {
    while (running_) {
        uint32_t netLen = 0;
        if (!readAll(reinterpret_cast<uint8_t*>(&netLen), 4)) break;
        uint32_t len = ntohl(netLen);
        if (len == 0 || len > 10 * 1024 * 1024) break;
        std::string data(len, '\0');
        if (!readAll(reinterpret_cast<uint8_t*>(&data[0]), len)) break;
        try {
            Json req = Json::parse(data);
            Json resp = router_->route(req, shared_from_this());
            std::string respStr = resp.dump();
            std::lock_guard<std::mutex> lock(sendMutex_);
            if (!sendJson(respStr)) break;
        } catch (const std::exception& e) {
            Json err;
            err["status"] = "error";
            err["message"] = std::string("Parse error: ") + e.what();
            std::lock_guard<std::mutex> lock(sendMutex_);
            if (!sendJson(err.dump())) break;
        }
    }
    if (onClose_) {
        onClose_(shared_from_this());
    }
}
bool Session::readAll(uint8_t* buffer, size_t len) {
    size_t total = 0;
    while(total < len) {
        ssize_t r = recv(socket_, reinterpret_cast<char*>(buffer + total), len - total, 0);
        if(r <= 0) return false;
        total += static_cast<size_t>(r);
    }
    return true;
}
bool Session::sendJson(const std::string& jsonStr) {
    uint32_t netLen = htonl(static_cast<uint32_t>(jsonStr.size()));
    if(send(socket_, reinterpret_cast<const char*>(&netLen), 4, MSG_NOSIGNAL) != 4) return false;
    if(send(socket_, jsonStr.c_str(), static_cast<int>(jsonStr.size()), MSG_NOSIGNAL) != static_cast<int>(jsonStr.size())) return false;
    return true;
}