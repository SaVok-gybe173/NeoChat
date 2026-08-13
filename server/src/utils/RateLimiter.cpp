#include "RateLimiter.hpp"

bool RateLimiter::isAllowed(const std::string& key) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = entries_.find(key);
    if(it == entries_.end()) return true;
    if(it->second.banned) {
        auto now = std::chrono::steady_clock::now();
        if(now >= it->second.banUntil) {
            it->second.banned = false;
            it->second.failedAttempts = 0;
            return true;
        }
        return false;
    }
    return true;
}
void RateLimiter::recordFailure(const std::string& key) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto& entry = entries_[key];
    entry.failedAttempts++;
    if(entry.failedAttempts >= MAX_ATTEMPTS) {
        entry.banned = true;
        entry.banUntil = std::chrono::steady_clock::now() + std::chrono::minutes(BAN_MINUTES);
    }
}
void RateLimiter::recordSuccess(const std::string& key) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = entries_.find(key);
    if(it != entries_.end()) {
        it->second.failedAttempts = 0;
        it->second.banned =false;
    }
}
void RateLimiter::cleanup() {
    std::lock_guard<std::mutex> lock(mutex_);
    auto now = std::chrono::steady_clock::now();
    for(auto it = entries_.begin(); it != entries_.end(); ) {
        if(!it->second.banned && it->second.failedAttempts == 0) {
            it = entries_.erase(it);
        } else if(it->second.banned && now >= it->second.banUntil) {
            it = entries_.erase(it);
        } else {
            it++;
        }
    }
}