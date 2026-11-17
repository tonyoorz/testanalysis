"""
Optimized History Data Processor
Provides efficient indexing and time-series analysis for defect history and MR data
"""

import os
import json
import sqlite3
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np


class OptimizedHistoryProcessor:
    """Optimized processor for defect history with time-series analysis"""
    
    def __init__(self, db_path: str = "database/history_index.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database with optimized schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create indexed history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                defect_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                field_name TEXT,
                old_value TEXT,
                new_value TEXT,
                user_name TEXT,
                action TEXT,
                event_type TEXT
            )
        """)
        
        # Create indexes for fast queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_defect_id ON history_events(defect_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON history_events(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_field_name ON history_events(field_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_defect_time ON history_events(defect_id, timestamp)")
        
        # Create aggregated metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS defect_metrics (
                defect_id TEXT PRIMARY KEY,
                total_updates INTEGER,
                unique_users INTEGER,
                first_update TEXT,
                last_update TEXT,
                avg_response_time_hours REAL,
                status_changes INTEGER,
                ecu_transfers INTEGER,
                solution_cluster_changes INTEGER,
                comment_count INTEGER,
                attachment_count INTEGER,
                metrics_json TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def index_history_files(self, history_dir: str = "history", force_reindex: bool = False):
        """Index all history JSON files into database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if force_reindex:
            cursor.execute("DELETE FROM history_events")
            cursor.execute("DELETE FROM defect_metrics")
        
        history_files = [f for f in os.listdir(history_dir) if f.endswith('_history.json')]
        print(f"Indexing {len(history_files)} history files...")
        
        indexed_count = 0
        for filename in history_files:
            defect_id = filename.replace('_history.json', '')
            
            # Check if already indexed
            if not force_reindex:
                cursor.execute("SELECT COUNT(*) FROM history_events WHERE defect_id = ?", (defect_id,))
                if cursor.fetchone()[0] > 0:
                    continue
            
            filepath = os.path.join(history_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                
                self._index_single_history(cursor, defect_id, history_data)
                indexed_count += 1
                
                if indexed_count % 100 == 0:
                    conn.commit()
                    print(f"Indexed {indexed_count} files...")
                    
            except Exception as e:
                print(f"Error indexing {filename}: {e}")
        
        conn.commit()
        conn.close()
        print(f"Indexing complete: {indexed_count} files indexed")
    
    def _index_single_history(self, cursor, defect_id: str, history_data: Dict):
        """Index a single history file"""
        if not history_data or 'data' not in history_data:
            return
        
        events = []
        metrics = {
            'users': set(),
            'status_changes': 0,
            'ecu_transfers': 0,
            'solution_cluster_changes': 0,
            'comments': 0,
            'attachments': 0,
            'timestamps': []
        }
        
        for entry in history_data['data']:
            timestamp = entry.get('timestamp', '')
            user_name = entry.get('user_name', '')
            action = entry.get('action', '')
            
            metrics['users'].add(user_name)
            metrics['timestamps'].append(timestamp)
            
            if 'change_set' in entry:
                for change in entry['change_set']:
                    field_name = change.get('field_name', '')
                    old_value = change.get('old_value_text', '')
                    new_value = change.get('value_text', '')
                    
                    # Track specific field changes
                    if field_name == 'phase':
                        metrics['status_changes'] += 1
                    elif field_name == 'assigned_ecu_udf':
                        metrics['ecu_transfers'] += 1
                    elif field_name == 'solution_cluster_udf':
                        metrics['solution_cluster_changes'] += 1
                    elif field_name == 'comments':
                        metrics['comments'] += 1
                    elif field_name == 'attachments':
                        metrics['attachments'] += 1
                    
                    events.append((
                        defect_id,
                        timestamp,
                        field_name,
                        old_value,
                        new_value,
                        user_name,
                        action,
                        'field_change'
                    ))
        
        # Insert events
        cursor.executemany("""
            INSERT INTO history_events 
            (defect_id, timestamp, field_name, old_value, new_value, user_name, action, event_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, events)
        
        # Calculate metrics
        if metrics['timestamps']:
            metrics['timestamps'].sort()
            first_update = metrics['timestamps'][0]
            last_update = metrics['timestamps'][-1]
            
            # Calculate average response time
            response_times = []
            for i in range(1, len(metrics['timestamps'])):
                try:
                    t1 = datetime.fromisoformat(metrics['timestamps'][i-1].replace('Z', '+00:00'))
                    t2 = datetime.fromisoformat(metrics['timestamps'][i].replace('Z', '+00:00'))
                    response_times.append((t2 - t1).total_seconds() / 3600)
                except:
                    pass
            
            avg_response_time = np.mean(response_times) if response_times else 0
        else:
            first_update = last_update = None
            avg_response_time = 0
        
        # Insert metrics
        cursor.execute("""
            INSERT OR REPLACE INTO defect_metrics
            (defect_id, total_updates, unique_users, first_update, last_update, 
             avg_response_time_hours, status_changes, ecu_transfers, 
             solution_cluster_changes, comment_count, attachment_count, metrics_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            defect_id,
            len(events),
            len(metrics['users']),
            first_update,
            last_update,
            avg_response_time,
            metrics['status_changes'],
            metrics['ecu_transfers'],
            metrics['solution_cluster_changes'],
            metrics['comments'],
            metrics['attachments'],
            json.dumps(metrics['timestamps'])
        ))
    
    def get_defect_timeline(self, defect_id: str) -> pd.DataFrame:
        """Get complete timeline for a defect"""
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT timestamp, field_name, old_value, new_value, user_name, action
            FROM history_events
            WHERE defect_id = ?
            ORDER BY timestamp
        """
        df = pd.read_sql_query(query, conn, params=(defect_id,))
        conn.close()
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    
    def get_field_change_history(self, defect_id: str, field_name: str) -> List[Dict]:
        """Get change history for a specific field"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, old_value, new_value, user_name
            FROM history_events
            WHERE defect_id = ? AND field_name = ?
            ORDER BY timestamp
        """, (defect_id, field_name))
        
        changes = []
        for row in cursor.fetchall():
            changes.append({
                'timestamp': row[0],
                'old_value': row[1],
                'new_value': row[2],
                'user_name': row[3]
            })
        
        conn.close()
        return changes
    
    def get_batch_metrics(self, defect_ids: List[str]) -> pd.DataFrame:
        """Get metrics for multiple defects efficiently"""
        conn = sqlite3.connect(self.db_path)
        
        placeholders = ','.join('?' * len(defect_ids))
        query = f"""
            SELECT * FROM defect_metrics
            WHERE defect_id IN ({placeholders})
        """
        
        df = pd.read_sql_query(query, conn, params=defect_ids)
        conn.close()
        
        return df
    
    def analyze_activity_patterns(self, defect_ids: List[str]) -> Dict:
        """Analyze activity patterns across defects"""
        conn = sqlite3.connect(self.db_path)
        
        placeholders = ','.join('?' * len(defect_ids))
        query = f"""
            SELECT 
                strftime('%H', timestamp) as hour,
                strftime('%w', timestamp) as weekday,
                COUNT(*) as activity_count
            FROM history_events
            WHERE defect_id IN ({placeholders})
            GROUP BY hour, weekday
        """
        
        df = pd.read_sql_query(query, conn, params=defect_ids)
        conn.close()
        
        return {
            'hourly_distribution': df.groupby('hour')['activity_count'].sum().to_dict(),
            'weekday_distribution': df.groupby('weekday')['activity_count'].sum().to_dict()
        }
    
    def get_ai_context_summary(self, defect_ids: List[str], max_defects: int = 100) -> str:
        """Generate AI-friendly context summary with time-series insights"""
        if len(defect_ids) > max_defects:
            defect_ids = defect_ids[:max_defects]
        
        metrics_df = self.get_batch_metrics(defect_ids)
        
        if metrics_df.empty:
            return "No history data available for the selected defects."
        
        # Calculate aggregate statistics
        summary_lines = [
            "=== Defect History Analysis ===",
            f"Total defects analyzed: {len(metrics_df)}",
            "",
            "Activity Metrics:",
            f"- Average updates per defect: {metrics_df['total_updates'].mean():.1f}",
            f"- Average unique users: {metrics_df['unique_users'].mean():.1f}",
            f"- Average response time: {metrics_df['avg_response_time_hours'].mean():.1f} hours",
            "",
            "Change Patterns:",
            f"- Total status changes: {metrics_df['status_changes'].sum()}",
            f"- Total ECU transfers: {metrics_df['ecu_transfers'].sum()}",
            f"- Total solution cluster changes: {metrics_df['solution_cluster_changes'].sum()}",
            f"- Total comments: {metrics_df['comment_count'].sum()}",
            "",
            "High Activity Defects (Top 5):",
        ]
        
        top_active = metrics_df.nlargest(5, 'total_updates')
        for _, row in top_active.iterrows():
            summary_lines.append(
                f"- Defect #{row['defect_id']}: {int(row['total_updates'])} updates, "
                f"{int(row['unique_users'])} users, {int(row['status_changes'])} status changes"
            )
        
        return "\n".join(summary_lines)


class MRDataProcessor:
    """Processor for Manual Run (MR) data with defect correlation"""
    
    def __init__(self, mr_dir: str = "mr"):
        self.mr_dir = mr_dir
    
    def load_all_mr_data(self) -> pd.DataFrame:
        """Load all MR JSON files into a DataFrame"""
        all_runs = []
        
        mr_files = [f for f in os.listdir(self.mr_dir) if f.endswith('.json')]
        
        for filename in mr_files:
            filepath = os.path.join(self.mr_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    for run in data:
                        run['source_file'] = filename
                        all_runs.append(run)
                elif isinstance(data, dict):
                    data['source_file'] = filename
                    all_runs.append(data)
                    
            except Exception as e:
                print(f"Error loading {filename}: {e}")
        
        if not all_runs:
            return pd.DataFrame()
        
        df = pd.DataFrame(all_runs)
        
        # Extract defect IDs from nested structure
        if 'defect' in df.columns:
            df['defect_count'] = df['defect'].apply(
                lambda x: x.get('total_count', 0) if isinstance(x, dict) else 0
            )
            df['defect_ids'] = df['defect'].apply(
                lambda x: [d.get('id') for d in x.get('data', [])] if isinstance(x, dict) else []
            )
        
        # Parse timestamps
        for col in ['started', 'finished_udf', 'last_modified', 'creation_time']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    
    def correlate_with_defects(self, mr_df: pd.DataFrame, defect_df: pd.DataFrame) -> pd.DataFrame:
        """Correlate MR data with defect data"""
        # Expand defect_ids into separate rows
        mr_expanded = []
        
        for _, row in mr_df.iterrows():
            defect_ids = row.get('defect_ids', [])
            if defect_ids:
                for defect_id in defect_ids:
                    row_copy = row.copy()
                    row_copy['linked_defect_id'] = defect_id
                    mr_expanded.append(row_copy)
            else:
                row_copy = row.copy()
                row_copy['linked_defect_id'] = None
                mr_expanded.append(row_copy)
        
        mr_expanded_df = pd.DataFrame(mr_expanded)
        
        # Merge with defect data
        if 'linked_defect_id' in mr_expanded_df.columns and 'id' in defect_df.columns:
            merged = mr_expanded_df.merge(
                defect_df,
                left_on='linked_defect_id',
                right_on='id',
                how='left',
                suffixes=('_mr', '_defect')
            )
            return merged
        
        return mr_expanded_df
    
    def get_test_efficiency_metrics(self, mr_df: pd.DataFrame) -> Dict:
        """Calculate test execution efficiency metrics"""
        if mr_df.empty:
            return {}
        
        metrics = {
            'total_runs': len(mr_df),
            'completed_runs': mr_df['is_completed'].sum() if 'is_completed' in mr_df.columns else 0,
            'defects_found': mr_df['defect_count'].sum() if 'defect_count' in mr_df.columns else 0,
        }
        
        # Calculate execution time
        if 'started' in mr_df.columns and 'finished_udf' in mr_df.columns:
            mr_df['execution_time'] = (mr_df['finished_udf'] - mr_df['started']).dt.total_seconds() / 60
            metrics['avg_execution_time_minutes'] = mr_df['execution_time'].mean()
            metrics['total_execution_time_hours'] = mr_df['execution_time'].sum() / 60
        
        # Defect detection rate
        if 'defect_count' in mr_df.columns:
            metrics['defect_detection_rate'] = (mr_df['defect_count'] > 0).sum() / len(mr_df) * 100
        
        return metrics


# Example usage
if __name__ == "__main__":
    print("=== Optimized History Processor Test ===\n")
    
    # Initialize processor
    processor = OptimizedHistoryProcessor()
    
    # Index history files (only needs to be done once or when data changes)
    print("Step 1: Indexing history files...")
    processor.index_history_files(force_reindex=False)
    
    # Get timeline for a specific defect
    print("\nStep 2: Getting defect timeline...")
    timeline = processor.get_defect_timeline("2111678")
    print(f"Timeline entries: {len(timeline)}")
    if not timeline.empty:
        print(timeline.head())
    
    # Get batch metrics
    print("\nStep 3: Getting batch metrics...")
    sample_ids = ["2111678", "2111679", "2111680"]
    metrics = processor.get_batch_metrics(sample_ids)
    print(metrics)
    
    # Generate AI context
    print("\nStep 4: Generating AI context...")
    context = processor.get_ai_context_summary(sample_ids)
    print(context)
    
    # Test MR processor
    print("\n=== MR Data Processor Test ===\n")
    mr_processor = MRDataProcessor()
    mr_df = mr_processor.load_all_mr_data()
    print(f"Loaded {len(mr_df)} MR records")
    
    if not mr_df.empty:
        efficiency = mr_processor.get_test_efficiency_metrics(mr_df)
        print("\nTest Efficiency Metrics:")
        for key, value in efficiency.items():
            print(f"- {key}: {value}")
