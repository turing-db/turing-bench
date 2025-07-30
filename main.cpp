#include <spdlog/spdlog.h>

#include "TuringClient.h"

int main () {
    using namespace turingClient;
    using Col = std::vector<std::unique_ptr<TypedColumn>>;
    
    TuringClient client("http://127.0.0.1:6666");

    Col ret{};

    auto query = [&client, &ret](std::string q) {
        bool res = client.query(q, "simpledb", ret);
        if (!res) {
            spdlog::error("Failed to query : {}", q);
        } else {
            spdlog::info("Successful query");
        }
    };

    query("match (n) return n");

    query("CHANGE NEW");
    
    query("create (n:NewNode{name=\"cyrus\"})");
}
