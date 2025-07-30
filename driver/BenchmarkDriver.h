#include <chrono>
#include <string>
#include <vector>

#include "spdlog/spdlog.h"

#include "TuringClient.h"

namespace bm {

class BenchmarkDriver {
public:
    struct BenchmarkResult {};

    BenchmarkDriver(const std::string& graph, turingClient::TuringClient& cl)
        : _graphName(graph),
        _cl(cl)
    {
    }


    void setup(std::vector<std::string>& queries, const std::string& filepath);

    void setup(std::vector<std::string>& buildQueries, std::vector<std::string>& queries,
               const std::string& buildFile, const std::string& queryFile);
    
    template <bool totalTime, bool perQuery, bool debug>
    void run(std::vector<std::string>& queries);


private:
    std::string _graphName;
    const turingClient::TuringClient& _cl;
    std::vector<std::string> _queryFiles;

    void parseQueries(std::vector<std::string>& queries,
                      const std::string& filepath);

    bool query(std::string_view q);
};

template <bool totalTime, bool perQuery, bool debug>
void BenchmarkDriver::run(std::vector<std::string>& queries) {
    using namespace std::chrono;
    using Clock = high_resolution_clock;
    using Timestamp = time_point<high_resolution_clock>;

    Timestamp pre;
    Timestamp post;
    std::vector<milliseconds> queryTimes(queries.size());

    if constexpr (totalTime) {
        pre = Clock::now();
    }

    for (size_t i {0}; const auto& q : queries) {
        spdlog::info(i);
        spdlog::info(q);
        bool res = query(q);
        if constexpr (perQuery) {
            // queryTimes[i] = res.getTotalTime();
        }
        if constexpr (debug) {
            if (!res) {
                spdlog::error("Query failed to execute : {}", q);
            }
        } 
    }

    if constexpr (totalTime) {
        post = Clock::now();
        auto duration = duration_cast<milliseconds>(post - pre);
        spdlog::info("Total time: {} ms", duration.count());
    }

    if constexpr (perQuery) {
        for (size_t i {0}; i < queries.size(); i++) {
            spdlog::info("{} : {}", queries[i], queryTimes[i].count());
        }
    }
}
}
