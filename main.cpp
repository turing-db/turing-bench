#include <spdlog/spdlog.h>
#include <argparse.hpp>

#include "TuringClient.h"
#include "driver/BenchmarkDriver.h"

const std::string GRAPH_NAME = "benchmarkdb";

using namespace bm;

int main (int argc, char** argv) {
    using namespace turingClient;

    argparse::ArgumentParser ap("TuringDB Benchmark");
        std::string graph{};
        std::string buildFile{};
        std::string queryFile{};

        ap.add_argument("-b", "--build")
            .nargs(1)
            .store_into(buildFile)
            .required()
            .help("CYPHER file containing create queries to build a DB from");

        ap.add_argument("-q","--query")
            .nargs(1)
            .store_into(queryFile)
            .required()
            .help("The query file to run against the loaded DB.");

        try {
            ap.parse_args(argc, argv);
        } catch (const std::exception& err) {
            std::cerr << err.what() << std::endl;
            std::cerr << ap;
            return 1;
        }
    
    using Col = std::vector<std::unique_ptr<TypedColumn>>;
    
    TuringClient client("http://127.0.0.1:6666");

    Col ret{};

    auto query = [&client, &ret](std::string q) {
        bool res = client.query(q, GRAPH_NAME, ret);
        if (!res) {
            spdlog::error("Failed to query : {}", q);
        } else {
            spdlog::info("Successful query");
        }
    };

    BenchmarkDriver dr(GRAPH_NAME, client);

    query("match (n) return n");

    query("CHANGE NEW");
    
    query("create (n:NewNode{name=\"cyrus\"})");
}
