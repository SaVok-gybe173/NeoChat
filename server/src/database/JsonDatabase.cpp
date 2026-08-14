#include "JsonDatabase.hpp"
#include <fstream>
#include <sstream>
#include <algorithm>
#include <chrono>
#include <optional>
#include <filesystem>

JsonDatabase::JsonDatabase(const std::string& usersFile, const std::string& messagesFile)
    : usersFile_(usersFile), messagesFile_(messagesFile) {}

JsonDatabase::~JsonDatabase() {
    stopFlush_ = true;
    if (flushThread_.joinable()) flushThread_.join();
    flush();
}

bool JsonDatabase::init() {
    loadUsers();
    loadMessages();
    flushThread_ = std::thread([this]() {
        while (!stopFlush_) {
            std::this_thread::sleep_for(std::chrono::seconds(5));
            flush();
        }
    });
    return true;
}

void JsonDatabase::flush() {
    std::lock_guard<std::mutex> lock(mutex_);
    if (dirtyUsers_.exchange(false)) {
        saveUsers();
    }
    if (dirtyMessages_.exchange(false)) {
        saveMessages();
    }
}

void JsonDatabase::loadUsers() {
    std::ifstream f(usersFile_);
    if (!f.is_open()) {
        usersJson_ = Json(std::map<std::string, Json>{{"users", Json(std::vector<Json>())}});
        return;
    }
    std::stringstream buf;
    buf << f.rdbuf();
    try {
        usersJson_ = Json::parse(buf.str());
    } catch (...) {
        usersJson_ = Json(std::map<std::string, Json>{{"users", Json(std::vector<Json>())}});
    }
    if (!usersJson_.contains("users")) {
        usersJson_["users"] = Json(std::vector<Json>());
    }
}

void JsonDatabase::saveUsers() {
    std::string tmp = usersFile_ + ".tmp";
    std::ofstream f(tmp);
    if (f.is_open()) {
        f << usersJson_.dump(2);
        f.close();
        std::filesystem::rename(tmp, usersFile_);
    }
}

void JsonDatabase::loadMessages() {
    std::ifstream f(messagesFile_);
    if (!f.is_open()) {
        messagesJson_ = Json(std::map<std::string, Json>{{"messages", Json(std::vector<Json>())}});
        return;
    }
    std::stringstream buf;
    buf << f.rdbuf();
    try {
        messagesJson_ = Json::parse(buf.str());
    } catch (...) {
        messagesJson_ = Json(std::map<std::string, Json>{{"messages", Json(std::vector<Json>())}});
    }
    if (!messagesJson_.contains("messages")) {
        messagesJson_["messages"] = Json(std::vector<Json>());
    }
    nextMsgId_ = 1;
    for (const auto& m : messagesJson_["messages"].arrayValue) {
        long long id = m["id"].getLongLong();
        if (id >= nextMsgId_) nextMsgId_ = id + 1;
    }
}

void JsonDatabase::saveMessages() {
    std::string tmp = messagesFile_ + ".tmp";
    std::ofstream f(tmp);
    if (f.is_open()) {
        f << messagesJson_.dump(2);
        f.close();
        std::filesystem::rename(tmp, messagesFile_);
    }
}

bool JsonDatabase::addUser(const User& user) {
    std::lock_guard<std::mutex> lock(mutex_);
    for (const auto& u : usersJson_["users"].arrayValue) {
        if (u["username"].getString() == user.username) return false;
    }
    Json obj;
    obj["username"] = user.username;
    obj["passwordHash"] = user.passwordHash;
    obj["salt"] = user.salt;
    obj["email"] = user.email;
    obj["emailConfirmed"] = user.emailConfirmed;
    usersJson_["users"].push_back(obj);
    dirtyUsers_ = true;
    return true;
}

std::optional<User> JsonDatabase::getUser(const std::string& username) {
    std::lock_guard<std::mutex> lock(mutex_);
    for (const auto& u : usersJson_["users"].arrayValue) {
        if (u["username"].getString() == username) {
            User res;
            res.username = u["username"].getString();
            res.passwordHash = u["passwordHash"].getString();
            res.salt = u["salt"].getString();
            if (u.contains("public_key")) res.publicKey = u["public_key"].getString();
            if (u.contains("email")) res.email = u["email"].getString();
            if (u.contains("emailConfirmed")) res.emailConfirmed = u["emailConfirmed"].getBool();
            if (u.contains("trustedDevice")) res.trustedDevice = u["trustedDevice"];
            return res;
        }
    }
    return std::nullopt;
}

bool JsonDatabase::updateUserPublicKey(const std::string& username, const std::string& publicKey) {
    std::lock_guard<std::mutex> lock(mutex_);
    for (auto& u : usersJson_["users"].arrayValue) {
        if (u["username"].getString() == username) {
            u["public_key"] = publicKey;
            dirtyUsers_ = true;
            return true;
        }
    }
    return false;
}

std::optional<std::string> JsonDatabase::getUserPublicKey(const std::string& username) {
    std::lock_guard<std::mutex> lock(mutex_);
    for (const auto& u : usersJson_["users"].arrayValue) {
        if (u["username"].getString() == username) {
            if (u.contains("public_key")) return u["public_key"].getString();
            break;
        }
    }
    return std::nullopt;
}

std::optional<User> JsonDatabase::getUserByEmail(const std::string& email) {
    std::lock_guard<std::mutex> lock(mutex_);
    for (const auto& u : usersJson_["users"].arrayValue) {
        if (u.contains("email") && u["email"].getString() == email) {
            User res;
            res.username = u["username"].getString();
            res.passwordHash = u["passwordHash"].getString();
            res.salt = u["salt"].getString();
            res.email = u["email"].getString();
            res.emailConfirmed = u.contains("emailConfirmed") ? u["emailConfirmed"].getBool() : false;
            return res;
        }
    }
    return std::nullopt;
}

bool JsonDatabase::setEmailConfirmed(const std::string& username) {
    std::lock_guard<std::mutex> lock(mutex_);
    for (auto& u : usersJson_["users"].arrayValue) {
        if (u["username"].getString() == username) {
            u["emailConfirmed"] = true;
            dirtyUsers_ = true;
            return true;
        }
    }
    return false;
}

bool JsonDatabase::setTrustedDevice(const std::string& username, const Json& device) {
    std::lock_guard<std::mutex> lock(mutex_);
    for (auto& u : usersJson_["users"].arrayValue) {
        if (u["username"].getString() == username) {
            u["trustedDevice"] = device;
            dirtyUsers_ = true;
            return true;
        }
    }
    return false;
}

long long JsonDatabase::addMessage(const Message& msg) {
    std::lock_guard<std::mutex> lock(mutex_);
    long long id = nextMsgId_++;
    Json obj;
    obj["id"] = id;
    obj["from"] = msg.from;
    obj["to"] = msg.to;
    obj["content"] = msg.content;
    obj["timestamp"] = msg.timestamp;
    obj["encrypted"] = msg.encrypted;
    obj["ephemeral_key"] = msg.ephemeralKey;
    obj["nonce"] = msg.nonce;
    obj["salt"] = msg.salt;
    messagesJson_["messages"].push_back(obj);
    dirtyMessages_ = true;
    return id;
}

std::vector<Message> JsonDatabase::getMessages(const std::string& user1, const std::string& user2, int limit, int offset) {
    std::lock_guard<std::mutex> lock(mutex_);
    std::vector<Message> res;
    for (const auto& m : messagesJson_["messages"].arrayValue) {
        std::string f = m["from"].getString();
        std::string t = m["to"].getString();
        if ((f == user1 && t == user2) || (f == user2 && t == user1)) {
            Message msg;
            msg.id = m["id"].getLongLong();
            msg.from = f;
            msg.to = t;
            msg.content = m["content"].getString();
            msg.timestamp = m["timestamp"].getLongLong();
            msg.encrypted = m.contains("encrypted") ? m["encrypted"].getBool() : false;
            msg.ephemeralKey = m.contains("ephemeral_key") ? m["ephemeral_key"].getString() : "";
            msg.nonce = m.contains("nonce") ? m["nonce"].getString() : "";
            msg.salt = m.contains("salt") ? m["salt"].getString() : "";
            res.push_back(msg);
        }
    }
    std::sort(res.begin(), res.end(), [](const Message& a, const Message& b) {
        return a.timestamp < b.timestamp;
    });
    if (offset > 0 && offset < static_cast<int>(res.size())) {
        res.erase(res.begin(), res.begin() + offset);
    } else if (offset >= static_cast<int>(res.size())) {
        res.clear();
    }
    if (limit > 0 && static_cast<int>(res.size()) > limit) {
        res.resize(limit);
    }
    return res;
}

std::vector<std::string> JsonDatabase::getAllUsers() {
    std::lock_guard<std::mutex> lock(mutex_);
    std::vector<std::string> res;
    for (const auto& u : usersJson_["users"].arrayValue) {
        res.push_back(u["username"].getString());
    }
    return res;
}
