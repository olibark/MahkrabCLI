#include <sqlite3.h>
#include <stdio.h>

int main() {
    sqlite3 *db;
    int rc = sqlite3_open(":memory:", &db);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Cannot open database: %s\n", sqlite3_errmsg(db));
        return 1;
    }
    printf("Opened SQLite database in memory.\n");
    sqlite3_close(db);
    return 0;
}
