#include <chrono>
#include <cstdint>
#include <map>
#include <string>
#include <vector>

#include "spdlog/spdlog.h"

#include "TuringClient.h"

namespace bm {

class BenchmarkDriver {
public:
    using TimeUnit = std::chrono::microseconds;

    struct BenchmarkResult {
        std::vector<TimeUnit> totalTimes;
        std::vector<std::map<std::string, std::vector<TimeUnit>>> queryTimes;
    };

    BenchmarkDriver(const std::string& graph, turingClient::TuringClient& cl,
                    uint32_t runs)
        : _graphName(graph),
          _cl(cl),
          _runs(runs)
    {
        _res.totalTimes.reserve(_runs);
        _res.queryTimes.resize(_runs);
    }

    bool setup(const std::string& buildFile, const std::string& queryFile);

    bool buildGraph(const std::string& buildFile);

    template <bool totalTime, bool perQuery, bool debug>
    void run();

    BenchmarkResult getResults() { return _res; }

    void reset() { _currentRun = 0; }

private:
    std::string _graphName;
    turingClient::TuringClient& _cl;
    BenchmarkResult _res;
    uint32_t _runs {1};
    uint32_t _currentRun {0};

    std::vector<std::string> _queries;

    size_t _changeNo {0};

    void parseQueries(std::vector<std::string>& queries,
                      const std::string& filepath);

    bool query(const std::string& q, const std::string& change = "");
};

template <bool totalTime, bool perQuery, bool debug>
void BenchmarkDriver::run() {
    using namespace std::chrono;
    using Clock = high_resolution_clock;
    using Timestamp = time_point<high_resolution_clock>;

    Timestamp totalTimer;
    Timestamp queryTimer;

    if constexpr (totalTime) {
        totalTimer = Clock::now();
    }

    for (const auto& q : _queries) {
        if constexpr (perQuery) {
            queryTimer = Clock::now();
        }

        bool res = query(q);

        if constexpr (perQuery) {
            _res.queryTimes.at(_currentRun)[q]
                .emplace_back(duration_cast<TimeUnit>(Clock::now() - queryTimer));
        }

        if constexpr (debug) {
            if (!res) {
                spdlog::error("Query failed to execute : {}", q);
                spdlog::error(_cl.getError().fmtMessage());
            }
        }
    }

    if constexpr (totalTime) {
        auto duration = duration_cast<TimeUnit>(Clock::now() - totalTimer);
        _res.totalTimes.emplace_back(duration);
    }
    _currentRun++;
}
}
