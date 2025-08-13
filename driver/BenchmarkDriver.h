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
        std::map<std::string, std::pair<size_t, size_t>> queryDims;
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

    bool setup(const std::string& buildFile="", const std::string& queryFile="");

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

    bool createGraph(const std::string& graphName) {
        std::vector<std::unique_ptr<turingClient::TypedColumn>> ret;
        return _cl.query("create graph "+ graphName, "default", ret);
    }

    bool queryDB(const std::string& q, const std::string& change="");
    bool queryDB(std::vector<std::unique_ptr<turingClient::TypedColumn>>& col,
                 const std::string& query, const std::string& change="");

    bool buildGraph(const std::string& buildFile);
    bool loadGraph(const std::string& graph);

    void presentTotal(std::ostream& out);
    void presentPerQuery(std::ostream& out);

    inline static auto us = [](TimeUnit t) {
        using namespace std::literals;
        return std::to_string(t / 1us) + "us";
    };

    inline static auto ms = [](TimeUnit t) {
        using namespace std::literals;
        return std::to_string(t / 1ms) + "ms";
    };

    inline static auto s = [](TimeUnit t) {
        using namespace std::literals;
        return std::to_string(t / 1s) + "s";
    };

};

template <bool debug>
void BenchmarkDriver::runQueryBenchmark() {
    using namespace std::chrono;
    using Clock = high_resolution_clock;
    using Timestamp = time_point<high_resolution_clock>;

    Timestamp queryTimer;

    std::vector<std::unique_ptr<turingClient::TypedColumn>> ret;
    for (const auto& query : _queries) {
        ret.clear();
        spdlog::info("Running benchmarks for query: {}", query);
        for (; _currentRun < _runs; _currentRun++) {
            std::cout << "\r" << std::setw(_spdlogFmt.size() - 4) << " " << "Run "
                      << _currentRun + 1 << "/" << _runs << std::flush;

            queryTimer = Clock::now();

            bool res = queryDB(ret, query);
            if constexpr (debug) {
                if (!res) {
                    spdlog::error("Query {} failed to execute:", query);
                    spdlog::error(_cl.getError().fmtMessage());
                    return;
                }
                if (ret.size() == 0) {
                    spdlog::error("Query {} returned an empty column.", query);
                    return;
                }
            }
            TimeUnit timeTaken = duration_cast<TimeUnit>(Clock::now() - queryTimer);
            _res.queryTimes[query].emplace_back(timeTaken);
            _res.queryDims.try_emplace(query, ret.size(), ret.at(0)->size());
        }
        std::cout << std::endl;
        reset();
    }
}

}
