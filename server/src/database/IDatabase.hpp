#pragma once
#include <string>
#include <vector>
#include <optional>

struct User {
    std::string username;
    std::string passwordHash;
    std::string salt;
    std::string publicKey;
};

struct Message {
    long long id;
    std::string from;
    std::string to;
    std::string content;
    long long timestamp;
    bool encrypted = false;
    std::string ephemeralKey;
    std::string nonce;
    std::string salt;
};

class IDatabase {
public:
    virtual ~IDatabase() = default;
    virtual bool init() = 0;

    virtual bool addUser(const User& user) = 0;
    virtual std::optional<User> getUser(const std::string& username) = 0;
    virtual bool updateUserPublicKey(const std::string& username, const std::string& publicKey) = 0;
    virtual std::optional<std::string> getUserPublicKey(const std::string& username) = 0;

    virtual long long addMessage(const Message& msg) = 0;
    virtual std::vector<Message> getMessages(const std::string& user1, const std::string& user2, int limit = 0, int offset = 0) = 0;
    virtual std::vector<std::string> getAllUsers() = 0;
};
