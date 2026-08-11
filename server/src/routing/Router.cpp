#include "routing/Router.hpp"
#include "routing/Handlers.hpp"
#include "network/Session.hpp"

Router::Router(Handlers* handlers) : handlers_(handlers) {}
Json Router::route(const Json& request, std::shared_ptr<Session> session) {
    Json res;
    if(!request.contains("action")) {
        res["status"] = "error";
        res["message"] = "Missing action";
        if (request.contains("req_id")) res["req_id"] = request["req_id"].getString();
        return res;
    }
    std::string action = request["action"].getString();
    if(action == "register") res = handlers_->handleRegister(request);
    else if(action == "login") res = handlers_->handleLogin(request, session);
    else if(action == "send_message") res = handlers_->handleSendMessage(request);
    else if(action == "get_messages") res = handlers_->handleGetMessages(request);
    else if(action == "get_users") res = handlers_->handleGetUsers(request);
    else if(action == "logout") res = handlers_->handleLogout(request, session);
    else if(action == "upload_key") res = handlers_->handleUploadKey(request);
    else if(action == "get_key") res = handlers_->handleGetKey(request);
    else {
        res["status"] = "error";
        res["message"] = "Unknown action: " + action;
    }
    if(request.contains("req_id")) {
        res["req_id"] = request["req_id"].getString();
    }
    return res;
}
void Router::onUserDisconnected(const std::string& username) {
    if (handlers_) handlers_->userDisconnected(username);
}