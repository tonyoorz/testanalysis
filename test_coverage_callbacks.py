# Test Coverage Analysis 回调函数模块
import gc
import pandas as pd
from dash import callback_context, html
from dash.dependencies import Input, Output, State
from test_coverage_components import (
    create_project_status_chart, 
    create_fvp_coverage_chart, 
    create_testcase_detail_chart,
    create_enhanced_status_distribution_pie,
    create_pass_rate_trend_chart, 
    create_test_aida_wordcloud,
    filter_test_data
)
from data_processor import create_empty_figure

def register_test_coverage_callbacks(app, prefix="de-tc"):
    """注册测试覆盖率分析的回调函数"""
    
    # 主图表更新回调
    @app.callback(
        [Output(f'{prefix}-project-status-chart', 'figure'),
         Output(f'{prefix}-fvp-coverage-chart', 'figure'),
         Output(f'{prefix}-testcase-detail-chart', 'figure'),
         Output(f'{prefix}-fv-dropdown', 'value'),
         Output(f'{prefix}-aida-dropdown', 'value'),
         Output(f'{prefix}-chart3-filtered-store', 'data')],
        [Input(f'{prefix}-project-dropdown', 'value'),
         Input(f'{prefix}-testweek-dropdown', 'value'),
         Input(f'{prefix}-pu-dropdown', 'value'),
         Input(f'{prefix}-aida-dropdown', 'value'),
         Input(f'{prefix}-status-dropdown', 'value'),
         Input(f'{prefix}-feature-region-dropdown', 'value'),
         Input(f'{prefix}-fvp-dropdown', 'value'),
         Input(f'{prefix}-fv-dropdown', 'value'),
         Input(f'{prefix}-project-status-chart', 'clickData'),
         Input(f'{prefix}-fvp-coverage-chart', 'clickData'),
         Input(f'{prefix}-testcase-detail-chart', 'clickData'),
         Input(f'{prefix}-data-store', 'data')],
        [State(f'{prefix}-fv-dropdown', 'value'),
         State(f'{prefix}-aida-dropdown', 'value')],
        prevent_initial_call=False
    )
    def update_test_coverage_charts(selected_projects, selected_testweeks, selected_pus,
                                   selected_aidas_input, selected_statuses, selected_feature_regions, 
                                   selected_fvps, selected_fvs_input,
                                   click_data_fv, click_data_aida, click_data_test, 
                                   stored_data,
                                   fv_state, aida_state):
        
        print(f"--- 测试覆盖率回调触发: {callback_context.triggered_id if callback_context.triggered else 'Initial load'} ---")
        ctx = callback_context
        
        # 加载数据
        if not stored_data:
            print("警告: 数据存储为空")
            empty_fig = create_empty_figure("数据加载失败")
            return empty_fig, empty_fig, empty_fig, [], []
        
        try:
            tdf = pd.DataFrame(stored_data)
            print(f"数据加载成功: {len(tdf)} 行")
            
            # 内存管理
            gc.collect()
            working_tdf = tdf.copy()
            print(f"数据处理开始，共 {len(working_tdf)} 行")
            
            # 处理AIDA筛选
            def is_filter_active(filter_value):
                return filter_value and len(filter_value) > 0 and 'all' not in filter_value
            
            # 处理点击事件和筛选逻辑
            output_fvs = list(fv_state) if fv_state else ['all']
            output_aidas = list(aida_state) if aida_state else ['all']
            
            if ctx.triggered:
                triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
                
                # 处理图表点击事件
                if 'project-status-chart' in triggered_id and click_data_fv:
                    if 'points' in click_data_fv and click_data_fv['points']:
                        clicked_fv = click_data_fv['points'][0].get('y', '')
                        if clicked_fv and clicked_fv != output_fvs:
                            output_fvs = [clicked_fv] if clicked_fv != 'all' else ['all']
                            print(f"FV图表点击: {clicked_fv}")
                
                elif 'fvp-coverage-chart' in triggered_id and click_data_aida:
                    if 'points' in click_data_aida and click_data_aida['points']:
                        clicked_aida = click_data_aida['points'][0].get('y', '')
                        if clicked_aida and clicked_aida != output_aidas:
                            output_aidas = [clicked_aida] if clicked_aida != 'all' else ['all']
                            print(f"AIDA图表点击: {clicked_aida}")
                
                elif 'aida-dropdown' in triggered_id:
                    output_aidas = selected_aidas_input if selected_aidas_input else ['all']
                
                elif 'fv-dropdown' in triggered_id:
                    output_fvs = selected_fvs_input if selected_fvs_input else ['all']
            
            print(f"应用筛选: fvs={output_fvs}, aidas={output_aidas}")
            filtered_tdf = working_tdf.copy()
            
            # 应用筛选条件
            if is_filter_active(selected_projects):
                filtered_tdf = filtered_tdf[filtered_tdf['project'].isin(selected_projects)]
            if is_filter_active(selected_testweeks):
                filtered_tdf = filtered_tdf[filtered_tdf['test_week'].isin(selected_testweeks)]
            if is_filter_active(selected_pus):
                filtered_tdf = filtered_tdf[filtered_tdf['pu'].isin(selected_pus)]
            if is_filter_active(output_aidas):
                if 'top_aida' in filtered_tdf.columns:
                    filtered_tdf = filtered_tdf[filtered_tdf['top_aida'].isin(output_aidas)]
            if is_filter_active(selected_feature_regions):
                if 'feature_region' in filtered_tdf.columns:
                    filtered_tdf = filtered_tdf[filtered_tdf['feature_region'].isin(selected_feature_regions)]
                    print(f"应用Feature Region筛选: {selected_feature_regions}, 结果行数: {len(filtered_tdf)}")
            if is_filter_active(selected_fvps):
                filtered_tdf = filtered_tdf[filtered_tdf['fvp'].isin(selected_fvps)]
            if is_filter_active(output_fvs):
                filtered_tdf = filtered_tdf[filtered_tdf['fv'].isin(output_fvs)]
            
            # 状态筛选
            if is_filter_active(selected_statuses):
                if 'native_status' in filtered_tdf.columns:
                    def extract_status_name(x):
                        if isinstance(x, dict) and 'name' in x:
                            return x['name']
                        elif isinstance(x, str):
                            return x
                        else:
                            return None
                    status_names = filtered_tdf['native_status'].apply(extract_status_name)
                    filtered_tdf = filtered_tdf[status_names.isin(selected_statuses)]
                else:
                    status_column = next((col for col in ['run_status', 'status', 'execution_status'] if col in filtered_tdf.columns), None)
                    if status_column:
                        filtered_tdf = filtered_tdf[filtered_tdf[status_column].isin(selected_statuses)]
            
            if filtered_tdf.empty:
                print("筛选后数据为空")
                empty_fig = create_empty_figure("筛选后无数据")
                return empty_fig, empty_fig, empty_fig, output_fvs, output_aidas, []
            
            print(f"筛选后数据: {len(filtered_tdf)} 行")
            
            # 判断是否有活跃的筛选器（非默认值）
            has_active_filters = (
                is_filter_active(selected_projects) or
                is_filter_active(selected_testweeks) or
                is_filter_active(selected_pus) or
                is_filter_active(output_aidas) or
                is_filter_active(selected_feature_regions) or
                is_filter_active(selected_fvps) or
                is_filter_active(output_fvs) or
                is_filter_active(selected_statuses)
            )
            
            print(f"筛选器状态检查: has_active_filters = {has_active_filters}")
            
            # 创建图表
            try:
                fig1 = create_project_status_chart(filtered_tdf)
                fig2 = create_fvp_coverage_chart(filtered_tdf)
                fig3 = create_testcase_detail_chart(filtered_tdf, has_active_filters)
                
                print("--- 测试覆盖率回调完成 ---")
                export_store = []
                raw_cols = ['test_week', 'test_id', 'test_name', 'run_status', 'top_aida', 'fv', 'project', 'pu', 'tester']
                for col in raw_cols:
                    if col not in filtered_tdf.columns:
                        filtered_tdf[col] = ''
                export_store = filtered_tdf[raw_cols].to_dict('records')
                return fig1, fig2, fig3, output_fvs, output_aidas, export_store
                
            except Exception as e:
                print(f"创建图表失败: {e}")
                import traceback
                traceback.print_exc()
                error_fig = create_empty_figure(f"图表创建失败: {str(e)[:100]}")
                return error_fig, error_fig, error_fig, output_fvs, output_aidas, []
                
        except Exception as e:
            print(f"回调函数执行失败: {e}")
            import traceback
            traceback.print_exc()
            error_fig = create_empty_figure(f"数据处理失败: {str(e)[:100]}")
            return error_fig, error_fig, error_fig, [], [], []

    # Phase 1 新增图表的回调函数
    @app.callback(
        [Output(f'{prefix}-status-distribution-pie', 'figure'),
         Output(f'{prefix}-pass-rate-trend-chart', 'figure'),
         Output(f'{prefix}-aida-wordcloud', 'figure'),
         Output(f'{prefix}-kpi-indicators', 'children')],
        [Input(f'{prefix}-project-dropdown', 'value'),
         Input(f'{prefix}-testweek-dropdown', 'value'),
         Input(f'{prefix}-pu-dropdown', 'value'),
         Input(f'{prefix}-aida-dropdown', 'value'),
         Input(f'{prefix}-status-dropdown', 'value'),
         Input(f'{prefix}-feature-region-dropdown', 'value'),
         Input(f'{prefix}-fvp-dropdown', 'value'),
         Input(f'{prefix}-fv-dropdown', 'value'),
         Input(f'{prefix}-data-store', 'data')],
        prevent_initial_call=False
    )
    def update_phase1_charts(selected_projects, selected_testweeks, selected_pus,
                           selected_aidas, selected_statuses, selected_feature_regions, 
                           selected_fvps, selected_fvs, stored_data):
        
        try:
            print("--- Phase 1 图表更新 ---")
            
            if not stored_data:
                empty_fig = create_empty_figure("数据加载失败", height=400)
                empty_kpi = html.Div("数据加载失败", style={'textAlign': 'center', 'color': '#dc3545'})
                return empty_fig, empty_fig, empty_fig, empty_kpi
            
            # 使用与主回调相同的筛选逻辑
            def is_filter_active(filter_value):
                return filter_value and len(filter_value) > 0 and 'all' not in filter_value
            
            working_tdf = pd.DataFrame(stored_data)
            filtered_tdf = working_tdf.copy()
            
            # 应用筛选条件（与主回调保持一致）
            if is_filter_active(selected_projects):
                filtered_tdf = filtered_tdf[filtered_tdf['project'].isin(selected_projects)]
            if is_filter_active(selected_testweeks):
                filtered_tdf = filtered_tdf[filtered_tdf['test_week'].isin(selected_testweeks)]
            if is_filter_active(selected_pus):
                filtered_tdf = filtered_tdf[filtered_tdf['pu'].isin(selected_pus)]
            if is_filter_active(selected_aidas):
                filtered_tdf = filtered_tdf[filtered_tdf['top_aida'].isin(selected_aidas)]
            if is_filter_active(selected_feature_regions):
                if 'feature_region' in filtered_tdf.columns:
                    filtered_tdf = filtered_tdf[filtered_tdf['feature_region'].isin(selected_feature_regions)]
            if is_filter_active(selected_fvps):
                filtered_tdf = filtered_tdf[filtered_tdf['fvp'].isin(selected_fvps)]
            if is_filter_active(selected_fvs):
                filtered_tdf = filtered_tdf[filtered_tdf['fv'].isin(selected_fvs)]
            if is_filter_active(selected_statuses):
                # 状态筛选逻辑
                if 'native_status' in filtered_tdf.columns:
                    def extract_status_name(x):
                        if isinstance(x, dict) and 'name' in x:
                            return x['name']
                        elif isinstance(x, str):
                            return x
                        else:
                            return None
                    status_names = filtered_tdf['native_status'].apply(extract_status_name)
                    filtered_tdf = filtered_tdf[status_names.isin(selected_statuses)]
                else:
                    status_column = next((col for col in ['run_status', 'status', 'execution_status'] if col in filtered_tdf.columns), 'run_status')
                    if status_column in filtered_tdf.columns:
                        filtered_tdf = filtered_tdf[filtered_tdf[status_column].isin(selected_statuses)]
            
            print(f"Phase 1 筛选后数据: {len(filtered_tdf)} 行")
            
            # 计算KPI指标
            total_count = len(filtered_tdf)
            if total_count > 0:
                # 处理状态数据
                def extract_status_name(status):
                    if isinstance(status, dict) and 'name' in status:
                        return status['name'].lower()
                    return str(status).lower() if status is not None else 'unknown'
                
                # 优先使用native_status列
                status_column = None
                if 'native_status' in filtered_tdf.columns:
                    status_column = 'native_status'
                elif 'run_status' in filtered_tdf.columns:
                    status_column = 'run_status'
                
                if status_column:
                    status_names = filtered_tdf[status_column].apply(extract_status_name)
                    
                    passed_count = len(status_names[status_names == 'passed'])
                    blocked_count = len(status_names[status_names == 'blocked']) + len(status_names[status_names == 'requires attention'])
                    failed_count = len(status_names[status_names == 'failed'])
                    planned_count = len(status_names[status_names == 'planned'])
                    executed_count = total_count - planned_count
                    
                    print(f"状态统计: Passed={passed_count}, Blocked={blocked_count}, Failed={failed_count}, Planned={planned_count}")
                    
                    pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0
                    block_rate = (blocked_count / total_count * 100) if total_count > 0 else 0
                    fail_rate = (failed_count / total_count * 100) if total_count > 0 else 0
                    execution_rate = (executed_count / total_count * 100) if total_count > 0 else 0
                else:
                    print("警告: 无法找到状态列")
                    pass_rate = block_rate = fail_rate = execution_rate = 0
            else:
                pass_rate = block_rate = fail_rate = execution_rate = 0
            
            # 创建KPI指标显示
            kpi_indicators = html.Div([
                html.Div([
                    html.H4(f"{total_count:,}", style={'margin': '0', 'color': '#2c3e50', 'fontSize': '28px'}),
                    html.P("总测试数", style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '14px'}),
                ], style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 'padding': '20px', 'borderRadius': '8px', 'margin': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                
                html.Div([
                    html.H4(f"{block_rate:.1f}%", style={'margin': '0', 'color': '#e74c3c', 'fontSize': '28px'}),
                    html.P("测试阻塞率", style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '14px'}),
                ], style={'textAlign': 'center', 'backgroundColor': '#fadbd8', 'padding': '20px', 'borderRadius': '8px', 'margin': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                
                html.Div([
                    html.H4(f"{100-execution_rate:.1f}%", style={'margin': '0', 'color': '#3498db', 'fontSize': '28px'}),
                    html.P("计划中", style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '14px'}),
                ], style={'textAlign': 'center', 'backgroundColor': '#d6eaf8', 'padding': '20px', 'borderRadius': '8px', 'margin': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                
                html.Div([
                    html.H4(f"{pass_rate:.1f}%", style={'margin': '0', 'color': '#27ae60', 'fontSize': '28px'}),
                    html.P("测试通过率", style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '14px'}),
                ], style={'textAlign': 'center', 'backgroundColor': '#d5f4e6', 'padding': '20px', 'borderRadius': '8px', 'margin': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                
                html.Div([
                    html.H4(f"{fail_rate:.1f}%", style={'margin': '0', 'color': '#f39c12', 'fontSize': '28px'}),
                    html.P("测试失败率", style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '14px'}),
                ], style={'textAlign': 'center', 'backgroundColor': '#fdeaa7', 'padding': '20px', 'borderRadius': '8px', 'margin': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
                
                html.Div([
                    html.H4(f"{execution_rate:.1f}%", style={'margin': '0', 'color': '#9b59b6', 'fontSize': '28px'}),
                    html.P("测试执行率", style={'margin': '0', 'color': '#7f8c8d', 'fontSize': '14px'}),
                ], style={'textAlign': 'center', 'backgroundColor': '#e8daef', 'padding': '20px', 'borderRadius': '8px', 'margin': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
            ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around', 'marginBottom': '25px'})
            
            # 创建三个图表
            status_pie_fig = create_enhanced_status_distribution_pie(filtered_tdf)
            pass_rate_fig = create_pass_rate_trend_chart(filtered_tdf)
            aida_heatmap_fig = create_test_aida_wordcloud(filtered_tdf)
            
            return status_pie_fig, pass_rate_fig, aida_heatmap_fig, kpi_indicators
            
        except Exception as e:
            print(f"Phase 1 图表创建出错: {e}")
            import traceback
            traceback.print_exc()
            
            empty_fig = create_empty_figure("图表创建失败", height=400)
            empty_kpi = html.Div("数据处理失败", style={'textAlign': 'center', 'color': '#dc3545'})
            return empty_fig, empty_fig, empty_fig, empty_kpi

    print(f"测试覆盖率回调函数已注册 (前缀: {prefix})")

    @app.callback(
        Output(f'{prefix}-download-chart3-xlsx', 'data'),
        Input(f'{prefix}-export-chart3-btn', 'n_clicks'),
        State(f'{prefix}-chart3-filtered-store', 'data'),
        prevent_initial_call=True
    )
    def export_chart3_prefixed(n_clicks, store_data):
        if not n_clicks:
            return None
        if not store_data:
            return None
        df = pd.DataFrame(store_data)
        if df.empty:
            return None
        def to_cw_label(val):
            s = str(val)
            if 'CW' in s:
                try:
                    week = s.split('CW')[1][:2]
                    return f'CW{week}'
                except Exception:
                    return s
            return s
        df['week_label'] = df['test_week'].apply(to_cw_label)
        priority = { 'Failed': 4, 'Blocked': 3, 'Requires Attention': 2, 'Planned': 1, 'Passed': 0 }
        def pick_status(series):
            return series.sort_values(key=lambda s: s.map(lambda x: priority.get(str(x), -1)), ascending=False).iloc[0]
        index_cols = ['test_id', 'test_name', 'top_aida', 'fv', 'project', 'pu', 'tester']
        for col in index_cols:
            if col not in df.columns:
                df[col] = ''
        grouped = df.groupby(index_cols + ['week_label'])['run_status'].apply(pick_status).reset_index()
        pivot = grouped.pivot(index=index_cols, columns='week_label', values='run_status')
        def week_sort_key(col):
            try:
                return int(str(col).replace('CW',''))
            except Exception:
                return 999
        ordered_cols = sorted(pivot.columns.tolist(), key=week_sort_key)
        pivot = pivot.reindex(columns=ordered_cols)
        pivot = pivot.reset_index()
        week_cols = ordered_cols
        def overall_status_row(row):
            vals = [str(row[c]) for c in week_cols if c in row and pd.notna(row[c])]
            if not vals:
                return ''
            return sorted(vals, key=lambda x: priority.get(str(x), -1), reverse=True)[0]
        pivot.insert(len(index_cols), '总体状态', pivot.apply(overall_status_row, axis=1))
        def calc_freq(row):
            vals = [row[c] for c in week_cols if c in row]
            tested = sum(pd.notna(v) and str(v) != '' for v in vals)
            return tested / len(week_cols) if len(week_cols) > 0 else 0
        def calc_pass_rate(row):
            vals = [row[c] for c in week_cols if c in row]
            tested_vals = [v for v in vals if pd.notna(v) and str(v) != '']
            if not tested_vals:
                return 0
            passed = sum(str(v) == 'Passed' for v in tested_vals)
            return passed / len(tested_vals)
        pivot['Test Frequency'] = pivot.apply(calc_freq, axis=1)
        pivot['Pass Rate'] = pivot.apply(calc_pass_rate, axis=1)
        avg_freq = float(pivot['Test Frequency'].mean(skipna=True)) if 'Test Frequency' in pivot.columns else 0
        avg_pass = float(pivot['Pass Rate'].mean(skipna=True)) if 'Pass Rate' in pivot.columns else 0
        avg_row = {col: '' for col in pivot.columns}
        avg_row['总体状态'] = ''
        avg_row['Test Frequency'] = avg_freq
        avg_row['Pass Rate'] = avg_pass
        pivot = pd.concat([pivot, pd.DataFrame([avg_row])], ignore_index=True)
        from io import BytesIO
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            pivot.to_excel(writer, index=False, sheet_name='Pivot')
            workbook = writer.book
            worksheet = writer.sheets['Pivot']
            nrows, ncols = pivot.shape
            worksheet.autofilter(0, 0, nrows, ncols - 1)
            worksheet.freeze_panes(1, len(index_cols) + 1)
            fmt_failed = workbook.add_format({'bg_color': '#FFC7CE'})
            fmt_blocked = workbook.add_format({'bg_color': '#FFD966'})
            fmt_attention = workbook.add_format({'bg_color': '#FFF2CC'})
            fmt_planned = workbook.add_format({'bg_color': '#D9D9D9'})
            fmt_passed = workbook.add_format({'bg_color': '#C6EFCE'})
            percent_fmt = workbook.add_format({'num_format': '0%'})
            start_col = len(index_cols) + 1
            end_col = ncols - 1
            worksheet.conditional_format(1, start_col, nrows, end_col, {'type': 'text', 'criteria': 'containing', 'value': 'Failed', 'format': fmt_failed})
            worksheet.conditional_format(1, start_col, nrows, end_col, {'type': 'text', 'criteria': 'containing', 'value': 'Blocked', 'format': fmt_blocked})
            worksheet.conditional_format(1, start_col, nrows, end_col, {'type': 'text', 'criteria': 'containing', 'value': 'Requires Attention', 'format': fmt_attention})
            worksheet.conditional_format(1, start_col, nrows, end_col, {'type': 'text', 'criteria': 'containing', 'value': 'Planned', 'format': fmt_planned})
            worksheet.conditional_format(1, start_col, nrows, end_col, {'type': 'text', 'criteria': 'containing', 'value': 'Passed', 'format': fmt_passed})
            tf_col = pivot.columns.get_loc('Test Frequency')
            pr_col = pivot.columns.get_loc('Pass Rate')
            worksheet.set_column(tf_col, tf_col, None, percent_fmt)
            worksheet.set_column(pr_col, pr_col, None, percent_fmt)
        buffer.seek(0)
        from dash import dcc
        return dcc.send_bytes(buffer.getvalue(), filename='测试覆盖率_图表三_导出.xlsx')
