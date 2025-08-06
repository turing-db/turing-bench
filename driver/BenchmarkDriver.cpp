#include "BenchmarkDriver.h"

#include <chrono>
#include <fstream>
#include <numeric>

#include "TuringClient.h"
#include "TypedColumn.h"
#include "tabulate/table.hpp"

using namespace bm;

void BenchmarkDriver::parseQueries(std::vector<std::string>& queries,
                                   const std::string& filepath) {
    queries.clear();

    std::ifstream file(filepath);
    std::string line;

    while (std::getline(file, line, ';')) {
        // Trim whitespace
        size_t start = line.find_first_not_of(" \t\r\n");
        size_t end = line.find_last_not_of(" \t\r\n");
        if (start != std::string::npos && end != std::string::npos) {
            std::string query = line.substr(start, end - start + 1);
            if (!query.empty()) {
                queries.push_back(query);
            }
        }
    }
}

bool BenchmarkDriver::setup(const std::string& buildFile, const std::string& queryFile) {
    spdlog::info("Building graph from CYPHER queries in file {}.", buildFile);
    if (!buildGraph(buildFile)) {
        return false;
    }

    spdlog::info("Parsing CYPHER queries in file {}.", queryFile);
    parseQueries(_queries, queryFile);
    if (_queries.empty()) {
        spdlog::error("No queries provided in file {}.", queryFile);
        return false;
    }
    return true;
}

bool BenchmarkDriver::buildGraph(const std::string& buildFile) {
    // Parse the CREATE queries
    std::vector<std::string> buildQueries;
    parseQueries(buildQueries, buildFile);
    if (buildQueries.empty()) {
        spdlog::error("No build queries provided.");
        return false;
    }

    // Build the graph from parsed queries
    if (!query("change new")) {
        spdlog::error("Failed to create new change");
        spdlog::error(_cl.getError().fmtMessage());
        return false;
    }

    auto changeStr = std::to_string(_changeNo);

    for (const auto& createQuery : buildQueries) {
        if (!createQuery.starts_with("CREATE")) {
            spdlog::error("Build queries contain non-create query : {}", createQuery);
            return false;
        }

        bool res = query(createQuery, changeStr);
        if (!res) {
            spdlog::error("Failed to run build query: {}", createQuery);
            spdlog::error(_cl.getError().fmtMessage());
            return false;
        }
    }

    if (!query("change submit", changeStr)) {
        spdlog::error("Failed to submit change");
        spdlog::error(_cl.getError().fmtMessage());
        return false;
    }

    _changeNo++;
    return true;
}

bool BenchmarkDriver::query(const std::string& q, const std::string& change) {
    // NOTE: This has to be reconstructed each time otherwise json error..
    std::vector<std::unique_ptr<turingClient::TypedColumn>> ret;
    bool res = _cl.query(q, _graphName, ret, "", change);
    // for (const auto& v :ret) {
    //     spdlog::info("Query {} returned {} elements", q, v->size());
    // }
    return res;
}

void BenchmarkDriver::presentTotal(std::ostream& out) {
    auto times = _res.totalTimes;
    std::ranges::sort(times);
    const size_t n = _runs;

    auto sum = std::reduce(times.begin(), times.end());

    auto mean = sum / n;
    auto min = times.front();
    auto max = times.back();
    auto median = (n % 2) == 0 ? (times[n / 2 - 1] + times[n / 2]) / 2
                               : times[n / 2];

    using namespace tabulate;
    Table table;

    // auto timeString = [](TimeUnit t) { return std::to_string(t.count()); };
    auto ms = [](TimeUnit t) {
        return std::to_string(
            std::chrono::duration_cast<std::chrono::milliseconds>(t).count());
    };

    auto s = [](TimeUnit t) {
        return std::to_string(
            std::chrono::duration_cast<std::chrono::milliseconds>(t).count() / 1000.f);
    };

    table.add_row({"Results over " + std::to_string(n) + " runs", "ms", "s"});
    table.add_row({"Mean", ms(mean), s(mean)});
    table.add_row({"Min", ms(min), s(min)});
    table.add_row({"Max", ms(max), s(max)});
    table.add_row({"Median", ms(median), s(median)});

    auto avgThroughput =
        _queries.size() / std::chrono::duration_cast<std::chrono::seconds>(mean).count();

    table.add_row({"", "", ""});
    table.add_row({"Average throughput", "", std::to_string(avgThroughput) + " queries / second"});

    out << table << std::endl;
}

void BenchmarkDriver::presentPerQuery(std::ostream& out) {
}

void BenchmarkDriver::present(std::ostream& out) {

    if (!_res.totalTimes.empty()) {
        presentTotal(out);
    }

    if (!_res.queryTimes.empty()) {
        presentPerQuery(out);
    }

}
