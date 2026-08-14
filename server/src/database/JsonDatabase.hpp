#pragma once
#include <vector>
#include <optional>
#include "database/IDatabase.hpp"
#include "utils/Json.hpp"
#include <mutex>
#include <string>
#include <atomic>
#include <thread>

class JsonDatabase : public IDatabase {
public:
    JsonDatabase(const std::string& usersFile, const std::string& messagesFile);
    ~JsonDatabase();
    JsonDatabase(const JsonDatabase&) = delete;
    JsonDatabase& operator=(const JsonDatabase&) = delete;
    bool init() override;
    bool addUser(const User& user) override;
    std::optional<User> getUser(const std::string& username) override;
    bool updateUserPublicKey(const std::string& username, const std::string& publicKey) override;
    std::optional<std::string> getUserPublicKey(const std::string& username) override;
    long long addMessage(const Message& msg) override;
    std::vector<Message> getMessages(const std::string& user1, const std::string& user2, int limit = 0, int offset = 0) override;
    std::vector<std::string> getAllUsers() override;

private:
    void loadUsers();
    void saveUsers();
    void loadMessages();
    void saveMessages();
    void flush();

    std::string usersFile_;
    std::string messagesFile_;
    Json usersJson_;
    Json messagesJson_;
    long long nextMsgId_ = 1;
    std::mutex mutex_;

    std::atomic<bool> dirtyUsers_{false};
    std::atomic<bool> dirtyMessages_{false};
    std::atomic<bool> stopFlush_{false};
    std::thread flushThread_;
};
