#pragma once
#include "ICrypto.hpp"
#include <vector>
#include <cstdint>

class Sha256Hasher : public ICrypto {
public:
    std::string hash(const std::string& input) override;

private:
    void transform(uint32_t h[8], const uint8_t* data);
    std::string toHex(const std::vector<uint8_t>& bytes);
};
