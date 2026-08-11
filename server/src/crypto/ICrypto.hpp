#pragma once
#include <string>

class ICrypto {
public:
    virtual ~ICrypto() = default;
    virtual std::string hash(const std::string& input) = 0;
};
