import json
import pandas as pd
import os

def export_semantic_catalog():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_path = os.path.join(base_dir, "semantic_catalog", "datasets.json")
    output_path = os.path.join(base_dir, "semantic_catalog_export_v2.csv")

    if not os.path.exists(datasets_path):
        print(f"Error: {datasets_path} not found.")
        return

    try:
        with open(datasets_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    def _append(rows, dataset_id, column_name, meaning, aliases, section, source_fields=""):
        rows.append(
            {
                "dataset_id": dataset_id,
                "column_name": column_name,
                "section": section,
                "source_fields": source_fields,
                "current_meaning": meaning or "",
                "current_aliases": ",".join([str(x) for x in (aliases or []) if str(x).strip()]),
                "new_meaning(fill_here)": "",
                "new_aliases(fill_here)": "",
            }
        )

    rows = []
    for dataset in data.get("datasets", []):
        dataset_id = dataset.get("id")
        if not dataset_id:
            continue

        seen = set()
        meaning_map = {}
        alias_map = {}

        for dim in dataset.get("core_dimensions", []) or []:
            name = dim.get("name")
            if not name:
                continue
            meaning_map[name] = dim.get("meaning") or ""
            alias_map[name] = dim.get("aliases") or []
            _append(rows, dataset_id, name, meaning_map[name], alias_map[name], section="core_dimensions")
            seen.add(name)

        for dim in dataset.get("time_columns", []) or []:
            name = dim.get("name")
            if not name:
                continue
            meaning_map.setdefault(name, dim.get("meaning") or "")
            alias_map.setdefault(name, dim.get("aliases") or [])
            if name not in seen:
                _append(rows, dataset_id, name, meaning_map[name], alias_map[name], section="time_columns")
                seen.add(name)

        for name in dataset.get("primary_keys", []) or []:
            if not name or name in seen:
                continue
            _append(rows, dataset_id, name, meaning_map.get(name, ""), alias_map.get(name, []), section="primary_keys")
            seen.add(name)

        for name in dataset.get("common_columns", []) or []:
            if not name or name in seen:
                continue
            _append(rows, dataset_id, name, meaning_map.get(name, ""), alias_map.get(name, []), section="common_columns")
            seen.add(name)

        lineage = dataset.get("field_lineage") or {}
        if isinstance(lineage, dict):
            for name, src in lineage.items():
                if not name:
                    continue
                if name in seen:
                    continue
                _append(rows, dataset_id, name, meaning_map.get(name, ""), alias_map.get(name, []), section="field_lineage", source_fields=str(src))
                seen.add(name)

        list_lineage = dataset.get("list_field_lineage") or {}
        if isinstance(list_lineage, dict):
            for name, src in list_lineage.items():
                if not name:
                    continue
                if name in seen:
                    continue
                _append(rows, dataset_id, name, meaning_map.get(name, ""), alias_map.get(name, []), section="list_field_lineage", source_fields=str(src))
                seen.add(name)

    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Successfully exported to {output_path}")

if __name__ == "__main__":
    export_semantic_catalog()
