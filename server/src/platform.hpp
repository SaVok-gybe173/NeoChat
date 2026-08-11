#pragma once
#ifdef _WIN32
    #ifndef WIN32_LEAN_AND_MEAN
        #define WIN32_LEAN_AND_MEAN
    #endif
    #include <winsock2.h>
    #include <ws2tcpip.h>

    #define CLOSE_SOCKET(s)     closesocket(s)
    #define ERRNO               WSAGetLastError()
    #define ERR_EINTR           WSAEINTR
    #define MSG_NOSIGNAL        0
    #define SHUT_RDWR           SD_BOTH

    #ifndef _SSIZE_T_DEFINED
    #define _SSIZE_T_DEFINED
    typedef int ssize_t;
    #endif
    typedef SOCKET PlatformSocket;
    typedef int socklen_t;

    #define SETSOCKOPT_PTR(ptr) (reinterpret_cast<const char*>(ptr))

    inline bool init_winsock() {
        WSADATA wsaData;
        return WSAStartup(MAKEWORD(2, 2), &wsaData) == 0;
    }
    inline void cleanup_winsock() { WSACleanup(); }
#else
    #include <unistd.h>
    #include <sys/socket.h>
    #include <arpa/inet.h>
    #include <netinet/in.h>
    #include <errno.h>

    #define CLOSE_SOCKET(s)     close(s)
    #define ERRNO               errno
    #define ERR_EINTR           EINTR
    #define SETSOCKOPT_PTR(ptr) (ptr)
    typedef int PlatformSocket;

    inline bool init_winsock() { return true; }
    inline void cleanup_winsock() {}
#endif
