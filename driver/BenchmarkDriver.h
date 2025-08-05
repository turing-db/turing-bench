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

    bool setup(const std::string& buildFile, const std::string& queryFile);

    bool buildGraph(const std::string& buildFile);

    template <bool totalTime, bool perQuery, bool debug>
    void run();

private:
    using TimeUnit = std::chrono::microseconds;

    std::string _graphName;
    turingClient::TuringClient& _cl;

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

        Timestamp pre;
        Timestamp post;
        std::vector<TimeUnit> queryTimes(_queries.size());
        Timestamp queryTimer;

        if constexpr (totalTime) {
            pre = Clock::now();
        }

        for (size_t i {0}; const auto& q : _queries) {
            if constexpr (perQuery) {
                queryTimer = Clock::now();
            }

            bool res = query(q);

            if constexpr (perQuery) {
                queryTimes[i] = duration_cast<TimeUnit>(Clock::now() - queryTimer);
            }

            if constexpr (debug) {
                if (!res) {
                    spdlog::error("Query failed to execute : {}", q);
                    spdlog::error(_cl.getError().fmtMessage());
                }
            }
        }

        if constexpr (totalTime) {
            post = Clock::now();
            auto duration = duration_cast<TimeUnit>(post - pre);
            spdlog::info("Total time: {} us", duration.count());
        }

        if constexpr (perQuery) {
            // for (size_t i {0}; i < _queries.size(); i++) {
            //     spdlog::info("{} : {}", _queries[i], queryTimes[i].count());
            // }
        }
}
}
