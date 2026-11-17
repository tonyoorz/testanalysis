#!/usr/bin/env python3
"""Initialize PostgreSQL tables for Octane dual-write mode."""

import argparse
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="初始化 PostgreSQL Octane 数据表")
    parser.add_argument("--pg-url", default=os.environ.get("POSTGRES_URL", ""), help="PostgreSQL connection URL")
    parser.add_argument("--pg-schema", default=os.environ.get("PG_SCHEMA", "public"), help="PostgreSQL schema")
    parser.add_argument("--legacy-schema", action="store_true", help="仅创建 legacy 表")
    args = parser.parse_args()

    if not args.pg_url:
        print("错误: 请通过 --pg-url 或 POSTGRES_URL 提供连接串")
        return 1

    try:
        from pg_storage import OctanePostgresStore

        store = OctanePostgresStore(args.pg_url, schema=args.pg_schema)
        store.create_tables()
        if not args.legacy_schema:
            store.create_optimized_tables()
        store.close()
        print(f"✅ PostgreSQL 初始化完成 (schema={args.pg_schema}, legacy_only={args.legacy_schema})")
        return 0
    except Exception as exc:
        print(f"❌ 初始化失败: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
