#pragma once
#include <string>
#include <unordered_map>
#include <mutex>
#include <chrono>

class RateLimiter {
    public:
    bool isAllowed(const std::string& key);
    void recordFailure(const std::string& key); // Для брутфорса
    void recordSuccess(const std::string& key); // Для брутфорса
    void cleanup();
    private:
    struct Entry {
        // Брутфорс
        int failedAttempts = 0;
        std::chrono::steady_clock::time_point banUntil;
        bool banned = false;
    };
    std::unordered_map<std::string, Entry> entries_;
    std::mutex mutex_;
    static constexpr int MAX_ATTEMPTS = 5;
    static constexpr int BAN_MINUTES = 5;
};