#include <stdexcept>

#include "TuringClient.h"

int main () {
    using namespace turingClient;
    using Col = std::vector<std::unique_ptr<TypedColumn>>;
    
    TuringClient client("http://127.0.0.1:6666");

    Col ret{};
    bool res = client.query("match (n) return n", "simpledb", ret);

    if (!res) {
        throw std::runtime_error("Failed to query");
    }
}
