#include "Sha256Hasher.hpp"
#include <sstream>
#include <iomanip>
#include <cstring>

#define ROTRIGHT(a,b) (((a) >> (b)) | ((a) << (32-(b))))
#define CH(x,y,z) (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x,y,z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define EP0(x) (ROTRIGHT(x,2) ^ ROTRIGHT(x,13) ^ ROTRIGHT(x,22))
#define EP1(x) (ROTRIGHT(x,6) ^ ROTRIGHT(x,11) ^ ROTRIGHT(x,25))
#define SIG0(x) (ROTRIGHT(x,7) ^ ROTRIGHT(x,18) ^ ((x) >> 3))
#define SIG1(x) (ROTRIGHT(x,17) ^ ROTRIGHT(x,19) ^ ((x) >> 10))

static const uint32_t k[64] = {
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
};
std::string Sha256Hasher::hash(const std::string& input) {
    h[0] = 0x6a09e667; h[1] = 0xbb67ae85; h[2] = 0x3c6ef372; h[3] = 0xa54ff53a;
    h[4] = 0x510e527f; h[5] = 0x9b05688c; h[6] = 0x1f83d9ab; h[7] = 0x5be0cd19;
    bitLen = 0;
    std::vector<uint8_t> data(input.begin(), input.end());
    bitLen += data.size() * 8;
    data.push_back(0x80);
    while((data.size() % 64) != 56) data.push_back(0x00);
    uint64_t bitLenBE = bitLen;
    for(int i = 7; i >= 0; i--) data.push_back((bitLenBE >> (i * 8)) & 0xFF);
    for(size_t i = 0; i < data.size(); i += 64) {
        transform(&data[i]);
    }
    std::vector<uint8_t> hash(32);
    for(int i = 0; i < 8; i++) {
        hash[i*4] = (h[i] >> 24) & 0xFF;
        hash[i*4+1] = (h[i] >> 16) & 0xFF;
        hash[i*4+2] = (h[i] >> 8) & 0xFF;
        hash[i*4+3] = h[i] & 0xFF;
    }
    return toHex(hash);
}
void Sha256Hasher::transform(const uint8_t* data) {
    uint32_t m[64];
    uint32_t w[8];
    for (int i = 0; i < 16; ++i) {
        m[i] = (data[i*4] << 24) | (data[i*4+1] << 16) | (data[i*4+2] << 8) | (data[i*4+3]);
    }
    for (int i = 16; i < 64; ++i) {
        m[i] = SIG1(m[i-2]) + m[i-7] + SIG0(m[i-15]) + m[i-16];
    }
    for (int i = 0; i < 8; ++i) w[i] = h[i];
    for (int i = 0; i < 64; ++i) {
        uint32_t t1 = w[7] + EP1(w[4]) + CH(w[4], w[5], w[6]) + k[i] + m[i];
        uint32_t t2 = EP0(w[0]) + MAJ(w[0], w[1], w[2]);
        w[7] = w[6];
        w[6] = w[5];
        w[5] = w[4];
        w[4] = w[3] + t1;
        w[3] = w[2];
        w[2] = w[1];
        w[1] = w[0];
        w[0] = t1 + t2;
    }
    for (int i = 0; i < 8; ++i) h[i] += w[i];
}
std::string Sha256Hasher::toHex(const std::vector<uint8_t>& bytes) {
    std::ostringstream oss;
    for (auto b : bytes) oss << std::hex << std::setw(2) << std::setfill('0') << (int)b;
    return oss.str();
}