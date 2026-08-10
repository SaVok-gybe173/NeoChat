#include "Config.hpp"
#include <fstream>
#include <sstream>
#include <algorithm>

bool Config::load(const std::string& filename) {
    std::ifstream file(filename);
    if(!file.is_open()) return false;
    std::string line;
    std::string currentSection;
    while(std::getline(file, line)) {
        size_t start = line.find_first_not_of(" \t\r\n");
        if(start == std::string::npos) continue;
        size_t end = line.find_last_not_of(" \t\r\n");
        line = line.substr(start, end - start + 1);
        if(line.empty() || line[0] == ';' || line[0] == '#') continue;
        if(line.front() == '[' && line.back() == ']') {
            currentSection = line.substr(1, line.size() - 2);
            continue;
        }
        size_t eq = line.find('=');
        if(eq == std::string::npos) continue;
        std::string key = line.substr(0, eq);
        std::string val = line.substr(eq + 1);
        key.erase(0, key.find_first_not_of(" \t"));
        key.erase(key.find_last_not_of(" \t") + 1);
        val.erase(0, val.find_first_not_of(" \t"));
        val.erase(val.find_last_not_of(" \t") + 1);
        data_[currentSection][key] = val;
    }
    return true;
}
std::string Config::getString(const std::string& section, const std::string& key, const std::string& defaultVal) const {
    auto sit = data_.find(section);
    if(sit == data_.end()) return defaultVal;
    auto kit = sit->second.find(key);
    if(kit == sit->second.end()) return defaultVal;
    return kit->second;
}
int Config::getInt(const std::string& section, const std::string& key, int defaultVal) const {
    std::string s = getString(section, key);
    if(s.empty()) return defaultVal;
    return std::stoi(s);
}