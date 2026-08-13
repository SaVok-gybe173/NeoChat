#pragma once
#include <string>
#include <mutex>
#include <fstream>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <iostream>

enum class LogLevel { Debug, Info, Warning, Error };

class Logger {
    public:
    static Logger& instance();
    bool init(const std::string& filename);
    void log(LogLevel level, const std::string& message);
    void debug(const std::string& msg) { log(LogLevel::Debug, msg); }
    void info(const std::string& msg) { log(LogLevel::Info, msg); }
    void warn(const std::string& msg) { log(LogLevel::Warning, msg); }
    void error(const std::string& msg) { log(LogLevel::Error, msg); }

    private:
    Logger() = default;
    ~Logger();
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;

    std::string levelToString(LogLevel level);
    std::string currentTimestamp();

    std::ofstream file_;
    std::mutex mutex_;
    bool initialized_ = false;
};