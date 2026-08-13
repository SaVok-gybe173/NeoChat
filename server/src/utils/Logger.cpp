#include "Logger.hpp"
#include "platform.hpp"

Logger& Logger::instance() {
    static Logger logger;
    return logger;
}
Logger::~Logger() {
    if(file_.is_open()) file_.close();
}
bool Logger::init(const std::string& filename) {
    std::lock_guard<std::mutex> lock(mutex_);
    file_.open(filename, std::ios::app);
    initialized_ = file_.is_open();
    return initialized_;
}
std::string Logger::levelToString(LogLevel level) {
    switch(level) {
        case LogLevel::Debug: return "DEBUG";
        case LogLevel::Info: return "INFO";
        case LogLevel::Warning: return "WARNING";
        case LogLevel::Error: return "ERROR";
    }
    return "UNKNOWN";
}
std::string Logger::currentTimestamp() {
    auto now = std::chrono::system_clock::now();
    auto time_t_now = std::chrono::system_clock::to_time_t(now);
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;

    std::tm tm_buf;
    thread_safe_localtime(&time_t_now, &tm_buf);

    std::stringstream ss;
    ss << std::put_time(&tm_buf, "%Y-%m-%d %H:%M:%S");
    ss << '.' << std::setfill('0') << std::setw(3) << ms.count();
    return ss.str();
}
void Logger::log(LogLevel level, const std::string& message) {
    std::lock_guard<std::mutex> lock(mutex_);
    std::string line = "[" + currentTimestamp() + "] [" + levelToString(level) + "]" + message;
    if(initialized_ && file_.is_open()) {
        file_ << line << '\n';
    }
    if(level == LogLevel::Error) {
        std::cerr << line << std::endl;
    } else {
        std::cout << line << std::endl;
    }
}