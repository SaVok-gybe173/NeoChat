#include "config/Config.hpp"
#include "crypto/Sha256Hasher.hpp"
#include "database/JsonDatabase.hpp"
#include "routing/Handlers.hpp"
#include "routing/Router.hpp"
#include "network/Server.hpp"
#include "platform.hpp"
#include "utils/Logger.hpp"
#include <iostream>
#include <filesystem>
#include <csignal>

static Server* g_server = nullptr;

void signalHandler(int) {
    if (g_server) {
        g_server->stop();
    }
}

int main(int argc, char* argv[]) {
    if (!Logger::instance().init("server.log")) {
        std::cerr << "Warning: File logger failed, logging to console only\n";
    }
    Logger::instance().info("Server starting...");

    if (!init_winsock()) {
        Logger::instance().error("WSAStartup failed");
        return 1;
    }

    std::string configFile = (argc > 1) ? argv[1] : "config.ini";

    Config config;
    if (!config.load(configFile)) {
        Logger::instance().error("Failed to load config: " + configFile);
        cleanup_winsock();
        return 1;
    }

    std::string host = config.getString("server", "host", "0.0.0.0");
    int port = config.getInt("server", "port", 8080);

    std::string usersFile = config.getString("database", "users_file", "data/users.json");
    std::string messagesFile = config.getString("database", "messages_file", "data/messages.json");

    std::filesystem::path upath(usersFile);
    std::filesystem::create_directories(upath.parent_path());
    std::filesystem::path mpath(messagesFile);
    std::filesystem::create_directories(mpath.parent_path());

    Sha256Hasher hasher;
    JsonDatabase db(usersFile, messagesFile);
    if (!db.init()) {
        Logger::instance().error("Failed to init database");
        cleanup_winsock();
        return 1;
    }

    Handlers handlers(&db, &hasher);
    Router router(&handlers);
    Server server(host, port, &router);
    g_server = &server;

    std::signal(SIGINT, signalHandler);
    std::signal(SIGTERM, signalHandler);

    if (!server.start()) {
        Logger::instance().error("Failed to start server");
        cleanup_winsock();
        return 1;
    }

    server.run();
    Logger::instance().info("Server stopped");
    g_server = nullptr;
    cleanup_winsock();
    return 0;
}
