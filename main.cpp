#include <ctime>
#include <cstdint>
#include <cstdlib>
#include <spdlog/spdlog.h>
#include <argparse.hpp>


#include "TuringClient.h"
#include "driver/BenchmarkDriver.h"

using namespace bm;

namespace {
    std::string generateTempGraphName() {
        return "graph" + std::to_string(time(nullptr));
    }
}

int main (int argc, char** argv) {
    using namespace turingClient;

    argparse::ArgumentParser ap("TuringDB Benchmark");
    std::string buildFile{}; 
    std::string graphToLoad{}; 

    std::string queryFile{};

    [[maybe_unused]] bool totalTime {true};
    [[maybe_unused]] bool perQuery {false};
    [[maybe_unused]] bool debug {false};

    uint16_t numRuns {1};

    std::string url {"http://127.0.0.1:6666"};

    ap.add_argument("-u", "--url")
            .nargs(1)
            .store_into(url)
            .default_value("http://127.0.0.1:6666")
            .help("URL and port of TuringDB server to connect to.");

    auto& graphLoadGroup = ap.add_mutually_exclusive_group(true);

    graphLoadGroup.add_argument("-b", "--build")
        .nargs(1)
        .store_into(buildFile)
        .help("CYPHER file containing create queries to build a DB from.");

    graphLoadGroup.add_argument("-l", "--load")
        .nargs(1)
        .store_into(graphToLoad)
        .help("The existing graph to load into the TuringDB server.");

    ap.add_argument("-q", "--query")
        .nargs(1)
        .store_into(queryFile)
        .required()
        .help("The query file to run against the loaded DB.");

    ap.add_argument("-t", "--total-time")
        .nargs(0)
        .store_into(totalTime)
        .default_value(true)
        .help("Perform benchmark runs where only the total time to execute all "
              "queries is measured.");

    ap.add_argument("-p", "--per-query")
        .nargs(0)
        .store_into(perQuery)
        .default_value(false)
        .help("Perform benchmark runs where the time to execute each query is "
              "measured.");

    ap.add_argument("-d", "--debug")
        .store_into(debug)
        .default_value(false)
        .implicit_value(true)
        .help("Enable debug mode: logs errors of queries. SHOULD NOT BE USED FOR "
              "COLLECTING MEANINGFUL DATA.");

    ap.add_argument("-r", "--runs")
        .nargs(1)
        .store_into(numRuns)
        .default_value(1)
        .help("The number of runs per benchmark.");

    try {
        ap.parse_args(argc, argv);
    } catch (const std::exception& err) {
        std::cerr << err.what() << std::endl;
        std::cerr << ap;
        return 1;
    }

    if (!totalTime && !perQuery) {
        spdlog::error("No mode selected. Please use --per-query or --total-time.");
        return EXIT_FAILURE;
    }

    TuringClient client(url);

    // If building a graph from CYPHER, create a temporary name for the graph
    // Otherwise, use the provided graph name to load it
    const std::string graphName =
        graphToLoad.empty() ? generateTempGraphName() : graphToLoad;
    BenchmarkDriver dr(graphName, client, numRuns);

    // Load/build any databases, parse queries
    bool setupResult = dr.setup(buildFile, queryFile);
    if (!setupResult) {
        spdlog::error("Setup failed.");
        return EXIT_FAILURE;
    }

    if (debug) {
        spdlog::warn("Using debug mode: results may be inaccurate.");
    }

    if (totalTime) {
        spdlog::error("TotalTime mode currently not supported");
        return EXIT_FAILURE;
    }

    bool result = false;
    if (perQuery) {
        if (!debug) {
            result = dr.runQueryBenchmark<false>();
        } else {
            result = dr.runQueryBenchmark<true>();
        }
    }

    if (result) {
        dr.present();
    }
    else {
        spdlog::error("Failed to run benchmarks");
    }

    return EXIT_SUCCESS;
}
