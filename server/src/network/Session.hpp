#pragma once
#include <thread>
#include <atomic>
#include <functional>
#include <memory>
#include <mutex>
#include <string>
#include "utils/Json.hpp"

class Router;
class Session : public std::enable_shared_from_this<Session> {
    public:
    using CloseCallback = std::function<void(std::shared_ptr<Session>)>;
    Session(PlatformSocket socket, Router* router, CloseCallback onClose);
    ~Session();
    void start();
    void stop();
    bool deliver(const Json& message);
    void setUsername(const std::string& username);
    std::string getUsername() const;
    private:
    void run();
    bool readAll(uint8_t* buffer, size_t len);
    bool sendJson(const std::string& jsonStr);
    int socket_;
    Router* router_;
    std::thread thread_;
    std::atomic<bool> running_;
    CloseCallback onClose_;
    std::mutex sendMutex_;
    std::string username_;
    mutable std::mutex usernameMutex_;
};
