import json
import os
import re
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso_datetime(value: Any) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        return None
    raw = value.strip()
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        try:
            if "." in raw:
                raw = raw.split(".", 1)[0]
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except Exception:
            return None


def _calc_test_week(value: Any) -> Optional[str]:
    dt = _parse_iso_datetime(value)
    if not dt:
        return None
    try:
        iso = dt.isocalendar()
        return f"{int(iso.year)}-CW{int(iso.week):02d}"
    except Exception:
        return None


def default_pg_url() -> str:
    return os.environ.get("POSTGRES_URL", "")


class OctanePostgresStore:
    """PostgreSQL store with an API compatible with downloader usage."""

    _DEFECT_COLUMNS: Sequence[str] = (
        "defect_id",
        "name",
        "creation_time",
        "last_modified",
        "team",
        "problem_finder_team",
        "program",
        "author",
        "aida_businesskey",
        "aida_english",
        "top_aida",
        "product_areas",
        "user_tags",
        "phase",
        "severity",
        "problem_severity",
        "status_phase",
        "owner",
        "detected_by",
        "detected_in_release",
        "software_version",
        "vin",
        "assigned_ecu",
        "lead_model",
        "ecu_no_of_changes",
        "parent_id",
        "parent_child_type",
        "relation_to",
        "test_week",
        "risk_score",
        "fv",
        "fvp",
        "tqr",
        "blocking_reason",
        "error_occurrence",
        "solution_responsible",
        "solution_cluster",
        "reporting_class",
        "function_responsible",
        "involved_i_step",
        "first_use_sop_of_function",
        "tolerated_count",
        "reprel_changes",
        "raw_json",
        "year",
        "fetched_at",
    )

    _MANUAL_RUN_COLUMNS: Sequence[str] = (
        "mr_id",
        "name",
        "test_name",
        "test_id",
        "creation_time",
        "last_modified",
        "started",
        "finished",
        "defect_id",
        "run_team",
        "program",
        "author",
        "run_by",
        "status",
        "native_status",
        "is_completed",
        "steps_num",
        "version_stamp",
        "release",
        "exec_model_series",
        "execution_sw_version",
        "test_version",
        "product_areas",
        "domain",
        "test_phase",
        "testing_tool_type",
        "taxonomies",
        "set_field",
        "target_ecu_conf",
        "testplatformid",
        "raw_json",
        "year",
        "spec",
        "fetched_at",
    )

    def __init__(self, pg_url: str, schema: str = "public"):
        self.pg_url = pg_url
        self.schema = schema or "public"
        self._conn = None
        self._connect()
        self._ensure_schema()

    def _connect(self) -> None:
        last_err = None
        try:
            import psycopg  # type: ignore

            self._conn = psycopg.connect(self.pg_url)
            self._conn.autocommit = False
            return
        except Exception as exc:  # pragma: no cover
            last_err = exc

        try:
            import psycopg2  # type: ignore

            self._conn = psycopg2.connect(self.pg_url)
            self._conn.autocommit = False
            return
        except Exception as exc2:  # pragma: no cover
            last_err = exc2

        raise RuntimeError(f"Failed to connect PostgreSQL: {last_err}")

    def close(self) -> None:
        if self._conn is None:
            return
        try:
            self._conn.close()
        except Exception:
            pass

    @contextmanager
    def _cursor(self):
        cur = self._conn.cursor()
        try:
            yield cur
        finally:
            cur.close()

    def _ensure_schema(self) -> None:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", self.schema):
            raise ValueError(f"Invalid schema name: {self.schema}")
        with self._cursor() as cur:
            cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{self.schema}"')
            cur.execute(f'SET search_path TO "{self.schema}"')
        self._conn.commit()

    def _set_schema(self, cur) -> None:
        cur.execute(f'SET search_path TO "{self.schema}"')

    @staticmethod
    def _normalize_year(year: Optional[int]) -> int:
        return int(year) if year is not None else -1

    @staticmethod
    def _safe_nested(data: Any, *keys: str, default: Any = None) -> Any:
        result = data
        for key in keys:
            if not isinstance(result, dict):
                return default
            result = result.get(key)
            if result is None:
                return default
        return result

    @staticmethod
    def _extract_full_name(value: Any) -> Any:
        if isinstance(value, dict):
            return value.get("full_name") or value.get("name")
        return value

    @staticmethod
    def _extract_relation_to(value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, dict):
            return value.get("name") or value.get("full_name") or value.get("id")
        if isinstance(value, list):
            parts: List[str] = []
            for item in value:
                if item is None:
                    continue
                if isinstance(item, dict):
                    cand = item.get("id") or item.get("name") or item.get("full_name")
                    if cand is not None:
                        parts.append(str(cand))
                else:
                    parts.append(str(item))
            normalized = [p.strip() for p in parts if p and p.strip()]
            return ",".join(normalized) if normalized else None
        if isinstance(value, str):
            value = value.strip()
            return value if value else None
        return str(value)

    @staticmethod
    def _extract_names(data: Any) -> Optional[str]:
        if data is None:
            return None
        if isinstance(data, dict):
            items = data.get("data", [])
            if not isinstance(items, list):
                return None
        elif isinstance(data, list):
            items = data
        else:
            return None

        names: List[str] = []
        for item in items:
            if isinstance(item, dict):
                name = item.get("name")
                if name:
                    names.append(str(name))
        return ",".join(names) if names else None

    @staticmethod
    def _get_aidas_list(product_areas: Any) -> List[str]:
        if not product_areas:
            return []
        if isinstance(product_areas, dict):
            items = product_areas.get("data", [])
        elif isinstance(product_areas, list):
            items = product_areas
        else:
            return []
        if not isinstance(items, list):
            return []
        out: List[str] = []
        for item in items:
            if isinstance(item, dict):
                name = item.get("name")
                if name:
                    out.append(str(name))
        return out

    @staticmethod
    def _get_top_req(req_list: List[str]) -> str:
        if not isinstance(req_list, list) or not req_list:
            return ""
        best = ""
        best_len = 10**9
        for req in req_list:
            if not isinstance(req, str):
                continue
            parts = req.split(" ")
            if not parts:
                continue
            tail = parts[-1]
            if tail and len(tail) < best_len:
                best_len = len(tail)
                best = req
        return best

    @staticmethod
    def _extract_english(text: Any) -> str:
        if not text:
            return "Unknown"
        words = re.findall(r"[a-zA-Z]+", str(text))
        return " ".join(words) if words else "Unknown"

    @staticmethod
    def _stringify(value: Any) -> Any:
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return value

    def create_tables(self) -> None:
        with self._cursor() as cur:
            self._set_schema(cur)
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS octane_payloads (
                    kind TEXT NOT NULL,
                    team TEXT NOT NULL,
                    year INTEGER NOT NULL DEFAULT -1,
                    spec TEXT NOT NULL,
                    payload_json JSONB NOT NULL,
                    fetched_at TIMESTAMPTZ NOT NULL,
                    PRIMARY KEY(kind, team, year, spec)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS octane_defect_histories (
                    defect_id TEXT PRIMARY KEY,
                    team TEXT NOT NULL,
                    total_count INTEGER,
                    payload_json JSONB NOT NULL,
                    fetched_at TIMESTAMPTZ NOT NULL
                )
                """
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_octane_payloads_kind_year_team ON octane_payloads(kind, year, team)"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_octane_histories_team ON octane_defect_histories(team)"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_octane_histories_team_defect ON octane_defect_histories(team, defect_id)"
            )
        self._conn.commit()

    def create_optimized_tables(self) -> None:
        with self._cursor() as cur:
            self._set_schema(cur)
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS octane_defects (
                    defect_id TEXT PRIMARY KEY,
                    name TEXT,
                    creation_time TEXT,
                    last_modified TEXT,
                    team TEXT,
                    problem_finder_team TEXT,
                    program TEXT,
                    author TEXT,
                    aida_businesskey TEXT,
                    aida_english TEXT,
                    top_aida TEXT,
                    product_areas TEXT,
                    user_tags TEXT,
                    phase TEXT,
                    severity TEXT,
                    problem_severity TEXT,
                    status_phase TEXT,
                    owner TEXT,
                    detected_by TEXT,
                    detected_in_release TEXT,
                    software_version TEXT,
                    vin TEXT,
                    assigned_ecu TEXT,
                    lead_model TEXT,
                    ecu_no_of_changes INTEGER,
                    parent_id TEXT,
                    parent_child_type TEXT,
                    relation_to TEXT,
                    test_week TEXT,
                    risk_score DOUBLE PRECISION,
                    fv TEXT,
                    fvp TEXT,
                    tqr TEXT,
                    blocking_reason TEXT,
                    error_occurrence TEXT,
                    solution_responsible TEXT,
                    solution_cluster TEXT,
                    reporting_class TEXT,
                    function_responsible TEXT,
                    involved_i_step TEXT,
                    first_use_sop_of_function TEXT,
                    tolerated_count INTEGER,
                    reprel_changes TEXT,
                    raw_json JSONB NOT NULL,
                    year INTEGER,
                    fetched_at TIMESTAMPTZ NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS octane_manual_runs (
                    mr_id TEXT PRIMARY KEY,
                    name TEXT,
                    test_name TEXT,
                    test_id TEXT,
                    creation_time TEXT,
                    last_modified TEXT,
                    started TEXT,
                    finished TEXT,
                    defect_id TEXT,
                    run_team TEXT,
                    program TEXT,
                    author TEXT,
                    run_by TEXT,
                    status TEXT,
                    native_status TEXT,
                    is_completed INTEGER,
                    steps_num INTEGER,
                    version_stamp TEXT,
                    release TEXT,
                    exec_model_series TEXT,
                    execution_sw_version TEXT,
                    test_version TEXT,
                    product_areas TEXT,
                    domain TEXT,
                    test_phase TEXT,
                    testing_tool_type TEXT,
                    taxonomies TEXT,
                    set_field TEXT,
                    target_ecu_conf TEXT,
                    testplatformid TEXT,
                    raw_json JSONB NOT NULL,
                    year INTEGER,
                    spec TEXT,
                    fetched_at TIMESTAMPTZ NOT NULL
                )
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS idx_defects_year ON octane_defects(year)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_defects_team ON octane_defects(team)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_defects_phase ON octane_defects(phase)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_defects_severity ON octane_defects(severity)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_defects_program ON octane_defects(program)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_manual_runs_year ON octane_manual_runs(year)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_manual_runs_release ON octane_manual_runs(release)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_manual_runs_defect ON octane_manual_runs(defect_id)")
        self._conn.commit()

    def upsert_payload(
        self,
        *,
        kind: str,
        team: str,
        year: Optional[int],
        spec: str,
        payload: Any,
        fetched_at: Optional[str] = None,
        commit: bool = True,
    ) -> None:
        fetched_at_val = fetched_at or _utc_now_iso()
        year_val = self._normalize_year(year)
        payload_json = json.dumps(payload, ensure_ascii=False)
        with self._cursor() as cur:
            self._set_schema(cur)
            cur.execute(
                """
                INSERT INTO octane_payloads(kind, team, year, spec, payload_json, fetched_at)
                VALUES (%s, %s, %s, %s, %s::jsonb, %s)
                ON CONFLICT(kind, team, year, spec) DO UPDATE SET
                    payload_json=EXCLUDED.payload_json,
                    fetched_at=EXCLUDED.fetched_at
                """,
                (kind, team, year_val, spec, payload_json, fetched_at_val),
            )
        if commit:
            self._conn.commit()

    def upsert_defect_history(
        self,
        *,
        defect_id: str,
        team: str,
        payload: Any,
        total_count: Optional[int] = None,
        fetched_at: Optional[str] = None,
        commit: bool = True,
    ) -> None:
        fetched_at_val = fetched_at or _utc_now_iso()
        payload_json = json.dumps(payload, ensure_ascii=False)
        total = total_count
        if total is None and isinstance(payload, dict):
            maybe = payload.get("total_count")
            total = int(maybe) if maybe is not None else None
        with self._cursor() as cur:
            self._set_schema(cur)
            cur.execute(
                """
                INSERT INTO octane_defect_histories(defect_id, team, total_count, payload_json, fetched_at)
                VALUES (%s, %s, %s, %s::jsonb, %s)
                ON CONFLICT(defect_id) DO UPDATE SET
                    team=EXCLUDED.team,
                    total_count=EXCLUDED.total_count,
                    payload_json=EXCLUDED.payload_json,
                    fetched_at=EXCLUDED.fetched_at
                """,
                (str(defect_id), team, total, payload_json, fetched_at_val),
            )
        if commit:
            self._conn.commit()

    def upsert_defects_batch(self, defects: List[Dict[str, Any]], year: int, fetched_at: Optional[str] = None) -> int:
        if not defects:
            return 0
        fetched_at_val = fetched_at or _utc_now_iso()
        aida_fv_map = self._load_aida_fv_mapping()
        records: List[Tuple[Any, ...]] = []

        for defect in defects:
            try:
                defect_id = defect.get("id")
                if not defect_id:
                    continue
                product_areas_raw = defect.get("product_areas")
                top_aida = self._get_top_req(self._get_aidas_list(product_areas_raw))
                aida_english = self._extract_english(top_aida)
                phase = self._extract_full_name(defect.get("phase"))
                severity = self._extract_full_name(defect.get("severity"))
                fv = self._assign_fv_from_aida(top_aida, aida_english, aida_fv_map)
                row = {
                    "defect_id": str(defect_id),
                    "name": defect.get("name"),
                    "creation_time": defect.get("creation_time"),
                    "last_modified": defect.get("last_modified"),
                    "team": self._extract_full_name(defect.get("team")),
                    "problem_finder_team": self._extract_full_name(defect.get("problem_finder_team_udf")),
                    "program": self._extract_full_name(defect.get("program")),
                    "author": self._extract_full_name(defect.get("author")),
                    "aida_businesskey": defect.get("aida_businesskey_udf"),
                    "aida_english": aida_english,
                    "top_aida": top_aida,
                    "product_areas": self._extract_names(product_areas_raw),
                    "user_tags": self._extract_names(defect.get("user_tags")),
                    "phase": phase,
                    "severity": severity,
                    "problem_severity": self._extract_full_name(defect.get("problem_severity_udf")),
                    "status_phase": f"{phase}_{severity}" if phase and severity else phase,
                    "owner": self._extract_full_name(defect.get("owner")),
                    "detected_by": self._extract_full_name(defect.get("detected_by")),
                    "detected_in_release": self._extract_full_name(defect.get("detected_in_release")),
                    "software_version": defect.get("software_version_udf"),
                    "vin": defect.get("vin_udf"),
                    "assigned_ecu": self._extract_full_name(defect.get("assigned_ecu_udf")),
                    "lead_model": self._extract_full_name(defect.get("lead_model_udf")),
                    "ecu_no_of_changes": defect.get("ecu_no_of_changes_udf"),
                    "parent_id": self._safe_nested(defect, "parent", "id"),
                    "parent_child_type": self._extract_full_name(defect.get("parent_child_udf")),
                    "relation_to": self._extract_relation_to(defect.get("relation_to_udf")),
                    "test_week": _calc_test_week(defect.get("creation_time")),
                    "risk_score": None,
                    "fv": fv,
                    "fvp": self._get_fvp_from_fv(fv),
                    "tqr": self._stringify(defect.get("tqr_udf")),
                    "blocking_reason": self._extract_full_name(defect.get("blocking_reason_udf")),
                    "error_occurrence": self._extract_full_name(defect.get("error_occurrence_udf")),
                    "solution_responsible": self._extract_full_name(defect.get("solution_responsible_udf")),
                    "solution_cluster": self._extract_full_name(defect.get("solution_cluster_udf")),
                    "reporting_class": self._extract_full_name(defect.get("reporting_class_udf")),
                    "function_responsible": self._extract_full_name(defect.get("function_responsible1_udf")),
                    "involved_i_step": self._extract_full_name(defect.get("involved_i_step1_udf")),
                    "first_use_sop_of_function": self._extract_full_name(defect.get("first_use_sop_of_function_udf")),
                    "tolerated_count": defect.get("tolerated_count_udf"),
                    "reprel_changes": self._stringify(defect.get("reprel_changes_udf")),
                    "raw_json": json.dumps(defect, ensure_ascii=False),
                    "year": int(year),
                    "fetched_at": fetched_at_val,
                }
                records.append(tuple(row[col] for col in self._DEFECT_COLUMNS))
            except Exception:
                continue

        if not records:
            return 0

        placeholders = ["%s"] * len(self._DEFECT_COLUMNS)
        placeholders[self._DEFECT_COLUMNS.index("raw_json")] = "%s::jsonb"
        cols_sql = ", ".join(self._DEFECT_COLUMNS)
        vals_sql = ", ".join(placeholders)
        updates = ", ".join(f"{c}=EXCLUDED.{c}" for c in self._DEFECT_COLUMNS if c != "defect_id")
        query = f"INSERT INTO octane_defects ({cols_sql}) VALUES ({vals_sql}) ON CONFLICT(defect_id) DO UPDATE SET {updates}"

        with self._cursor() as cur:
            self._set_schema(cur)
            cur.executemany(query, records)
        self._conn.commit()
        return len(records)

    def upsert_manual_runs_batch(
        self,
        manual_runs: List[Dict[str, Any]],
        year: int,
        spec: str,
        fetched_at: Optional[str] = None,
    ) -> int:
        if not manual_runs:
            return 0
        fetched_at_val = fetched_at or _utc_now_iso()
        records: List[Tuple[Any, ...]] = []
        for mr in manual_runs:
            try:
                mr_id = mr.get("id")
                if not mr_id:
                    continue
                row = {
                    "mr_id": str(mr_id),
                    "name": mr.get("name"),
                    "test_name": self._safe_nested(mr, "test", "name"),
                    "test_id": self._safe_nested(mr, "test", "id"),
                    "creation_time": mr.get("creation_time"),
                    "last_modified": mr.get("last_modified"),
                    "started": mr.get("started"),
                    "finished": mr.get("finished_udf"),
                    "defect_id": self._safe_nested(mr, "defect", "id"),
                    "run_team": self._extract_full_name(mr.get("run_team_000_udf")),
                    "program": self._extract_full_name(mr.get("program")),
                    "author": self._extract_full_name(mr.get("author")),
                    "run_by": self._extract_full_name(mr.get("run_by")),
                    "status": self._extract_full_name(mr.get("status")),
                    "native_status": self._extract_full_name(mr.get("native_status")),
                    "is_completed": 1 if mr.get("is_completed") else 0,
                    "steps_num": mr.get("steps_num"),
                    "version_stamp": self._stringify(mr.get("version_stamp")),
                    "release": self._extract_full_name(mr.get("release")),
                    "exec_model_series": self._extract_full_name(mr.get("exec_model_series_udf")),
                    "execution_sw_version": self._stringify(mr.get("execution_sw_version_udf")),
                    "test_version": self._extract_full_name(mr.get("test_version")),
                    "product_areas": self._extract_names(mr.get("product_areas")),
                    "domain": self._extract_full_name(mr.get("domain_udf")),
                    "test_phase": self._extract_full_name(mr.get("test_phase")),
                    "testing_tool_type": self._extract_full_name(mr.get("testing_tool_type")),
                    "taxonomies": self._extract_names(mr.get("taxonomies")),
                    "set_field": self._extract_full_name(mr.get("set_udf")),
                    "target_ecu_conf": self._stringify(mr.get("target_ecu_conf_udf")),
                    "testplatformid": self._stringify(mr.get("testplatformid_udf")),
                    "raw_json": json.dumps(mr, ensure_ascii=False),
                    "year": int(year),
                    "spec": spec,
                    "fetched_at": fetched_at_val,
                }
                records.append(tuple(row[col] for col in self._MANUAL_RUN_COLUMNS))
            except Exception:
                continue

        if not records:
            return 0
        placeholders = ["%s"] * len(self._MANUAL_RUN_COLUMNS)
        placeholders[self._MANUAL_RUN_COLUMNS.index("raw_json")] = "%s::jsonb"
        cols_sql = ", ".join(self._MANUAL_RUN_COLUMNS)
        vals_sql = ", ".join(placeholders)
        updates = ", ".join(f"{c}=EXCLUDED.{c}" for c in self._MANUAL_RUN_COLUMNS if c != "mr_id")
        query = f"INSERT INTO octane_manual_runs ({cols_sql}) VALUES ({vals_sql}) ON CONFLICT(mr_id) DO UPDATE SET {updates}"
        with self._cursor() as cur:
            self._set_schema(cur)
            cur.executemany(query, records)
        self._conn.commit()
        return len(records)

    def _load_aida_fv_mapping(self) -> Dict[str, str]:
        mapping: Dict[str, str] = {}
        excel_file = "aida/top_aida_project_fv_mapping.xlsx"
        if not os.path.exists(excel_file):
            return mapping
        try:
            import pandas as pd

            for sheet_name in ["IDCevo", "IDC", "MGU", "App", "RSU"]:
                try:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                except Exception:
                    continue
                if "top_aida" in df.columns and "fv" in df.columns:
                    for _, row in df.iterrows():
                        top_aida = row.get("top_aida")
                        fv = row.get("fv")
                        if top_aida is None or fv is None:
                            continue
                        aida = str(top_aida).strip()
                        fv_s = str(fv).strip()
                        if aida and fv_s and fv_s != "nan":
                            mapping[aida] = fv_s
                            mapping[self._extract_english(aida)] = fv_s
                if "aida_english" in df.columns and "fv" in df.columns:
                    for _, row in df.iterrows():
                        aida_english = row.get("aida_english")
                        fv = row.get("fv")
                        if aida_english is None or fv is None:
                            continue
                        aida_s = str(aida_english).strip()
                        fv_s = str(fv).strip()
                        if aida_s and fv_s and fv_s != "nan":
                            mapping[aida_s] = fv_s
        except Exception:
            return mapping
        return mapping

    @staticmethod
    def _assign_fv_from_aida(top_aida: str, aida_english: str, mapping: Dict[str, str]) -> Optional[str]:
        unknown_tokens = {"", "unknown", "none", "nan"}
        if top_aida:
            top_aida_key = str(top_aida).strip()
            if top_aida_key and top_aida_key.lower() not in unknown_tokens:
                fv = mapping.get(top_aida_key)
                if fv:
                    return fv
        if aida_english:
            aida_key = str(aida_english).strip()
            if aida_key and aida_key.lower() not in unknown_tokens:
                return mapping.get(aida_key)
        return None

    @staticmethod
    def _get_fvp_from_fv(fv: Optional[str]) -> Optional[str]:
        if not fv:
            return None
        fvp_mapping = {
            "DIPS_TSP_Call_Services": "Tianhua",
            "DIPS_TSP_CD_Updates": "Tianhua",
            "DIPS_TSP_Remote_Services": "Tianhua",
            "eMob": "Tianhua",
            "DIPS_TSP_MobileApps": "Tianhua",
            "DIPS_TSP_Enabler": "Tianhua",
            "IuK_TSP_Navi": "Tony",
            "IuK_TSP_AZV": "Xu Miao",
            "IuK_TSP_Entertainment": "Xu Miao",
            "IuK_TSP_Audio": "Xu Miao",
            "IuK_TSP_Connectivity": "Xu Miao",
            "IuK_TSP_HMI": "Jerry",
            "DIPS_TSP_RSU": "Jerry",
            "IuK_TSP_Carfunctions": "Jerry",
            "IuK_TSP_Perso CN": "Jerry",
            "RSU": "Jerry",
            "Mybmw App": "Marin",
        }
        return fvp_mapping.get(fv)
