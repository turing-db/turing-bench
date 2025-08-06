#include <cstdint>
#include <cstdlib>
#include <ranges>
#include <spdlog/spdlog.h>
#include <argparse.hpp>

#include "TuringClient.h"
#include "driver/BenchmarkDriver.h"

using namespace bm;

constexpr bool TOTALTIME {true};
constexpr bool PERQUERY {true};
[[maybe_unused]] constexpr bool DEBUG {true};

int main (int argc, char** argv) {
    using namespace turingClient;

    argparse::ArgumentParser ap("TuringDB Benchmark");
        std::string graph{}; 
        std::string buildFile{}; 
        std::string queryFile{};
        [[maybe_unused]] bool totalTime {true};
        [[maybe_unused]] bool perQuery {false};
        [[maybe_unused]] bool debug {false};
        uint16_t numRuns {1};

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
            .nargs(0)
            .store_into(debug)
            .default_value(false)
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
    
    TuringClient client("http://127.0.0.1:6666");
    BenchmarkDriver dr("default", client, numRuns);
    bool setupResult = dr.setup(buildFile, queryFile);

    if (!setupResult) {
        spdlog::error("Setup failed.");
        return EXIT_FAILURE;
    }

    if (totalTime) {
        for (size_t i = 1; i <= numRuns; ++i) {
            spdlog::info("Performing total time run {}/{}.", i, numRuns);
            dr.run<TOTALTIME, false, false>();
        }
        spdlog::info("Finished runs for total time.");
        dr.reset();
    }

    if (perQuery) {
        for ([[maybe_unused]] size_t i = 1; i <= numRuns; ++i) {
            spdlog::info("Performing per query run {}/{}.", i, numRuns);
            dr.run<false, PERQUERY, false>();
        }
        spdlog::info("Finished per query runs.");
        dr.reset();
    }

    auto results = dr.getResults();
    for (size_t i{0}; const auto& time : results.totalTimes) {
        spdlog::info("Run {} took {} us", ++i, time.count());
    }

    for (size_t i {0}; const auto& runInfo : results.queryTimes) {
        for (const auto& [query, times] : runInfo) {
            auto avg = std::reduce(times.begin(), times.end()) / times.size();
            spdlog::info("Run {} average time for query : {}", ++i, query);
            spdlog::info("{} us", avg.count());
        }
    }
}
