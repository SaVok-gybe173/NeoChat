#pragma once
#include "utils/Json.hpp"
#include <memory>

class Handlers;
class Session;

class Router {
public:
    Router(Handlers* handlers);
    Json route(const Json& request, std::shared_ptr<Session> session);
    void onUserDisconnected(const std::string& username);

private:
    Handlers* handlers_;
};