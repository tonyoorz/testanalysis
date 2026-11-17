import argparse
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="初始化本地 Octane SQLite 数据库")
    parser.add_argument("--db-path", default=None, help="SQLite 数据库路径 (默认: database/local_data.db)")
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.abspath(__file__))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)

    from octane_db import OctaneSQLiteStore, default_db_path

    db_path = args.db_path or default_db_path(repo_root)
    store = OctaneSQLiteStore(db_path)
    store.create_tables()
    store.close()
    print(db_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

