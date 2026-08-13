#pragma once
#include "../platform.hpp"
#include <string>
#include <atomic>
#include <unordered_map>
#include <mutex>
#include <memory>

class Router;
class Session;

class Server {
public:
    Server(const std::string& host, int port, Router* router);
    ~Server();
    bool start();
    void stop();
    void run();

private:
    void removeSession(std::shared_ptr<Session> session);

    std::string host_;
    int port_;
    int listenSocket_;
    Router* router_;
    std::atomic<bool> running_;
    std::unordered_map<PlatformSocket, std::shared_ptr<Session>> sessions_;
    std::mutex sessionsMutex_;
};
