#include "routing/Handlers.hpp"
#include "network/Session.hpp"
#include <random>
#include <chrono>
#include <sstream>
#include <iomanip>

Handlers::Handlers(IDatabase* db, ICrypto* hasher) : db_(db), hasher_(hasher) {}
std::string Handlers::generateToken() {
    std::random_device rd;
    std::stringstream ss;
    ss << std::hex << std::setfill('0');
    for(int i = 0; i < 4; i++) ss << std::setw(8) << rd();
    return ss.str();
}
std::string Handlers::hashPassword(const std::string& password, const std::string& salt) {
    return hasher_->hash(password + salt);
}
bool Handlers::validateUsername(const std::string& username, Json& outError) {
    if(username.empty() || username.size() > 32) {
        outError["status"] = "error";
        outError["message"] = "Username must be 1-32 characters";
        return false;
    }
    return true;
}
bool Handlers::validateContent(const std::string& content, Json& outError) {
    if(content.empty() || content.size() > 4096) {
        outError["status"] = "error";
        outError["message"] = "Content must be 1-4096 characters";
        return false;
    }
    return true;
}
bool Handlers::validatePublicKey(const std::string& key, Json& outError) {
    if(key.empty() || key.size() > 256) {
        outError["status"] = "error";
        outError["message"] = "Public key too large (max 256 chars)";
        return false;
    }
    return true;
}
bool Handlers::validateEmail(const std::string& email, Json& outError) {
    // Базовая проверка формата без внешних библиотек
    if(email.empty() || email.size() > 254) {
        outError["status"] = "error";
        outError["message"] = "Email must be 1-254 characters";
        return false;
    }
    size_t at = email.find('@');
    // ровно один @, не в начале и не в конце
    if(at == std::string::npos || at == 0 || at == email.size() - 1) {
        outError["status"] = "error";
        outError["message"] = "Invalid email format";
        return false;
    }
    if(email.find('@', at + 1) != std::string::npos) {
        outError["status"] = "error";
        outError["message"] = "Invalid email format";
        return false;
    }
    std::string domain = email.substr(at + 1);
    // в домене должна быть точка, и он не должен начинаться/заканчиваться точкой
    if(domain.find('.') == std::string::npos ||
       domain.front() == '.' || domain.back() == '.') {
        outError["status"] = "error";
        outError["message"] = "Invalid email format";
        return false;
    }
    return true;
}
void Handlers::userConnected(const std::string& username, std::shared_ptr<Session> session) {
    std::lock_guard<std::mutex> lock(activeUsersMutex_);
    activeUsers_[username] = session;
}
void Handlers::userDisconnected(const std::string& username) {
    std::lock_guard<std::mutex> lock(activeUsersMutex_);
    activeUsers_.erase(username);
    Logger::instance().info("User disconnected: " + username);
}
Json Handlers::handleRegister(const Json& req) {
    Json res;
    if(!req.contains("username") || !req.contains("password") || !req.contains("email")) {
        res["status"] = "error";
        res["reason"] = "missing_fields";
        res["message"] = "Missing username, password or email";
        return res;
    }
    std::string username = req["username"].getString();
    std::string password = req["password"].getString();
    std::string email = req["email"].getString();
    if(!validateUsername(username, res)) {
        res["reason"] = "invalid_username";
        return res;
    }
    if(!validateEmail(email, res)) {
        res["reason"] = "invalid_email";
        return res; 
    }
    if(!rateLimiter_.isAllowed(username)) {
        Logger::instance().warn("Rate limit hit for register: " + username);
        res["status"] = "error";
        res["reason"] = "rate_limited";
        res["message"] = "Too many attempts. Try again in 5 minutes.";
        return res;
    }
    if(password.empty() || password.size() > 128) {
        res["status"] = "error";
        res["reason"] = "invalid_password";
        res["message"] = "Password must be 1-128 characters";
        return res;
    }
    // Уникальность email
    if(db_->getUserByEmail(email)) {
        Logger::instance().warn("Registration failed (email exists): " + email);
        res["status"] = "error";
        res["reason"] = "email_taken";
        res["message"] = "Email already registered";
        return res;
    }
    std::string salt = generateToken(); // 128-bit
    User user;
    user.username = username;
    user.passwordHash = hashPassword(password, salt);
    user.salt = salt;
    user.email = email;
    if(db_->addUser(user)) {
        Logger::instance().info("User registered: " + username);
        res["status"] = "ok";
        res["message"] = "User registered";
    } else {
        Logger::instance().warn("Registration failed (exists): " + username);
        res["status"] = "error";
        res["reason"] = "username_taken";
        res["message"] = "Username already exists";
    }
    return res;
}
Json Handlers::handleLogin(const Json& req, std::shared_ptr<Session> session) {
    Json res;
    if(!req.contains("username") || !req.contains("password")) {
        res["status"] = "error";
        res["reason"] = "missing_fields";
        res["message"] = "Missing username or password";
        return res;
    }
    std::string username = req["username"].getString();
    std::string password = req["password"].getString();
    if (!validateUsername(username, res)) {
        res["reason"] = "invalid_username";
        return res;
    }
    if (!rateLimiter_.isAllowed(username)) {
        Logger::instance().warn("Rate limit hit for login: " + username);
        res["status"] = "error";
        res["reason"] = "rate_limited";
        res["message"] = "Too many attempts. Try again in 5 minutes.";
        return res;
    }
    auto userOpt = db_->getUser(username);
    if(!userOpt) {
        rateLimiter_.recordFailure(username);
        res["status"] = "error";
        res["reason"] = "invalid_credentials";
        res["message"] = "Invalid credentials";
        return res;
    }
    User user = *userOpt;
    if(hashPassword(password, user.salt) == user.passwordHash) {
        rateLimiter_.recordSuccess(username);
        std::string token = generateToken();
        {
            std::lock_guard<std::mutex> lock(sessionMutex_);
            authTokens_[token] = username;
        }
        if(session) {
            session->setUsername(username);
            userConnected(username, session);
        }
        Logger::instance().info("User logged in: " + username);
        res["status"] = "ok";
        res["token"] = token;
        res["username"] = username;
    } else {
        rateLimiter_.recordFailure(username);
        Logger::instance().warn("Failed login for user: " + username);
        res["status"] = "error";
        res["reason"] = "invalid_credentials";
        res["message"] = "Invalid credentials";
    }
    return res;
}
Json Handlers::handleSendMessage(const Json& req) {
    Json res;
    if(!req.contains("token") || !req.contains("to") || !req.contains("content")) {
        res["status"] = "error";
        res["reason"] = "missing_fields";
        res["message"] = "Missing fields";
        return res;
    }
    std::string token = req["token"].getString();
    std::string to = req["to"].getString();
    std::string content = req["content"].getString();
    std::string from;
    {
        std::lock_guard<std::mutex> lock(sessionMutex_);
        auto it = authTokens_.find(token);
        if (it == authTokens_.end()) {
            res["status"] = "error";
            res["reason"] = "invalid_token";
            res["message"] = "Invalid token";
            return res;
        }
        from = it->second;
    }
    if (!rateLimiter_.isAllowed(from)) {  // rate limit по username, не по token
        res["status"] = "error";
        res["reason"] = "rate_limited";
        res["message"] = "Rate limited";
        return res;
    }
    if (!validateUsername(to, res)) {
        res["reason"] = "invalid_username";
        return res;
    }
    if (!validateContent(content, res)) {
        res["reason"] = "invalid_content";
        return res;
    }
    if (!db_->getUser(to)) {
        res["status"] = "error";
        res["reason"] = "user_not_found";
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
    msg.salt = req.contains("salt") ? req["salt"].getString() : "";
    std::shared_ptr<Session> targetSession;
    {
        std::lock_guard<std::mutex> lock(activeUsersMutex_);
        auto it = activeUsers_.find(to);
        if(it != activeUsers_.end()) { 
            targetSession = it->second.lock();
            if (!targetSession) {
                activeUsers_.erase(it); // Сессия умерла
            }
        }
    }
    bool deliveredOnline = false;
    if(targetSession) {
        Json push;
        push["type"] = "push";
        push["action"] = "new_message";
        push["from"] = from;
        push["content"] = content;
        push["timestamp"] = msg.timestamp;
        push["encrypted"] = msg.encrypted;
        push["ephemeral_key"] = msg.ephemeralKey;
        push["nonce"] = msg.nonce;
        push["salt"] = msg.salt;
        if(targetSession->deliver(push)) {
            deliveredOnline = true;
        }
    }
    db_->addMessage(msg);
    Logger::instance().info("Message from " + from + " to " + to + " (online=" + (deliveredOnline ? "yes" : "no") + ")");
    res["status"] = "ok";
    res["message"] = "Message sent";
    res["delivered_online"] = deliveredOnline;
    return res;
}
Json Handlers::handleGetMessages(const Json& req) {
    Json res;
    if(!req.contains("token") || !req.contains("peer")) {
        res["status"] = "error";
        res["reason"] = "missing_fields";
        res["message"] = "Missing fields";
        return res;
    }
    std::string token = req["token"].getString();
    std::string peer = req["peer"].getString();
    std::string username;
    {
        std::lock_guard<std::mutex> lock(sessionMutex_);
        auto it = authTokens_.find(token);
        if(it == authTokens_.end()) {
            res["status"] = "error";
            res["reason"] = "invalid_token";
            res["message"] = "Invalid token";
            return res;
        }
        username = it->second;
    }
    if (!rateLimiter_.isAllowed(username)) {
        res["status"] = "error";
        res["reason"] = "rate_limited";
        res["message"] = "Rate limited";
        return res;
    }
    if (!validateUsername(peer, res)) {
        res["reason"] = "invalid_username";
        return res;
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
        obj["salt"] = m.salt;
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
        res["reason"] = "missing_fields";
        res["message"] = "Missing token";
        return res;
    }
    std::string token = req["token"].getString();
    std::string username;
    {
        std::lock_guard<std::mutex> lock(sessionMutex_);
        auto it = authTokens_.find(token);
        if(it == authTokens_.end()) { 
            res["status"]="error";
            res["reason"] = "invalid_token";
            res["message"]="Invalid token"; 
            return res; 
        }
        username = it->second;
    }
    if (!rateLimiter_.isAllowed(username)) {
        res["status"] = "error";
        res["reason"] = "rate_limited";
        res["message"] = "Rate limited";
        return res;
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
        res["reason"] = "missing_fields";
        res["message"] = "Missing token";
        return res;
    }
    std::string token = req["token"].getString();
    std::string username;
    {
        std::lock_guard<std::mutex> lock(sessionMutex_);
        auto it = authTokens_.find(token);
        if(it != authTokens_.end()) {
            username = it->second;
            authTokens_.erase(it);
        }
    }
    if(!username.empty()) {
        userDisconnected(username);
    }
    Logger::instance().info("User logged out: " + (username.empty() ? "unknown" : username));
    res["status"] = "ok";
    res["message"] = "Logged out";
    return res;
}
Json Handlers::handleUploadKey(const Json& req) {
    Json res;
    if(!req.contains("token") || !req.contains("key_data")) {
        res["status"] = "error";
        res["reason"] = "missing_fields";
        res["message"] = "Missing token or key_data";
        return res;
    }
    std::string token = req["token"].getString();
    std::string keyData = req["key_data"].getString();
    if (!validatePublicKey(keyData, res)) {
        res["reason"] = "invalid_key";
        return res;
    }
    std::string username;
    {
        std::lock_guard<std::mutex> lock(sessionMutex_);
        auto it = authTokens_.find(token);
        if(it == authTokens_.end()) {
            res["status"] = "error";
            res["reason"] = "invalid_token";
            res["message"] = "Invalid token";
            return res;
        }
        username = it->second;
    }
    if (!rateLimiter_.isAllowed(username)) {
        res["status"] = "error";
        res["reason"] = "rate_limited";
        res["message"] = "Rate limited";
        return res;
    }
    if(db_->updateUserPublicKey(username,keyData)) {
        Logger::instance().info("Public key uploaded for: " + username);
        res["status"] = "ok";
        res["message"] = "Public key uploaded";
    } else {
        res["status"] = "error";
        res["reason"] = "user_not_found";
        res["message"] = "User not found";
    }
    return res;
}
Json Handlers::handleGetKey(const Json& req) {
    Json res;
    // Требуем token, чтобы исключить перебор username
    if(!req.contains("token")) {
        res["status"] = "error";
        res["reason"] = "missing_fields";
        res["message"] = "Missing token";
        return res;
    }
    std::string token = req["token"].getString();
    std::string requester;
    {
        std::lock_guard<std::mutex> lock(sessionMutex_);
        auto it = authTokens_.find(token);
        if(it == authTokens_.end()) { 
            res["status"]="error";
            res["reason"] = "invalid_token";
            res["message"]="Invalid token"; 
            return res; 
        }
        requester = it->second;
    }
    if(!rateLimiter_.isAllowed(requester)) {
        res["status"] = "error";
        res["reason"] = "rate_limited";
        res["message"] = "Rate limited";
        return res;
    }
    if(!req.contains("username")) {
        res["status"] = "error";
        res["reason"] = "missing_fields";
        res["message"] = "Missing username";
        return res;
    }
    std::string username = req["username"].getString();
    if (!validateUsername(username, res)) {
        res["reason"] = "invalid_username";
        return res;
    }
    auto keyOpt = db_->getUserPublicKey(username);
    if(keyOpt) {
        res["status"] = "ok";
        res["key_data"] = *keyOpt;
    } else {
        res["status"] = "error";
        res["reason"] = "key_not_found";
        res["message"] = "Public key not found";
    }
    return res;
}
