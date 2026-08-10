#pragma once
#include <string>
#include <vector>
#include <map>
#include <sstream>
#include <stdexcept>
#include <cctype>
#include <iomanip>
#include <cmath>

enum class JsonType { Null, Bool, Number, String, Array, Object };
class Json {
    public:
    JsonType type = JsonType::Null;
    bool boolValue = false;
    double numberValue = 0.0;
    std::string stringValue;
    std::vector<Json> arrayValue;
    std::map<std::string, Json> objectValue;
    Json() = default;
    Json(std::nullptr_t) : type(JsonType::Null) {}
    Json(bool v) : type(JsonType::Bool), boolValue(v) {}
    Json(int v) : type(JsonType::Number), numberValue(v) {}
    Json(long long v) : type(JsonType::Number), numberValue(static_cast<double>(v)) {}
    Json(double v) : type(JsonType::Number), numberValue(v) {}
    Json(const std::string& v) : type(JsonType::String), stringValue(v) {}
    Json(const char* v) : type(JsonType::String), stringValue(v) {}
    Json(const std::vector<Json>& v) : type(JsonType::Array), arrayValue(v) {}
    Json(const std::map<std::string, Json>& v) : type(JsonType::Object), objectValue(v) {}
    Json(JsonType t) : type(t) {}
    Json(const Json& other) = default;
    Json(Json&& other) = default;
    // --- operator= для примитивов ---
    Json& operator=(const Json& other) = default;
    Json& operator=(Json&& other) = default;
    Json& operator=(std::nullptr_t) {
        type = JsonType::Null;
        boolValue = false; numberValue = 0.0; stringValue.clear();
        arrayValue.clear(); objectValue.clear();
        return *this;
    }
    Json& operator=(bool v) {
        type = JsonType::Bool; boolValue = v;
        numberValue = 0.0; stringValue.clear(); arrayValue.clear(); objectValue.clear();
        return *this;
    }
    Json& operator=(int v) { return operator=(static_cast<long long>(v)); }
    Json& operator=(long long v) {
        type = JsonType::Number; numberValue = static_cast<double>(v);
        boolValue = false; stringValue.clear(); arrayValue.clear(); objectValue.clear();
        return *this;
    }
    Json& operator=(double v) {
        type = JsonType::Number; numberValue = v;
        boolValue = false; stringValue.clear(); arrayValue.clear(); objectValue.clear();
        return *this;
    }
    Json& operator=(const std::string& v) {
        type = JsonType::String; stringValue = v;
        boolValue = false; numberValue = 0.0; arrayValue.clear(); objectValue.clear();
        return *this;
    }
    Json& operator=(const char* v) {
        type = JsonType::String; stringValue = v;
        boolValue = false; numberValue = 0.0; arrayValue.clear(); objectValue.clear();
        return *this;
    }
    static Json parse(const std::string& text) {
        Parser p(text);
        return p.parse();
    }
    std::string dump(int indent = -1) const {
        if(indent >= 0) return dumpImpl(0, indent);
        return dumpCompact();
    }
    bool isNull() const { return type == JsonType::Null; }
    bool isBool() const { return type == JsonType::Bool; }
    bool isNumber() const { return type == JsonType::Number; }
    bool isString() const { return type == JsonType::String; }
    bool isArray() const { return type == JsonType::Array; }
    bool isObject() const { return type == JsonType::Object; }
    bool getBool() const { return boolValue; }
    double getNumber() const { return numberValue; }
    int getInt() const { return static_cast<int>(numberValue); }
    long long getLongLong() const { return static_cast<long long>(numberValue); }
    const std::string& getString() const { return stringValue; }
    std::vector<Json>& getArray() { return arrayValue; }
    const std::map<std::string, Json>& getObject() const { return objectValue; }
    Json& operator[](const std::string& key) {
        type = JsonType::Object;
        return objectValue[key];
    }
    const Json& operator[](const std::string& key) const {
        static const Json nullJson;
        auto it = objectValue.find(key);
        if(it != objectValue.end()) return it->second;
        return nullJson;
    }
    Json& operator[](size_t idx) {
        if(type != JsonType::Array) type = JsonType::Array;
        if(idx >= arrayValue.size()) arrayValue.resize(idx + 1);
        return arrayValue[idx];
    }
    const Json& operator[](size_t idx) const {
        static const Json nullJson;
        if(type != JsonType::Array || idx >= arrayValue.size()) return nullJson;
        return arrayValue[idx];
    }
    bool contains(const std::string& key) const {
        return type == JsonType::Object && objectValue.count(key);
    }
    void push_back(const Json& val) {
        if(type != JsonType::Array) type = JsonType::Array;
        arrayValue.push_back(val);
    }
    size_t size() const {
        if(type == JsonType::Array) return arrayValue.size();
        if(type == JsonType::Object) return objectValue.size();
        return 0;
    }
    private:
    struct Parser {
        const std::string& s;
        size_t pos = 0;
        Parser(const std::string& str) : s(str) {}
        void skip() {
            while(pos < s.size() && (s[pos] == ' ' || s[pos] == '\t' || s[pos] == '\n' || s[pos] == '\r')) pos++;
        }
        Json parseString() {
            pos++;
            std::string result;
            while(pos < s.size() && s[pos] != '"') {
                if(s[pos] == '\\') {
                    pos++;
                    if(pos >= s.size()) throw std::runtime_error("Invalid escape");
                    switch (s[pos]) {
                        case '"': result += '"'; break;
                        case '\\': result += '\\'; break;
                        case '/': result += '/'; break;
                        case 'b': result += '\b'; break;
                        case 'f': result += '\f'; break;
                        case 'n': result += '\n'; break;
                        case 'r': result += '\r'; break;
                        case 't': result += '\t'; break;
                        default: result += s[pos]; break;
                    }
                } else {
                    result += s[pos];
                }
                pos++;
            }
            if(pos >= s.size()) throw std::runtime_error("Unterminated string");
            pos++;
            return Json(result);
        }
        Json parseObject() {
            Json obj(JsonType::Object);
            pos++;
            while(true) {
                skip();
                if(pos < s.size() && s[pos] == '}') { ++pos; break; }
                if(s[pos] != '"') throw std::runtime_error("Expected string key");
                std::string key = parseString().stringValue;
                skip();
                if(pos >= s.size() || s[pos] != ':') throw std::runtime_error("Expected: ");
                pos++;
                Json val = parse();
                obj.objectValue[key] = val;
                skip();
                if(pos < s.size() && s[pos] == ',') { pos++; continue; }
                if(pos < s.size() && s[pos] == '}') { pos++; break; }
                throw std::runtime_error("Expected , or }");
            }
            return obj;
        }
        Json parseArray() {
            Json arr(JsonType::Array);
            pos++;
            while(true) {
                skip();
                if(pos < s.size() && s[pos] == ']') { pos++; break; }
                arr.arrayValue.push_back(parse());
                skip();
                if(pos < s.size() && s[pos] == ',') { pos++; continue; }
                if(pos < s.size() && s[pos] == ']') { pos++; break; }
                throw std::runtime_error("Expected , or ]");
            }
            return arr;
        }
        Json parseBool() {
            if(s.substr(pos, 4) == "true") { pos += 4; return Json(true); }
            if(s.substr(pos, 5) == "false") { pos += 5; return Json(false); }
            throw std::runtime_error("Invalid bool");
        }
        Json parseNull() {
            if(s.substr(pos, 4) == "null") { pos += 4; return Json(); }
            throw std::runtime_error("Invalid null");
        }
        Json parseNumber() {
            size_t start = pos;
            if(s[pos] == '-') pos++;
            while(pos < s.size() && std::isdigit(s[pos])) pos++;
            if(pos < s.size() && s[pos] == '.') {
                pos++;
                while(pos < s.size() && std::isdigit(s[pos])) pos++;
            }
            if(pos < s.size() && (s[pos] == 'e' || s[pos] == 'E')) {
                pos++;
                if(pos < s.size() && (s[pos] == '+' || s[pos] == '-')) pos++;
                while(pos < s.size() && std::isdigit(s[pos])) pos++;
            }
            double val = std::stod(s.substr(start, pos - start));
            return Json(val);
        }
        Json parse() {
            skip();
            if(pos >= s.size()) throw std::runtime_error("Empty JSON");
            char c = s[pos];
            if(c == '{') return parseObject();
            if(c == '[') return parseArray();
            if(c == '"') return parseString();
            if(c == 't' || c == 'f') return parseBool();
            if(c == 'n') return parseNull();
            return parseNumber();
        }
    };
    std::string dumpCompact() const {
        switch(type) {
            case JsonType::Null: return "null";
            case JsonType::Bool: return boolValue ? "true" : "false";
            case JsonType::Number: {
                std::ostringstream oss;
                if(numberValue == std::floor(numberValue)) {
                    oss << static_cast<long long>(numberValue);
                } else {
                    oss << numberValue;
                }
                return oss.str();
            }
            case JsonType::String: return "\"" + escape(stringValue) + "\"";
            case JsonType::Array: {
                std::string res = "[";
                for(size_t i = 0; i < arrayValue.size(); i++) {
                    if(i) res += ",";
                    res += arrayValue[i].dumpCompact();
                }
                return res + "]";
            }
            case JsonType::Object: {
                std::string res = "{";
                bool first = true;
                for(const auto& [k, v] : objectValue) {
                    if(!first) res += ",";
                    first = false;
                    res += "\"" + escape(k) + "\":" + v.dumpCompact();
                }
                return res + "}";
            }
        }
        return "null";
    }
    std::string dumpImpl(int depth, int indent) const {
        std::string prefix(depth * indent, ' ');
        switch(type) {
            case JsonType::Null: return "null";
            case JsonType::Bool: return boolValue ? "true" : "false";
            case JsonType::Number: {
                std::ostringstream oss;
                if (numberValue == std::floor(numberValue)) {
                    oss << static_cast<long long>(numberValue);
                } else {
                    oss << numberValue;
                }
                return oss.str();
            }
            case JsonType::String: return "\"" + escape(stringValue) + "\"";
            case JsonType::Array: {
                if (arrayValue.empty()) return "[]";
                std::string res = "[\n";
                for (size_t i = 0; i < arrayValue.size(); ++i) {
                    res += prefix + std::string(indent, ' ') + arrayValue[i].dumpImpl(depth + 1, indent);
                    if (i + 1 < arrayValue.size()) res += ",";
                    res += "\n";
                }
                return res + prefix + "]";
            }
            case JsonType::Object: {
                if (objectValue.empty()) return "{}";
                std::string res = "{\n";
                bool first = true;
                for (const auto& [k, v] : objectValue) {
                    if (!first) res += ",\n";
                    first = false;
                    res += prefix + std::string(indent, ' ') + "\"" + escape(k) + "\": " + v.dumpImpl(depth + 1, indent);
                }
                return res + "\n" + prefix + "}";
            }
        }
        return "null";
    }
    static std::string escape(const std::string& s) {
        std::string r;
        for(char c : s) {
            switch(c) {
                case '"': r += "\\\""; break;
                case '\\': r += "\\\\"; break;
                case '\b': r += "\\b"; break;
                case '\f': r += "\\f"; break;
                case '\n': r += "\\n"; break;
                case '\r': r += "\\r"; break;
                case '\t': r += "\\t"; break;
                default: r += c; break;
            }
        }
        return r;
    }
};
