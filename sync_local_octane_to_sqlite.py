import argparse
import datetime
import glob
import json
import os
import re
from collections import defaultdict

from octane_db import OctaneSQLiteStore, default_db_path


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--db-path", default=None)
    p.add_argument("--years", default="auto")
    p.add_argument("--team", default="DTSV_China")
    p.add_argument("--defect-dirs", default="defect")
    p.add_argument("--mr-dir", default="mr")
    p.add_argument("--history-dir", default="history")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--report-path", default=None)
    return p.parse_args()


def parse_years(s):
    years = []
    for x in s.split(","):
        x = x.strip()
        if x.isdigit() and len(x) == 4:
            years.append(int(x))
    return sorted(set(years))


def detect_years(repo_root, defect_dirs, mr_dir):
    years = set()
    for d in defect_dirs:
        d_abs = d if os.path.isabs(d) else os.path.join(repo_root, d)
        if not os.path.isdir(d_abs):
            continue
        for p in glob.glob(os.path.join(d_abs, "*_defect.json")):
            y = infer_year_from_name(os.path.basename(p))
            if y:
                years.add(int(y))
    mr_abs = mr_dir if os.path.isabs(mr_dir) else os.path.join(repo_root, mr_dir)
    if os.path.isdir(mr_abs):
        for p in glob.glob(os.path.join(mr_abs, "R*.json")):
            y, _ = infer_mr_release_and_year(os.path.basename(p))
            if y:
                years.add(int(y))
    if not years:
        years.add(datetime.datetime.now().year)
    return sorted(years)


def read_json_data(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []
    if isinstance(data, dict) and isinstance(data.get("data"), list):
        return data["data"]
    if isinstance(data, list):
        return data
    return []


def read_json_obj(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def infer_year_from_name(name):
    m = re.search(r"(20\d{2})", name)
    if not m:
        return None
    return int(m.group(1))


def infer_team_from_defect_file(base, default_team):
    m = re.match(r"^\d{4}_(.+)_defect\.json$", base)
    if not m:
        return default_team
    team = m.group(1).strip()
    return team or default_team


def infer_mr_release_and_year(base):
    m = re.match(r"^R(\d{2})(\d{2})\.json$", base, flags=re.IGNORECASE)
    if not m:
        return None, None
    yy = int(m.group(1))
    rel = int(m.group(2))
    year = 2000 + yy
    spec = f"R-{yy:02d}-{rel:02d}"
    return year, spec


def collect_defect_files(repo_root, defect_dirs, years):
    files = []
    for d in defect_dirs:
        d_abs = d if os.path.isabs(d) else os.path.join(repo_root, d)
        if not os.path.isdir(d_abs):
            continue
        for y in years:
            patterns = [
                os.path.join(d_abs, f"{y}_defect.json"),
                os.path.join(d_abs, f"{y}_*_defect.json"),
            ]
            for pat in patterns:
                files.extend(glob.glob(pat))
    out = []
    seen = set()
    for p in sorted(files):
        b = os.path.basename(p)
        if "master" in b.lower():
            continue
        if "fail" in b.lower():
            continue
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
    return out


def collect_mr_files(repo_root, mr_dir, years):
    d_abs = mr_dir if os.path.isabs(mr_dir) else os.path.join(repo_root, mr_dir)
    if not os.path.isdir(d_abs):
        return []
    files = glob.glob(os.path.join(d_abs, "R*.json"))
    out = []
    for p in sorted(files):
        y, _ = infer_mr_release_and_year(os.path.basename(p))
        if y in years:
            out.append(p)
    return out


def collect_history_files(repo_root, history_dir):
    d_abs = history_dir if os.path.isabs(history_dir) else os.path.join(repo_root, history_dir)
    if not os.path.isdir(d_abs):
        return []
    return sorted(glob.glob(os.path.join(d_abs, "*_history.json")))


def build_defect_payloads(files, default_team):
    grouped = defaultdict(dict)
    file_stats = []
    for p in files:
        base = os.path.basename(p)
        year = infer_year_from_name(base)
        team = infer_team_from_defect_file(base, default_team)
        records = read_json_data(p)
        kept = 0
        for r in records:
            if not isinstance(r, dict):
                continue
            did = r.get("id")
            if not did:
                continue
            grouped[(team, year)][str(did)] = r
            kept += 1
        file_stats.append({"file": p, "year": year, "team": team, "records": len(records), "kept": kept})
    final_grouped = {}
    for k, m in grouped.items():
        final_grouped[k] = list(m.values())
    return final_grouped, file_stats


def build_mr_payloads(files, default_team):
    grouped = defaultdict(dict)
    file_stats = []
    for p in files:
        base = os.path.basename(p)
        year, spec = infer_mr_release_and_year(base)
        if not year or not spec:
            continue
        records = read_json_data(p)
        kept = 0
        for r in records:
            if not isinstance(r, dict):
                continue
            rid = r.get("id")
            if not rid:
                continue
            grouped[(default_team, year, spec)][str(rid)] = r
            kept += 1
        file_stats.append({"file": p, "year": year, "spec": spec, "records": len(records), "kept": kept})
    final_grouped = {}
    for k, m in grouped.items():
        final_grouped[k] = list(m.values())
    return final_grouped, file_stats


def build_history_payloads(files):
    out = {}
    file_stats = []
    for p in files:
        base = os.path.basename(p)
        m = re.match(r"^(.+)_history\.json$", base)
        if not m:
            continue
        defect_id = m.group(1)
        payload = read_json_obj(p)
        total_count = payload.get("total_count") if isinstance(payload, dict) else None
        out[str(defect_id)] = {"payload": payload, "total_count": total_count, "file": p}
        file_stats.append({"file": p, "defect_id": defect_id, "total_count": total_count})
    return out, file_stats


def current_id_set(conn, table, id_col):
    cur = conn.cursor()
    rows = cur.execute(f"SELECT {id_col} FROM {table}").fetchall()
    return {str(r[0]) for r in rows if r and r[0] is not None}


def ensure_report_path(repo_root, report_path):
    if report_path:
        return report_path
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    d = os.path.join(repo_root, "database", "backups")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, f"local_file_sync_report_{ts}.json")


def _name_or_full(v):
    if isinstance(v, dict):
        return v.get("full_name") or v.get("name")
    return v


def _nested_name(d, key):
    v = d.get(key)
    if isinstance(v, dict):
        return v.get("name") or v.get("full_name")
    return None


def _extract_joined_names(value):
    data = None
    if isinstance(value, dict):
        data = value.get("data", [])
    elif isinstance(value, list):
        data = value
    if not isinstance(data, list):
        return None
    vals = []
    for x in data:
        if isinstance(x, dict):
            n = x.get("name")
            if n:
                vals.append(n)
    return ",".join(vals) if vals else None


def _extract_relation(value):
    if value is None:
        return None
    if isinstance(value, dict):
        return value.get("id") or value.get("name") or value.get("full_name")
    if isinstance(value, list):
        vals = []
        for x in value:
            if isinstance(x, dict):
                v = x.get("id") or x.get("name") or x.get("full_name")
                if v is not None:
                    vals.append(str(v))
            elif x is not None:
                vals.append(str(x))
        return ",".join(vals) if vals else None
    return str(value)


def _build_defect_row(defect, year, fetched_at):
    phase = _nested_name(defect, "phase")
    severity = _nested_name(defect, "severity")
    status_phase = f"{phase}_{severity}" if phase and severity else phase
    row = {
        "defect_id": str(defect.get("id")),
        "name": defect.get("name"),
        "creation_time": defect.get("creation_time"),
        "last_modified": defect.get("last_modified"),
        "team": _name_or_full(defect.get("team")),
        "problem_finder_team": _name_or_full(defect.get("problem_finder_team_udf")),
        "program": _name_or_full(defect.get("program")),
        "author": _name_or_full(defect.get("author")),
        "aida_businesskey": defect.get("aida_businesskey_udf"),
        "aida_english": None,
        "top_aida": None,
        "product_areas": _extract_joined_names(defect.get("product_areas")),
        "user_tags": _extract_joined_names(defect.get("user_tags")),
        "phase": phase,
        "severity": severity,
        "problem_severity": _nested_name(defect, "problem_severity_udf"),
        "status_phase": status_phase,
        "owner": _name_or_full(defect.get("owner")),
        "detected_by": _name_or_full(defect.get("detected_by")),
        "detected_in_release": _name_or_full(defect.get("detected_in_release")),
        "software_version": defect.get("software_version_udf"),
        "vin": defect.get("vin_udf"),
        "assigned_ecu": _name_or_full(defect.get("assigned_ecu_udf")),
        "lead_model": _name_or_full(defect.get("lead_model_udf")),
        "ecu_no_of_changes": defect.get("ecu_no_of_changes_udf"),
        "parent_id": defect.get("parent", {}).get("id") if isinstance(defect.get("parent"), dict) else None,
        "parent_child_type": _nested_name(defect, "parent_child_udf"),
        "relation_to": _extract_relation(defect.get("relation_to_udf")),
        "test_week": None,
        "risk_score": None,
        "fv": None,
        "fvp": None,
        "tqr": defect.get("tqr_udf"),
        "blocking_reason": defect.get("blocking_reason_udf"),
        "error_occurrence": defect.get("error_occurrence_udf"),
        "solution_responsible": _name_or_full(defect.get("solution_responsible_udf")),
        "solution_cluster": _name_or_full(defect.get("solution_cluster_udf")),
        "reporting_class": _extract_joined_names(defect.get("reporting_class_udf")),
        "function_responsible": _name_or_full(defect.get("function_responsible1_udf")),
        "involved_i_step": _name_or_full(defect.get("involved_i_step1_udf")),
        "first_use_sop_of_function": defect.get("first_use_sop_of_function_udf"),
        "tolerated_count": defect.get("tolerated_count_udf"),
        "reprel_changes": defect.get("reprel_changes_udf"),
        "raw_json": json.dumps(defect, ensure_ascii=False),
        "year": year,
        "fetched_at": fetched_at,
    }
    return row


def insert_new_defects_compatible(conn, defects, year, existing_ids):
    cols = [r[1] for r in conn.execute("PRAGMA table_info(octane_defects)").fetchall()]
    if not cols:
        return 0
    fetched_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    insert_cols = [c for c in cols if c in _build_defect_row({}, year, fetched_at)]
    if "defect_id" not in insert_cols:
        return 0
    placeholders = ",".join(["?"] * len(insert_cols))
    sql = f"INSERT INTO octane_defects ({','.join(insert_cols)}) VALUES ({placeholders})"
    def scalar(v):
        if isinstance(v, (dict, list)):
            return json.dumps(v, ensure_ascii=False)
        return v
    to_insert = []
    for d in defects:
        if not isinstance(d, dict):
            continue
        did = d.get("id")
        if did is None:
            continue
        did_s = str(did)
        if did_s in existing_ids:
            continue
        row_map = _build_defect_row(d, year, fetched_at)
        to_insert.append(tuple(scalar(row_map.get(c)) for c in insert_cols))
        existing_ids.add(did_s)
    if not to_insert:
        return 0
    conn.executemany(sql, to_insert)
    conn.commit()
    return len(to_insert)


def main():
    args = parse_args()
    repo_root = os.path.dirname(os.path.abspath(__file__))
    db_path = args.db_path or default_db_path(repo_root)
    defect_dirs = [x.strip() for x in args.defect_dirs.split(",") if x.strip()]
    if str(args.years).strip().lower() == "auto":
        years = detect_years(repo_root, defect_dirs, args.mr_dir)
    else:
        years = parse_years(args.years)
        if not years:
            years = detect_years(repo_root, defect_dirs, args.mr_dir)

    defect_files = collect_defect_files(repo_root, defect_dirs, years)
    mr_files = collect_mr_files(repo_root, args.mr_dir, years)
    history_files = collect_history_files(repo_root, args.history_dir)

    defect_grouped, defect_file_stats = build_defect_payloads(defect_files, args.team)
    mr_grouped, mr_file_stats = build_mr_payloads(mr_files, args.team)
    history_map, history_file_stats = build_history_payloads(history_files)

    store = OctaneSQLiteStore(db_path)
    store.create_tables()
    store.create_optimized_tables()

    before_defect_ids = current_id_set(store._conn, "octane_defects", "defect_id")
    before_mr_ids = current_id_set(store._conn, "octane_manual_runs", "mr_id")
    before_hist_ids = current_id_set(store._conn, "octane_defect_histories", "defect_id")

    incoming_defect_ids = set()
    for records in defect_grouped.values():
        for r in records:
            if isinstance(r, dict) and r.get("id") is not None:
                incoming_defect_ids.add(str(r.get("id")))

    incoming_mr_ids = set()
    for records in mr_grouped.values():
        for r in records:
            if isinstance(r, dict) and r.get("id") is not None:
                incoming_mr_ids.add(str(r.get("id")))

    incoming_hist_ids = {str(k) for k in history_map.keys()}

    precheck = {
        "defects": {
            "incoming": len(incoming_defect_ids),
            "new": len(incoming_defect_ids - before_defect_ids),
            "update": len(incoming_defect_ids & before_defect_ids),
        },
        "manual_runs": {
            "incoming": len(incoming_mr_ids),
            "new": len(incoming_mr_ids - before_mr_ids),
            "update": len(incoming_mr_ids & before_mr_ids),
        },
        "histories": {
            "incoming": len(incoming_hist_ids),
            "new": len(incoming_hist_ids - before_hist_ids),
            "update": len(incoming_hist_ids & before_hist_ids),
        },
    }

    write_stats = {
        "defect_payload_rows": 0,
        "defect_optimized_rows": 0,
        "mr_payload_rows": 0,
        "mr_optimized_rows": 0,
        "history_rows": 0,
    }

    if args.execute:
        for (team, year), records in defect_grouped.items():
            if not records or not year:
                continue
            store.upsert_payload(kind="defects", team=team, year=int(year), spec="", payload={"data": records})
            write_stats["defect_payload_rows"] += 1
            write_stats["defect_optimized_rows"] += insert_new_defects_compatible(
                store._conn, records, int(year), before_defect_ids
            )

        for (team, year, spec), records in mr_grouped.items():
            if not records:
                continue
            store.upsert_payload(kind="manual_runs", team=team, year=int(year), spec=spec, payload={"data": records})
            write_stats["mr_payload_rows"] += 1
            write_stats["mr_optimized_rows"] += store.upsert_manual_runs_batch(manual_runs=records, year=int(year), spec=spec)

        for defect_id, obj in history_map.items():
            store.upsert_defect_history(
                defect_id=defect_id,
                team=args.team,
                payload=obj["payload"],
                total_count=obj.get("total_count"),
            )
            write_stats["history_rows"] += 1

    after_counts = {
        "octane_payloads": store._conn.execute("SELECT COUNT(*) FROM octane_payloads").fetchone()[0],
        "octane_defects": store._conn.execute("SELECT COUNT(*) FROM octane_defects").fetchone()[0],
        "octane_manual_runs": store._conn.execute("SELECT COUNT(*) FROM octane_manual_runs").fetchone()[0],
        "octane_defect_histories": store._conn.execute("SELECT COUNT(*) FROM octane_defect_histories").fetchone()[0],
    }
    after_year_defects = {
        str(y): c
        for y, c in store._conn.execute("SELECT year, COUNT(*) FROM octane_defects GROUP BY year ORDER BY year").fetchall()
    }
    after_year_mr = {
        str(y): c
        for y, c in store._conn.execute("SELECT year, COUNT(*) FROM octane_manual_runs GROUP BY year ORDER BY year").fetchall()
    }
    integrity = store._conn.execute("PRAGMA integrity_check").fetchone()[0]
    store.close()

    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "mode": "execute" if args.execute else "dry_run",
        "db_path": db_path,
        "years": years,
        "inputs": {
            "defect_files": defect_files,
            "mr_files": mr_files,
            "history_files_count": len(history_files),
        },
        "file_stats": {
            "defect_files": defect_file_stats,
            "mr_files": mr_file_stats,
            "history_files_sample": history_file_stats[:100],
        },
        "precheck": precheck,
        "write_stats": write_stats,
        "post": {
            "table_counts": after_counts,
            "defects_by_year": after_year_defects,
            "manual_runs_by_year": after_year_mr,
            "integrity_check": integrity,
        },
    }

    report_path = ensure_report_path(repo_root, args.report_path)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("REPORT_PATH=" + report_path)
    print("MODE=" + report["mode"])
    print("DB_PATH=" + db_path)
    print("DEFECT_FILES=" + str(len(defect_files)))
    print("MR_FILES=" + str(len(mr_files)))
    print("HISTORY_FILES=" + str(len(history_files)))
    print("PRECHECK=" + json.dumps(precheck, ensure_ascii=False))
    print("WRITE_STATS=" + json.dumps(write_stats, ensure_ascii=False))
    print("POST_TABLE_COUNTS=" + json.dumps(after_counts, ensure_ascii=False))
    print("INTEGRITY=" + str(integrity))


if __name__ == "__main__":
    main()
