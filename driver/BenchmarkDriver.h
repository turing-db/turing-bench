#include <chrono>
#include <cstdint>
#include <map>
#include <string>
#include <vector>
#include <iomanip>

#include "spdlog/spdlog.h"

#include "TuringClient.h"

namespace bm {

class BenchmarkDriver {
public:
    using TimeUnit = std::chrono::microseconds;

    struct BenchmarkResult {
        std::vector<TimeUnit> totalTimes;
        std::map<std::string, std::vector<TimeUnit>> queryTimes;
    };

    BenchmarkDriver(const std::string& graph, turingClient::TuringClient& cl,
                    uint32_t runs)
        : _graphName(graph),
          _cl(cl),
          _runs(runs)
    {
        _res.totalTimes.reserve(_runs);
        spdlog::set_pattern(_spdlogFmt);
    }

    bool setup(const std::string& buildFile, const std::string& queryFile);

    bool buildGraph(const std::string& buildFile);

    template <bool totalTime, bool perQuery, bool debug>
    void run();

    template <bool debug>
    void runQueryBenchmark();
    
    BenchmarkResult getResults() { return _res; }

    void reset() { _currentRun = 0; }

    void present(std::ostream& out=std::cout);

private:
    std::string _graphName;
    turingClient::TuringClient& _cl;
    BenchmarkResult _res;
    uint32_t _runs {1};
    uint32_t _currentRun {0};

    std::vector<std::string> _queries;

    size_t _changeNo {0};

    inline static const std::string _spdlogFmt = "[%H:%M:%S] %^[%l]%$ %v";

    void parseQueries(std::vector<std::string>& queries,
                      const std::string& filepath);

    bool queryDB(const std::string& q, const std::string& change = "");

    void presentTotal(std::ostream& out);
    void presentPerQuery(std::ostream& out);
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

        bool res = queryDB(q);

        if constexpr (perQuery) {
            _res.queryTimes[q].emplace_back(
                duration_cast<TimeUnit>(Clock::now() - queryTimer));
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

template <bool debug>
void BenchmarkDriver::runQueryBenchmark() {
    using namespace std::chrono;
    using Clock = high_resolution_clock;
    using Timestamp = time_point<high_resolution_clock>;
    
    Timestamp queryTimer;

    for (const auto& query : _queries) {
        spdlog::info("Running benchmarks for query: {}", query);
        for (; _currentRun < _runs; _currentRun++) {
            std::cout << "\r" << std::setw(_spdlogFmt.size() - 4) << " " << "Run "
                      << _currentRun + 1 << "/" << _runs << std::flush;

            queryTimer = Clock::now();

            bool res = queryDB(query);
            if constexpr (debug) {
                if (!res) {
                    spdlog::error("Query {} failed to execute:", query);
                    spdlog::error(_cl.getError().fmtMessage());
                    return;
                }
            }
        }
        std::cout << std::endl;

        TimeUnit timeTaken = duration_cast<TimeUnit>(Clock::now() - queryTimer);

        _res.queryTimes[query].emplace_back(timeTaken);
    }
}

}
