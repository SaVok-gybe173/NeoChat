#pragma once
#include <string>
#include <map>

class Config {
    public:
    bool load(const std::string& filename);
    std::string getString(const std::string& section, const std::string& key, const std::string& defaultVal = "") const;
    int getInt(const std::string& section, const std::string& key, int defaultVal = 0) const;
    private:
    std::map<std::string, std::map<std::string, std::string>> data_;
};
