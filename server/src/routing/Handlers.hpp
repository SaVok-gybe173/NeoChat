#pragma once
#include "utils/Json.hpp"
#include "utils/Logger.hpp"
#include "utils/RateLimiter.hpp"
#include "database/IDatabase.hpp"
#include "crypto/ICrypto.hpp"
#include <string>
#include <map>
#include <mutex>
#include <unordered_map>
#include <memory>

class Session;

class Handlers {
public:
    Handlers(IDatabase* db, ICrypto* hasher);
    Json handleRegister(const Json& req);
    Json handleLogin(const Json& req, std::shared_ptr<Session> session);
    Json handleSendMessage(const Json& req);
    Json handleGetMessages(const Json& req);
    Json handleGetUsers(const Json& req);
    Json handleLogout(const Json& req, std::shared_ptr<Session> session);
    Json handleUploadKey(const Json& req);
    Json handleGetKey(const Json& req);
    void userConnected(const std::string& username, std::shared_ptr<Session> session);
    void userDisconnected(const std::string& username);
private:
    std::string generateToken();
    std::string hashPassword(const std::string& password, const std::string& salt);
    bool validateUsername(const std::string& username, Json& outError);
    bool validateContent(const std::string& content, Json& outError);
    bool validatePublicKey(const std::string& key, Json& outError);
    bool validateEmail(const std::string& email, Json& outError);
    IDatabase* db_;
    ICrypto* hasher_;
    std::map<std::string, std::string> authTokens_;
    std::mutex sessionMutex_;
    std::unordered_map<std::string, std::weak_ptr<Session>> activeUsers_;
    std::mutex activeUsersMutex_;
    RateLimiter rateLimiter_;
};
