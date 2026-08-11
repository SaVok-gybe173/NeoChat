#include "routing/Handlers.hpp"
#include "network/Session.hpp"
#include <random>
#include <chrono>
#include <sstream>
#include <iomanip>

Handlers::Handlers(IDatabase* db, ICrypto* hasher) : db_(db), hasher_(hasher) {}
std::string Handlers::generateToken() {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, 15);
    std::stringstream ss;
    for(int i = 0; i < 32; i++) ss << std::hex << dis(gen);
    return ss.str();
}
std::string Handlers::hashPassword(const std::string& password, const std::string& salt) {
    return hasher_->hash(password + salt);
}
void Handlers::userConnected(const std::string& username, std::shared_ptr<Session> session) {
    std::lock_guard<std::mutex> lock(activeUsersMutex_);
    activeUsers_[username] = session;
}
void Handlers::userDisconnected(const std::string& username) {
    std::lock_guard<std::mutex> lock(activeUsersMutex_);
    activeUsers_.erase(username);
}
Json Handlers::handleRegister(const Json& req) {
    Json res;
    if(!req.contains("username") || !req.contains("password")) {
        res["status"] = "error";
        res["message"] = "Empty username or password";
        return res;
    }
    std::string username = req["username"].getString();
    std::string password = req["password"].getString();
    if(username.empty() || password.empty()) {
        res["status"] = "error";
        res["message"] = "Empty username or password";
        return res;
    }
    std::string salt = generateToken().substr(0, 16);
    User user;
    user.username = username;
    user.passwordHash = hashPassword(password, salt);
    user.salt = salt;
    if(db_->addUser(user)) {
        res["status"] = "ok";
        res["message"] = "User registered";
    } else {
        res["status"] = "error";
        res["message"] = "Username already exists";
    }
    return res;
}
Json Handlers::handleLogin(const Json& req, std::shared_ptr<Session> session) {
    Json res;
    if(!req.contains("username") || !req.contains("password")) {
        res["status"] = "error";
        res["message"] = "Missing username or password";
        return res;
    }
    std::string username = req["username"].getString();
    std::string password = req["password"].getString();
    auto userOpt = db_->getUser(username);
    if(!userOpt) {
        res["status"] = "error";
        res["message"] = "Invalid credentials";
        return res;
    }
    User user = *userOpt;
    if(hashPassword(password, user.salt) == user.passwordHash) {
        std::string token = generateToken();
        {
            std::lock_guard<std::mutex> lock(sessionMutex_);
            sessions_[token] = username;
        }
        if(session) {
            session->setUsername(username);
            userConnected(username, session);
        }
        res["status"] = "ok";
        res["token"] = token;
        res["username"] = username;
    } else {
        res["status"] = "error";
        res["message"] = "Invalid credentials";
    }
    return res;
}
Json Handlers::handleSendMessage(const Json& req) {
    Json res;
    if(!req.contains("token") || !req.contains("to") || !req.contains("content")) {
        res["status"] = "error";
        res["message"] = "Missing fields";
        return res;
    }
    std::string token = req["token"].getString();
    std::string to = req["to"].getString();
    std::string content = req["content"].getString();
    std::string from;
    {
        std::lock_guard<std::mutex> lock(sessionMutex_);
        auto it = sessions_.find(token);
        if(it == sessions_.end()) {
            res["status"] = "error";
            res["message"] = "Invalid token";
            return res;
        }
        from = it->second;
    }
    if (!db_->getUser(to)) {
        res["status"] = "error";
        res["message"] = "Recipient not found";
        return res;
    }
    Message msg;
    msg.from = from;
    msg.to = to;
    msg.content = content;
    msg.timestamp = std::chrono::duration_cast<std::chrono::seconds>(std::chrono::system_clock::now().time_since_epoch()).count();
    msg.encrypted = req.contains("encrypted") ? req["encrypted"].getBool() : false;
    msg.ephemeralKey = req.contains("ephemeral_key") ? req["ephemeral_key"].getString() : "";
    msg.nonce = req.contains("nonce") ? req["nonce"].getString() : "";
    bool deliveredOnline = false;
    {
        std::lock_guard<std::mutex> lock(activeUsersMutex_);
        auto it = activeUsers_.find(to);
        if(it != activeUsers_.end()) {
            if(auto s = it->second.lock()) {
                Json push;
                push["type"] = "push";
                push["action"] = "new_message";
                push["from"] = from;
                push["content"] = content;
                push["timestamp"] = msg.timestamp;
                push["encrypted"] = msg.encrypted;
                push["ephemeral_key"] = msg.ephemeralKey;
                push["nonce"] = msg.nonce;
                if(s->deliver(push)) {
                    deliveredOnline = true;
                }
            } else {
                activeUsers_.erase(it);
            }
        }
    }
    db_->addMessage(msg);
    res["status"] = "ok";
    res["message"] = "Message sent";
    res["delivered_online"] = deliveredOnline;
    return res;
}
Json Handlers::handleGetMessages(const Json& req) {
    Json res;
    if(!req.contains("token") || !req.contains("peer")) {
        res["status"] = "error";
        res["message"] = "Missing fields";
        return res;
    }
    std::string token = req["token"].getString();
    std::string peer = req["peer"].getString();
    std::string username;
    {
        std::lock_guard<std::mutex> lock(sessionMutex_);
        auto it = sessions_.find(token);
        if(it == sessions_.end()) {
            res["status"] = "error";
            res["message"] = "Invalid token";
            return res;
        }
        username = it->second;
    }
    int limit = req.contains("limit") ? req["limit"].getInt() : 100;
    int offset = req.contains("offset") ? req["offset"].getInt() : 0;
    if(limit < 0) limit = 0;
    if(offset < 0) offset = 0;
    auto messages = db_->getMessages(username, peer, limit, offset);
    Json arr;
    for(const auto& m : messages) {
        Json obj;
        obj["id"] = m.id;
        obj["from"] = m.from;
        obj["to"] = m.to;
        obj["content"] = m.content;
        obj["timestamp"] = m.timestamp;
        obj["encrypted"] = m.encrypted;
        obj["ephemeral_key"] = m.ephemeralKey;
        obj["nonce"] = m.nonce;
        arr.push_back(obj);
    }
    res["status"] = "ok";
    res["messages"] = arr;
    return res;
}
Json Handlers::handleGetUsers(const Json& req) {
    Json res;
    if(!req.contains("token")) {
        res["status"] = "error";
        res["message"] = "Missing token";
        return res;
    }
    std::string token = req["token"].getString();
    {
        std::lock_guard<std::mutex> lock(sessionMutex_);
        if(sessions_.find(token) == sessions_.end()) {
            res["status"] = "error";
            res["message"] = "Invalid token";
            return res;
        }
    }
    auto users = db_->getAllUsers();
    Json arr;
    for(const auto& u : users) arr.push_back(u);
    res["status"] = "ok";
    res["users"] = arr;
    return res;
}
Json Handlers::handleLogout(const Json& req, std::shared_ptr<Session> session) {
    Json res;
    if(!req.contains("token")) {
        res["status"] = "error";
        res["message"] = "Missing token";
        return res;
    }
    std::string token = req["token"].getString();
    std::string username;
    {
        std::lock_guard<std::mutex> lock(sessionMutex_);
        auto it = sessions_.find(token);
        if(it != sessions_.end()) {
            username = it->second;
            sessions_.erase(it);
        }
    }
    if(!username.empty()) {
        userDisconnected(username);
    }
    res["status"] = "ok";
    res["message"] = "Logged out";
    return res;
}
Json Handlers::handleUploadKey(const Json& req) {
    Json res;
    if(!req.contains("token") || !req.contains("key_data")) {
        res["status"] = "error";
        res["message"] = "Missing token or key_data";
        return res;
    }
    std::string token = req["token"].getString();
    std::string keyData = req["key_data"].getString();
    std::string username;
    {
        std::lock_guard<std::mutex> lock(sessionMutex_);
        auto it = sessions_.find(token);
        if(it == sessions_.end()) {
            res["status"] = "error";
            res["message"] = "Invalid token";
            return res;
        }
        username = it->second;
    }
    if(db_->updateUserPublicKey(username,keyData)) {
        res["status"] = "ok";
        res["message"] = "Public key uploaded";
    } else {
        res["status"] = "error";
        res["message"] = "User not found";
    }
    return res;
}
Json Handlers::handleGetKey(const Json& req) {
    Json res;
    // Требуем token, чтобы исключить перебор username
    if(!req.contains("token")) {
        res["status"] = "error";
        res["message"] = "Missing token";
        return res;
    }
    std::string token = req["token"].getString();
    {
        std::lock_guard<std::mutex> lock(sessionMutex_);
        if(sessions_.find(token) == sessions_.end()) {
            res["status"] = "error";
            res["message"] = "Invalid token";
            return res;
        }
    }
    if(!req.contains("username")) {
        res["status"] = "error";
        res["message"] = "Missing username";
        return res;
    }
    std::string username = req["username"].getString();
    auto keyOpt = db_->getUserPublicKey(username);
    if(keyOpt) {
        res["status"] = "ok";
        res["key_data"] = *keyOpt;
    } else {
        res["status"] = "error";
        res["message"] = "Public key not found";
    }
    return res;
}