#include "BenchmarkDriver.h"

#include <fstream>

#include "TuringClient.h"
#include "TypedColumn.h"

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

void BenchmarkDriver::setup(std::vector<std::string>& queries,
                            const std::string& filepath) {

    if (filepath.empty()) {
        throw std::runtime_error("No filepath provided");
    }

    // Generate queries and their types
    parseQueries(queries, filepath);

    if (queries.empty()) {
        throw std::runtime_error("No queries provided");
    }
}


void BenchmarkDriver::setup(std::vector<std::string>& queries,
                            const std::string& buildFile, const std::string& queryFile) {
    // Generate the CREATE queries
    std::vector<std::string> buildQueries;
    parseQueries(buildQueries, buildFile);
    if (buildQueries.empty()) {
        spdlog::error("No build queries provided.");
        return;
    }

    // Build the graph
    using Col = std::vector<std::unique_ptr<turingClient::TypedColumn>>;
    [[maybe_unused]] Col ret;

    query("change new");
    auto changeStr = std::to_string(_changeNo);
    for (const auto& q : buildQueries) {
        if (!q.starts_with("CREATE")) {
            spdlog::error("Build queries contain non-create query : {}", q);
        }
        query(q, changeStr); // XXX: Assumes first change in graph
    }
    query("change submit", changeStr);
    _changeNo++;

    parseQueries(queries, queryFile);
    if (queries.empty()) {
        spdlog::error("No build queries provided.");
        return;
    }

}

bool BenchmarkDriver::query(const std::string& q, const std::string& change) {
    std::vector<std::unique_ptr<turingClient::TypedColumn>> ret;
    bool res = _cl.query(q, _graphName, ret, "", change);
    if (!res) {
        spdlog::error("Error running: {}", q);
        spdlog::error(_cl.getError().fmtMessage());
    }
    spdlog::info("Ran {}", q);
    return res;
}
