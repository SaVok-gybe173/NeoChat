#pragma once
#include "database/IDatabase.hpp"
#include "utils/Json.hpp"
#include <mutex>
#include <string>

class JsonDatabase : public IDatabase {
    public:
    JsonDatabase(const std::string& userFile, const std::string& messagesFile);
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

    std::string usersFile_;
    std::string messagesFile_;
    Json usersJson_;
    Json messagesJson_;
    long long nextMsgId_ = 1;
    std::mutex mutex_;
};