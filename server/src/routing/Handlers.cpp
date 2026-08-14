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
void Handlers::userConnected(const std::string& username, std::shared_ptr<Session> session) {
    std::lock_guard<std::mutex> lock(activeUsersMutex_);
    activeUsers_[username] = session;
}
void Handlers::userDisconnected(const std::string& username) {
    std::lock_guard<std::mutex> lock(activeUsersMutex_);
    activeUsers_.erase(username);
    Logger::instance().info("User disconnected: " + username);
}

Json Handlers::handleRegister(const Json& req) { // добавлены новы методы
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
    if(!validateUsername(username, res)) return res;
    if(!rateLimiter_.isAllowed(username)) {
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
    if(db_->getUser(username)) {
        res["status"] = "error";
        res["reason"] = "username_taken";
        res["message"] = "Username already exists";
        return res;
    }
    if(db_->getUserByEmail(email)) {
        res["status"] = "error";
        res["reason"] = "email_taken";
        res["message"] = "Account with this email already exists";
        return res;
    }

    std::string salt = generateToken();
    User user;
    user.username = username;
    user.passwordHash = hashPassword(password, salt);
    user.salt = salt;
    user.email = email;
    user.emailConfirmed = true; // почта не проверяется, аккаунт активен сразу
    db_->addUser(user);
    std::string code = generateToken().substr(0, 6);
    //{
    //    std::lock_guard<std::mutex> lock(codesMutex_);
    //    pendingCodes_[email] = { code, std::chrono::duration_cast<std::chrono::seconds>(std::chrono::system_clock::now().time_since_epoch()).count() + 600 };
    //}
    //sendConfirmationEmail(email, code);
    Logger::instance().info("User registered (pending confirmation): " + username);
    res["status"] = "ok";
    res["message"] = "confirmation_sent";
    return res;
}

void Handlers::sendConfirmationEmail(const std::string& email, const std::string& code) {
    // TODO: тут должна быть настоящая отправка письма (SMTP-библиотека)
    Logger::instance().info("[STUB] Confirmation code for " + email + " = " + code);
}

Json Handlers::handleConfirmationRequest(const Json& req) {
    Json res;
    if(!req.contains("email")) {
        res["status"] = "error";
        res["reason"] = "missing_fields";
        res["message"] = "Missing email";
        return res;
    }
    std::string email = req["email"].getString();
    auto userOpt = db_->getUserByEmail(email);
    if(!userOpt) {
        res["status"] = "error";
        res["reason"] = "account_not_found";
        res["message"] = "No account with this email";
        return res;
    }
    std::string code = generateToken().substr(0, 6);
    {
        std::lock_guard<std::mutex> lock(codesMutex_);
        pendingCodes_[email] = { code, std::chrono::duration_cast<std::chrono::seconds>(std::chrono::system_clock::now().time_since_epoch()).count() + 600 };
    }
    sendConfirmationEmail(email, code);
    res["status"] = "ok";
    res["message"] = "confirmation_sent";
    return res;
}

Json Handlers::handleConfirmationCode(const Json& req) {
    Json res;
    if(!req.contains("email") || !req.contains("code")) {
        res["status"] = "error";
        res["reason"] = "missing_fields";
        res["message"] = "Missing email or code";
        return res;
    }
    std::string email = req["email"].getString();
    std::string code = req["code"].getString();
    long long now = std::chrono::duration_cast<std::chrono::seconds>(std::chrono::system_clock::now().time_since_epoch()).count();
    std::lock_guard<std::mutex> lock(codesMutex_);
    auto it = pendingCodes_.find(email);
    if(it == pendingCodes_.end() || it->second.code != code) {
        res["status"] = "error";
        res["reason"] = "invalid_code";
        res["message"] = "Confirmation code is incorrect";
        return res;
    }
    if(now > it->second.expiresAt) {
        pendingCodes_.erase(it);
        res["status"] = "error";
        res["reason"] = "code_expired";
        res["message"] = "Confirmation code has expired";
        return res;
    }
    auto userOpt = db_->getUserByEmail(email);
    if(userOpt) {
        db_->setEmailConfirmed(userOpt->username);
        if(req.contains("device")) {
            db_->setTrustedDevice(userOpt->username, req["device"]);
        }
    }
    pendingCodes_.erase(it);
    res["status"] = "ok";
    res["message"] = "email_confirmed";
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
    if (!validateUsername(username, res)) return res;
    if (!rateLimiter_.isAllowed(username)) {
        res["status"] = "error";
        res["reason"] = "rate_limited";
        res["message"] = "Too many attempts. Try again in 5 minutes.";
        return res;
    }
    auto userOpt = db_->getUser(username);
    if(!userOpt || hashPassword(password, userOpt->salt) != userOpt->passwordHash) {
        rateLimiter_.recordFailure(username);
        res["status"] = "error";
        res["reason"] = "invalid_credentials";
        res["message"] = "Invalid username or password";
        return res;
    }
    if(!userOpt->emailConfirmed) {
        res["status"] = "error";
        res["reason"] = "email_not_confirmed";
        res["message"] = "Please confirm your email first";
        return res;
    }
    Json device = req.contains("device") ? req["device"] : Json();
    bool deviceOk = true;
    if(userOpt->trustedDevice.contains("device_id")) {
        // уже есть доверенное устройство — сверяем
        std::string trustedId = userOpt->trustedDevice["device_id"].getString();
        std::string incomingId = device.contains("device_id") ? device["device_id"].getString() : "";
        deviceOk = (!incomingId.empty() && incomingId == trustedId);
    } else {
        // первый вход — сохраняем текущее устройство как доверенное
        db_->setTrustedDevice(username, device);
    }
    if(!deviceOk) {
        std::string code = generateToken().substr(0, 6);
        {
            std::lock_guard<std::mutex> lock(codesMutex_);
            pendingCodes_[userOpt->email] = { code, std::chrono::duration_cast<std::chrono::seconds>(std::chrono::system_clock::now().time_since_epoch()).count() + 600 };
        }
        sendConfirmationEmail(userOpt->email, code);
        res["status"] = "error";
        res["reason"] = "device_not_verified";
        res["message"] = "New device detected, email confirmation required";
        return res;
    }
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
    res["email"] = userOpt->email;
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
        auto it = authTokens_.find(token);
        if (it == authTokens_.end()) {
            res["status"] = "error";
            res["message"] = "Invalid token";
            return res;
        }
        from = it->second;
    }
    if (!rateLimiter_.isAllowed(from)) {  // rate limit по username, не по token
        res["status"] = "error";
        res["message"] = "Rate limited";
        return res;
    }
    if (!validateUsername(to, res)) return res;
    if (!validateContent(content, res)) return res;
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
            res["message"] = "Invalid token";
            return res;
        }
        username = it->second;
    }
    if (!rateLimiter_.isAllowed(username)) {
        res["status"] = "error";
        res["message"] = "Rate limited";
        return res;
    }
    if (!validateUsername(peer, res)) return res;
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
            res["message"]="Invalid token"; 
            return res; 
        }
        username = it->second;
    }
    if (!rateLimiter_.isAllowed(username)) {
        res["status"] = "error";
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
        res["message"] = "Missing token or key_data";
        return res;
    }
    std::string token = req["token"].getString();
    std::string keyData = req["key_data"].getString();
    if (!validatePublicKey(keyData, res)) return res;
    std::string username;
    {
        std::lock_guard<std::mutex> lock(sessionMutex_);
        auto it = authTokens_.find(token);
        if(it == authTokens_.end()) {
            res["status"] = "error";
            res["message"] = "Invalid token";
            return res;
        }
        username = it->second;
    }
    if (!rateLimiter_.isAllowed(username)) {
        res["status"] = "error";
        res["message"] = "Rate limited";
        return res;
    }
    if(db_->updateUserPublicKey(username,keyData)) {
        Logger::instance().info("Public key uploaded for: " + username);
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
    std::string requester;
    {
        std::lock_guard<std::mutex> lock(sessionMutex_);
        auto it = authTokens_.find(token);
        if(it == authTokens_.end()) { 
            res["status"]="error"; 
            res["message"]="Invalid token"; 
            return res; 
        }
        requester = it->second;
    }
    if(!rateLimiter_.isAllowed(requester)) {
        res["status"] = "error";
        res["message"] = "Rate limited";
        return res;
    }
    if(!req.contains("username")) {
        res["status"] = "error";
        res["message"] = "Missing username";
        return res;
    }
    std::string username = req["username"].getString();
    if (!validateUsername(username, res)) return res;
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
