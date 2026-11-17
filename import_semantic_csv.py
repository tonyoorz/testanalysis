import json
import pandas as pd
import os

def import_semantic_catalog():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    datasets_path = os.path.join(base_dir, "semantic_catalog", "datasets.json")
    csv_path = os.path.join(base_dir, "semantic_catalog_export.csv")

    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return
    
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    try:
        with open(datasets_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    updated_count = 0
    
    # Create lookup map from CSV
    updates = {}
    for _, row in df.iterrows():
        key = (row['dataset_id'], row['column_name'])
        new_meaning = str(row.get('new_meaning(fill_here)', '')).strip()
        new_aliases_str = str(row.get('new_aliases(fill_here)', '')).strip()
        
        if new_meaning == 'nan': new_meaning = ''
        if new_aliases_str == 'nan': new_aliases_str = ''

        if new_meaning or new_aliases_str:
            updates[key] = {
                'meaning': new_meaning,
                'aliases': [x.strip() for x in new_aliases_str.split(',') if x.strip()] if new_aliases_str else None
            }

    # Apply updates to JSON structure
    for dataset in data.get("datasets", []):
        ds_id = dataset.get("id")
        
        for section in ["core_dimensions", "time_columns"]:
            for col in dataset.get(section, []):
                col_name = col.get("name")
                key = (ds_id, col_name)
                
                if key in updates:
                    change = updates[key]
                    modified = False
                    
                    if change['meaning']:
                        col['meaning'] = change['meaning']
                        modified = True
                        print(f"Updated meaning for {ds_id}.{col_name}")
                        
                    if change['aliases']:
                        current = set(col.get("aliases", []))
                        new_set = set(change['aliases'])
                        if not new_set.issubset(current):
                            # Append new aliases, don't overwrite existing ones unless you want to replace
                            # Strategy: Merge and unique
                            merged = list(current.union(new_set))
                            col['aliases'] = merged
                            modified = True
                            print(f"Updated aliases for {ds_id}.{col_name}: {merged}")
                    
                    if modified:
                        updated_count += 1

    if updated_count > 0:
        # Backup original
        import shutil
        backup_path = datasets_path + ".bak"
        shutil.copy(datasets_path, backup_path)
        print(f"Backed up original JSON to {backup_path}")

        # Save new JSON
        with open(datasets_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved {updated_count} updates to {datasets_path}")
    else:
        print("No changes found in CSV to import.")

if __name__ == "__main__":
    import_semantic_catalog()
