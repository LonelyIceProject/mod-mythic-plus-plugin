#include "ScriptRunner.h"
#include "SqliteFunctions.h"
#include "SqliteScriptTarget.h"
#include <sqlite3.h>
#include <algorithm>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <iterator>
#include <vector>

int main(int argc, char** argv)
{
    if (argc != 3)
        return 2;
    sqlite3* db = nullptr;
    if (sqlite3_open(":memory:", &db) != SQLITE_OK)
        return 2;
    RegisterMySqlFunctions(db);
    int status = 0;
    {
        SqliteScriptTarget target(db);
        std::ifstream schema(argv[1]);
        std::string ddl((std::istreambuf_iterator<char>(schema)), std::istreambuf_iterator<char>());
        DbError error;
        if (!target.Exec(ddl, error))
        {
            std::cerr << error.message << '\n';
            return 1;
        }
        std::vector<std::filesystem::path> scripts;
        for (auto const& file : std::filesystem::recursive_directory_iterator(argv[2]))
            if (file.is_regular_file() && file.path().extension() == ".sql")
                scripts.push_back(file.path());
        std::sort(scripts.begin(), scripts.end());
        for (auto const& path : scripts)
        {
            ScriptRunner runner(target);
            if (!runner.RunFile(path))
            {
                std::cerr << runner.GetError().ToString() << '\n';
                status = 1;
                break;
            }
            std::cout << path.filename().string() << ": OK\n";
        }
    }
    sqlite3_close(db);
    return status;
}
