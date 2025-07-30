#include "BenchmarkDriver.h"

#include <fstream>

#include "TuringClient.h"

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


void BenchmarkDriver::setup(std::vector<std::string>& buildQueries,
                            std::vector<std::string>& queries,
                            const std::string& buildFile, const std::string& queryFile) {
    // Generate the CREATE queries
    parseQueries(buildQueries, buildFile);
    if (buildQueries.empty()) {
        spdlog::error("No build queries provided.");
        return;
    }

    // Build the graph
    for (const auto& q : buildQueries) {
        if (!q.starts_with("CREATE")) {
            spdlog::error("Build queries contain non-create query : {}", q);
        }
        // QueryStatus res = _db.query(q, _graphName, &_mem, commit.value(), changeRes.value());
    }

    parseQueries(queries, queryFile);
    if (queries.empty()) {
        spdlog::error("No build queries provided.");
        return;
    }

    if (queries.empty()) {
        throw std::runtime_error("No queries provided");
    }
}

bool BenchmarkDriver::query(std::string_view q) {
    std::vector<std::unique_ptr<turingClient::TypedColumn>> ret;
    return _cl.query(q, _graphName, ret);
}
