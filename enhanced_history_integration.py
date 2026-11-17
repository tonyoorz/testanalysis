"""
Enhanced History Integration for AI Chat Manager
Demonstrates how to integrate optimized history processing with AI analysis
"""

import pandas as pd
from typing import Dict, List, Optional, Any
from optimized_history_processor import OptimizedHistoryProcessor, MRDataProcessor


class EnhancedHistoryAnalyzer:
    """Enhanced analyzer that combines defect data, history, and MR data for AI"""
    
    def __init__(self, 
                 history_db_path: str = "database/history_index.db",
                 mr_dir: str = "mr"):
        self.history_processor = OptimizedHistoryProcessor(db_path=history_db_path)
        self.mr_processor = MRDataProcessor(mr_dir=mr_dir)
        
    def enrich_defect_data_with_history(self, defect_df: pd.DataFrame) -> pd.DataFrame:
        """Enrich defect DataFrame with history metrics"""
        if defect_df.empty or 'id' not in defect_df.columns:
            return defect_df
        
        defect_ids = defect_df['id'].astype(str).tolist()
        
        # Get batch metrics from indexed history
        history_metrics = self.history_processor.get_batch_metrics(defect_ids)
        
        if history_metrics.empty:
            return defect_df
        
        # Merge with defect data
        enriched = defect_df.merge(
            history_metrics,
            left_on='id',
            right_on='defect_id',
            how='left',
            suffixes=('', '_history')
        )
        
        # Add derived features
        enriched['is_high_activity'] = enriched['total_updates'] > enriched['total_updates'].quantile(0.75)
        enriched['is_slow_response'] = enriched['avg_response_time_hours'] > enriched['avg_response_time_hours'].quantile(0.75)
        enriched['is_complex'] = (enriched['ecu_transfers'] > 2) | (enriched['solution_cluster_changes'] > 2)
        
        return enriched
    
    def generate_ai_context_with_history(self, 
                                         defect_df: pd.DataFrame,
                                         question: str = "",
                                         include_mr: bool = False) -> str:
        """Generate comprehensive AI context including history insights"""
        
        context_parts = []
        
        # 1. Basic defect statistics
        context_parts.append("=== Defect Data Overview ===")
        context_parts.append(f"Total defects: {len(defect_df)}")
        
        if 'severity_group' in defect_df.columns:
            severity_dist = defect_df['severity_group'].value_counts().to_dict()
            context_parts.append(f"Severity distribution: {severity_dist}")
        
        if 'status_phase' in defect_df.columns:
            status_dist = defect_df['status_phase'].value_counts().head(5).to_dict()
            context_parts.append(f"Top 5 status phases: {status_dist}")
        
        context_parts.append("")
        
        # 2. History-based insights
        if 'id' in defect_df.columns:
            defect_ids = defect_df['id'].astype(str).tolist()
            history_summary = self.history_processor.get_ai_context_summary(defect_ids, max_defects=100)
            context_parts.append(history_summary)
            context_parts.append("")
        
        # 3. Activity patterns
        if 'total_updates' in defect_df.columns:
            context_parts.append("=== Activity Analysis ===")
            
            high_activity = defect_df[defect_df.get('is_high_activity', False)]
            if not high_activity.empty:
                context_parts.append(f"High activity defects: {len(high_activity)} ({len(high_activity)/len(defect_df)*100:.1f}%)")
            
            slow_response = defect_df[defect_df.get('is_slow_response', False)]
            if not slow_response.empty:
                context_parts.append(f"Slow response defects: {len(slow_response)} ({len(slow_response)/len(defect_df)*100:.1f}%)")
            
            complex_defects = defect_df[defect_df.get('is_complex', False)]
            if not complex_defects.empty:
                context_parts.append(f"Complex defects (multiple transfers): {len(complex_defects)} ({len(complex_defects)/len(defect_df)*100:.1f}%)")
            
            context_parts.append("")
        
        # 4. ECU and Solution Cluster transfer patterns
        if 'ecu_transfers' in defect_df.columns:
            context_parts.append("=== Transfer Patterns ===")
            
            total_ecu_transfers = defect_df['ecu_transfers'].sum()
            avg_ecu_transfers = defect_df['ecu_transfers'].mean()
            context_parts.append(f"Total ECU transfers: {int(total_ecu_transfers)}")
            context_parts.append(f"Average ECU transfers per defect: {avg_ecu_transfers:.2f}")
            
            if 'solution_cluster_changes' in defect_df.columns:
                total_sc_changes = defect_df['solution_cluster_changes'].sum()
                avg_sc_changes = defect_df['solution_cluster_changes'].mean()
                context_parts.append(f"Total Solution Cluster changes: {int(total_sc_changes)}")
                context_parts.append(f"Average SC changes per defect: {avg_sc_changes:.2f}")
            
            # Identify defects with excessive transfers (potential ping-pong issues)
            excessive_transfers = defect_df[defect_df['ecu_transfers'] > 3]
            if not excessive_transfers.empty:
                context_parts.append(f"\n⚠️ Warning: {len(excessive_transfers)} defects with >3 ECU transfers (potential ownership issues)")
                if 'id' in excessive_transfers.columns:
                    sample_ids = excessive_transfers['id'].head(3).tolist()
                    context_parts.append(f"   Sample IDs: {sample_ids}")
            
            context_parts.append("")
        
        # 5. MR data correlation (if requested)
        if include_mr:
            mr_df = self.mr_processor.load_all_mr_data()
            if not mr_df.empty:
                context_parts.append("=== Test Execution Data (MR) ===")
                
                efficiency = self.mr_processor.get_test_efficiency_metrics(mr_df)
                for key, value in efficiency.items():
                    if isinstance(value, float):
                        context_parts.append(f"- {key}: {value:.2f}")
                    else:
                        context_parts.append(f"- {key}: {value}")
                
                # Correlate with defects
                if 'id' in defect_df.columns:
                    correlated = self.mr_processor.correlate_with_defects(mr_df, defect_df)
                    if not correlated.empty and 'linked_defect_id' in correlated.columns:
                        linked_count = correlated['linked_defect_id'].notna().sum()
                        context_parts.append(f"- MR runs linked to defects: {linked_count}")
                
                context_parts.append("")
        
        # 6. Question-specific insights
        if question:
            context_parts.append("=== Question Context ===")
            context_parts.append(f"User question: {question}")
            
            # Detect question intent and provide relevant data
            question_lower = question.lower()
            
            if any(keyword in question_lower for keyword in ['trend', '趋势', 'over time', '随时间']):
                context_parts.append("\n📊 Time-series data available in history metrics")
                if 'first_update' in defect_df.columns and 'last_update' in defect_df.columns:
                    context_parts.append("   - Use 'first_update' and 'last_update' for temporal analysis")
            
            if any(keyword in question_lower for keyword in ['transfer', '流转', 'ecu', 'ownership']):
                context_parts.append("\n🔄 Transfer pattern data available")
                if 'ecu_transfers' in defect_df.columns:
                    high_transfer = defect_df[defect_df['ecu_transfers'] > 2]
                    context_parts.append(f"   - {len(high_transfer)} defects with multiple ECU transfers")
            
            if any(keyword in question_lower for keyword in ['response', '响应', 'speed', '速度']):
                context_parts.append("\n⏱️ Response time metrics available")
                if 'avg_response_time_hours' in defect_df.columns:
                    avg_response = defect_df['avg_response_time_hours'].mean()
                    context_parts.append(f"   - Average response time: {avg_response:.1f} hours")
            
            if any(keyword in question_lower for keyword in ['test', '测试', 'mr', 'execution']):
                context_parts.append("\n🧪 Test execution data available (use include_mr=True for details)")
            
            context_parts.append("")
        
        # 7. Data quality notes
        context_parts.append("=== Data Quality Notes ===")
        
        if 'total_updates' in defect_df.columns:
            no_history = defect_df[defect_df['total_updates'].isna() | (defect_df['total_updates'] == 0)]
            if not no_history.empty:
                context_parts.append(f"⚠️ {len(no_history)} defects have no history data")
        
        if 'avg_response_time_hours' in defect_df.columns:
            zero_response = defect_df[defect_df['avg_response_time_hours'] == 0]
            if not zero_response.empty:
                context_parts.append(f"ℹ️ {len(zero_response)} defects have zero response time (single update)")
        
        return "\n".join(context_parts)
    
    def get_detailed_defect_story(self, defect_id: str, defect_df: pd.DataFrame) -> str:
        """Generate a narrative story for a specific defect including history"""
        
        # Get defect basic info
        defect_row = defect_df[defect_df['id'].astype(str) == str(defect_id)]
        if defect_row.empty:
            return f"Defect #{defect_id} not found in current dataset."
        
        defect_info = defect_row.iloc[0]
        
        story_parts = []
        story_parts.append(f"=== Defect #{defect_id} Story ===\n")
        
        # Basic info
        if 'name' in defect_info:
            story_parts.append(f"Title: {defect_info['name']}")
        if 'severity_group' in defect_info:
            story_parts.append(f"Severity: {defect_info['severity_group']}")
        if 'status_phase' in defect_info:
            story_parts.append(f"Current Status: {defect_info['status_phase']}")
        
        story_parts.append("")
        
        # Timeline
        timeline = self.history_processor.get_defect_timeline(defect_id)
        if not timeline.empty:
            story_parts.append(f"📅 Timeline ({len(timeline)} events):")
            
            # Key milestones
            status_changes = timeline[timeline['field_name'] == 'phase']
            if not status_changes.empty:
                story_parts.append(f"\nStatus Changes ({len(status_changes)}):")
                for _, event in status_changes.iterrows():
                    story_parts.append(
                        f"  {event['timestamp'].strftime('%Y-%m-%d %H:%M')} - "
                        f"{event['old_value']} → {event['new_value']} "
                        f"(by {event['user_name']})"
                    )
            
            # ECU transfers
            ecu_changes = timeline[timeline['field_name'] == 'assigned_ecu_udf']
            if not ecu_changes.empty:
                story_parts.append(f"\nECU Transfers ({len(ecu_changes)}):")
                for _, event in ecu_changes.iterrows():
                    story_parts.append(
                        f"  {event['timestamp'].strftime('%Y-%m-%d %H:%M')} - "
                        f"{event['old_value']} → {event['new_value']}"
                    )
            
            # Solution Cluster changes
            sc_changes = timeline[timeline['field_name'] == 'solution_cluster_udf']
            if not sc_changes.empty:
                story_parts.append(f"\nSolution Cluster Changes ({len(sc_changes)}):")
                for _, event in sc_changes.iterrows():
                    story_parts.append(
                        f"  {event['timestamp'].strftime('%Y-%m-%d %H:%M')} - "
                        f"{event['old_value']} → {event['new_value']}"
                    )
            
            # Activity summary
            story_parts.append(f"\nActivity Summary:")
            unique_users = timeline['user_name'].nunique()
            story_parts.append(f"  - Unique contributors: {unique_users}")
            
            time_span = (timeline['timestamp'].max() - timeline['timestamp'].min()).days
            story_parts.append(f"  - Active period: {time_span} days")
            
            # Identify potential issues
            story_parts.append("\n🔍 Insights:")
            
            if len(ecu_changes) > 3:
                story_parts.append("  ⚠️ Multiple ECU transfers detected - possible ownership confusion")
            
            if len(status_changes) > 5:
                story_parts.append("  ⚠️ Frequent status changes - possible back-and-forth issues")
            
            if time_span > 90:
                story_parts.append("  ⚠️ Long-running defect (>90 days) - consider escalation")
            
            if unique_users > 5:
                story_parts.append("  ℹ️ Multiple contributors - collaborative effort or handoff issues?")
        
        else:
            story_parts.append("⚠️ No history data available for this defect")
        
        return "\n".join(story_parts)
    
    def compare_defect_groups(self, 
                             defect_df: pd.DataFrame,
                             group_by: str = 'project') -> Dict[str, Any]:
        """Compare different groups of defects based on history metrics"""
        
        if group_by not in defect_df.columns:
            return {"error": f"Column '{group_by}' not found in data"}
        
        # Ensure history metrics are available
        if 'total_updates' not in defect_df.columns:
            defect_df = self.enrich_defect_data_with_history(defect_df)
        
        comparison = {}
        
        for group_name, group_df in defect_df.groupby(group_by):
            if len(group_df) < 3:  # Skip small groups
                continue
            
            comparison[group_name] = {
                'count': len(group_df),
                'avg_updates': group_df['total_updates'].mean() if 'total_updates' in group_df.columns else 0,
                'avg_response_time': group_df['avg_response_time_hours'].mean() if 'avg_response_time_hours' in group_df.columns else 0,
                'avg_ecu_transfers': group_df['ecu_transfers'].mean() if 'ecu_transfers' in group_df.columns else 0,
                'high_activity_rate': (group_df.get('is_high_activity', False).sum() / len(group_df) * 100) if 'is_high_activity' in group_df.columns else 0,
                'complex_rate': (group_df.get('is_complex', False).sum() / len(group_df) * 100) if 'is_complex' in group_df.columns else 0,
            }
        
        # Rank groups
        if comparison:
            # Find best and worst performers
            sorted_by_response = sorted(comparison.items(), key=lambda x: x[1]['avg_response_time'])
            comparison['_insights'] = {
                'fastest_response': sorted_by_response[0][0] if sorted_by_response else None,
                'slowest_response': sorted_by_response[-1][0] if sorted_by_response else None,
            }
            
            sorted_by_complexity = sorted(comparison.items(), key=lambda x: x[1]['complex_rate'], reverse=True)
            comparison['_insights']['most_complex'] = sorted_by_complexity[0][0] if sorted_by_complexity else None
        
        return comparison


# Integration example for enhanced_ai_chat_manager.py
def integrate_with_chat_manager():
    """
    Example of how to integrate this with enhanced_ai_chat_manager.py
    
    Add this to EnhancedAIChatManager class:
    
    def __init__(self, ...):
        ...
        # Add history analyzer
        self.history_analyzer = EnhancedHistoryAnalyzer()
    
    def _generate_data_context(self, data, question="", intents=None):
        # Convert data to DataFrame
        if isinstance(data, pd.DataFrame):
            df = data
        else:
            df = self._convert_to_dataframe(data)
        
        # Enrich with history
        enriched_df = self.history_analyzer.enrich_defect_data_with_history(df)
        
        # Generate comprehensive context
        context = self.history_analyzer.generate_ai_context_with_history(
            enriched_df,
            question=question,
            include_mr=('test' in question.lower() or 'mr' in question.lower())
        )
        
        return context
    """
    pass


if __name__ == "__main__":
    print("=== Enhanced History Integration Test ===\n")
    
    # Initialize analyzer
    analyzer = EnhancedHistoryAnalyzer()
    
    # Test with sample data
    from data_processor import load_defect_data
    
    print("Loading defect data...")
    defect_df = load_defect_data()
    
    if not defect_df.empty:
        print(f"Loaded {len(defect_df)} defects\n")
        
        # Enrich with history
        print("Enriching with history metrics...")
        enriched_df = analyzer.enrich_defect_data_with_history(defect_df)
        print(f"Added history metrics for {enriched_df['total_updates'].notna().sum()} defects\n")
        
        # Generate AI context
        print("Generating AI context...")
        context = analyzer.generate_ai_context_with_history(
            enriched_df,
            question="What are the trends in defect resolution?",
            include_mr=False
        )
        print(context)
        print("\n" + "="*60 + "\n")
        
        # Get detailed story for first defect
        if 'id' in enriched_df.columns:
            first_id = enriched_df['id'].iloc[0]
            print(f"Getting detailed story for defect #{first_id}...")
            story = analyzer.get_detailed_defect_story(str(first_id), enriched_df)
            print(story)
            print("\n" + "="*60 + "\n")
        
        # Compare groups
        if 'project' in enriched_df.columns:
            print("Comparing projects...")
            comparison = analyzer.compare_defect_groups(enriched_df, group_by='project')
            
            print("\nProject Comparison:")
            for project, metrics in comparison.items():
                if project != '_insights':
                    print(f"\n{project}:")
                    for key, value in metrics.items():
                        if isinstance(value, float):
                            print(f"  - {key}: {value:.2f}")
                        else:
                            print(f"  - {key}: {value}")
            
            if '_insights' in comparison:
                print("\n🏆 Key Insights:")
                insights = comparison['_insights']
                print(f"  - Fastest response: {insights.get('fastest_response')}")
                print(f"  - Slowest response: {insights.get('slowest_response')}")
                print(f"  - Most complex: {insights.get('most_complex')}")
    
    else:
        print("No defect data available for testing")
