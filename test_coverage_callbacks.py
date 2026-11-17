# Test Coverage Analysis 回调函数模块
import hashlib
import json
import time
import uuid
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
    get_cached_test_coverage_dataframe
)
from data_processor import create_empty_figure

_RESULT_CACHE = {}
_RESULT_CACHE_TTL_SECONDS = 1800
_RESULT_CACHE_MAX_ENTRIES = 16
_HIDDEN_PHASE1_CHARTS_ENABLED = False


def _extract_scalar_value(value):
    if isinstance(value, dict):
        for key in ('name', 'full_name', 'value', 'id'):
            if key in value and value.get(key) not in (None, ''):
                return str(value.get(key)).strip()
        return ''
    if value is None:
        return ''
    if isinstance(value, float) and pd.isna(value):
        return ''
    return str(value).strip()


def _extract_year_from_week(value):
    text = _extract_scalar_value(value)
    if not text:
        return None
    import re
    m = re.search(r'(\d{2,4})\s*-\s*CW\s*(\d{1,2})', text, flags=re.IGNORECASE)
    if not m:
        return None
    year = int(m.group(1))
    if year < 100:
        year += 2000
    return year


def _build_year_series(df):
    year_series = pd.to_numeric(df['year'], errors='coerce') if 'year' in df.columns else pd.Series(index=df.index, dtype='float64')
    year_series = year_series.where(year_series.isna() | (year_series >= 100), year_series + 2000)
    if 'test_week' in df.columns:
        week_years = df['test_week'].apply(_extract_year_from_week)
        year_series = year_series.where(week_years.isna(), week_years)
    return pd.to_numeric(year_series, errors='coerce')


def _cleanup_result_cache():
    now = time.time()
    expired_keys = [
        key for key, payload in _RESULT_CACHE.items()
        if payload.get("expires_at", 0) <= now
    ]
    for key in expired_keys:
        _RESULT_CACHE.pop(key, None)
    if len(_RESULT_CACHE) > _RESULT_CACHE_MAX_ENTRIES:
        ordered_keys = sorted(_RESULT_CACHE.keys(), key=lambda k: _RESULT_CACHE[k].get("expires_at", 0))
        for old_key in ordered_keys[:len(_RESULT_CACHE) - _RESULT_CACHE_MAX_ENTRIES]:
            _RESULT_CACHE.pop(old_key, None)


def _cache_dataframe_result(df, tag):
    if df is None or df.empty:
        return ''
    _cleanup_result_cache()
    cache_key = f"tc-result-{tag}-{uuid.uuid4().hex}"
    _RESULT_CACHE[cache_key] = {
        "dataframe": df,
        "expires_at": time.time() + _RESULT_CACHE_TTL_SECONDS
    }
    return cache_key


def _get_cached_dataframe_result(cache_key):
    if not cache_key:
        return pd.DataFrame()
    _cleanup_result_cache()
    payload = _RESULT_CACHE.get(cache_key)
    if not payload:
        return pd.DataFrame()
    cached_df = payload.get("dataframe")
    if cached_df is None:
        return pd.DataFrame()
    return cached_df


def _get_source_dataframe(stored_data):
    if isinstance(stored_data, dict):
        return get_cached_test_coverage_dataframe(stored_data.get('cache_key'))
    if isinstance(stored_data, list):
        return pd.DataFrame(stored_data)
    return pd.DataFrame()


def _normalize_working_dataframe(df):
    if df.empty:
        return df
    if 'tc_prepared_flag' in df.columns:
        return df
    normalized_df = df.copy()
    for col in ['project', 'test_week', 'pu', 'top_aida', 'feature_region', 'fvp', 'fv', 'native_status', 'run_status', 'status', 'execution_status', 'tester']:
        if col in normalized_df.columns:
            normalized_df[col] = normalized_df[col].apply(_extract_scalar_value)
    normalized_df['tc_prepared_flag'] = True
    return normalized_df


def _is_filter_active(filter_value):
    return filter_value and len(filter_value) > 0 and 'all' not in filter_value


def _normalize_filter_value(filter_value):
    if not filter_value:
        return []
    normalized = []
    for item in filter_value:
        normalized.append(_extract_scalar_value(item))
    return sorted([item for item in normalized if item != ''])


def _build_filter_signature(source_cache_key, selected_years, selected_projects, selected_testweeks, selected_pus,
                            selected_aidas, selected_statuses, selected_feature_regions, selected_fvps, selected_fvs):
    signature_payload = {
        "source_cache_key": source_cache_key,
        "years": _normalize_filter_value(selected_years),
        "projects": _normalize_filter_value(selected_projects),
        "testweeks": _normalize_filter_value(selected_testweeks),
        "pus": _normalize_filter_value(selected_pus),
        "aidas": _normalize_filter_value(selected_aidas),
        "statuses": _normalize_filter_value(selected_statuses),
        "feature_regions": _normalize_filter_value(selected_feature_regions),
        "fvps": _normalize_filter_value(selected_fvps),
        "fvs": _normalize_filter_value(selected_fvs)
    }
    signature_text = json.dumps(signature_payload, ensure_ascii=False, sort_keys=True)
    return hashlib.md5(signature_text.encode("utf-8")).hexdigest()


def _apply_common_filters(df, selected_years, selected_projects, selected_testweeks, selected_pus,
                          selected_aidas, selected_statuses, selected_feature_regions, selected_fvps, selected_fvs):
    filtered_tdf = df.copy()
    if _is_filter_active(selected_years):
        year_series = _build_year_series(filtered_tdf)
        filtered_tdf = filtered_tdf[year_series.astype('Int64').isin([int(y) for y in selected_years])]
    if _is_filter_active(selected_projects):
        filtered_tdf = filtered_tdf[filtered_tdf['project'].isin(selected_projects)]
    if _is_filter_active(selected_testweeks):
        filtered_tdf = filtered_tdf[filtered_tdf['test_week'].isin(selected_testweeks)]
    if _is_filter_active(selected_pus):
        filtered_tdf = filtered_tdf[filtered_tdf['pu'].isin(selected_pus)]
    if _is_filter_active(selected_aidas) and 'top_aida' in filtered_tdf.columns:
        filtered_tdf = filtered_tdf[filtered_tdf['top_aida'].isin(selected_aidas)]
    if _is_filter_active(selected_feature_regions) and 'feature_region' in filtered_tdf.columns:
        filtered_tdf = filtered_tdf[filtered_tdf['feature_region'].isin(selected_feature_regions)]
    if _is_filter_active(selected_fvps):
        filtered_tdf = filtered_tdf[filtered_tdf['fvp'].isin(selected_fvps)]
    if _is_filter_active(selected_fvs):
        filtered_tdf = filtered_tdf[filtered_tdf['fv'].isin(selected_fvs)]
    if _is_filter_active(selected_statuses):
        if 'native_status' in filtered_tdf.columns:
            status_names = filtered_tdf['native_status'].apply(_extract_scalar_value)
            filtered_tdf = filtered_tdf[status_names.isin(selected_statuses)]
        else:
            status_column = next((col for col in ['run_status', 'status', 'execution_status'] if col in filtered_tdf.columns), None)
            if status_column:
                filtered_tdf = filtered_tdf[filtered_tdf[status_column].isin(selected_statuses)]
    return filtered_tdf


def _build_export_dataframe(filtered_tdf):
    if filtered_tdf.empty:
        return pd.DataFrame()
    status_mapping = {
        'passed': 'Passed',
        'failed': 'Failed',
        'blocked': 'Blocked',
        'planned': 'Planned',
        'requires attention': 'Blocked'
    }
    if 'native_status' in filtered_tdf.columns:
        status_series = filtered_tdf['native_status'].apply(_extract_scalar_value)
    else:
        status_source_col = next((c for c in ['run_status', 'status', 'execution_status'] if c in filtered_tdf.columns), None)
        status_series = filtered_tdf[status_source_col] if status_source_col else pd.Series([''] * len(filtered_tdf))
    export_df = filtered_tdf.copy()
    export_df['export_status'] = status_series.apply(
        lambda x: status_mapping.get(str(x).strip().lower(), str(x).strip()) if x is not None else ''
    )
    export_cols = [
        'test_week', 'test_id', 'test_name',
        'export_status',
        'top_aida', 'fvp', 'fv',
        'project', 'pu', 'tester'
    ]
    for col in export_cols:
        if col not in export_df.columns:
            export_df[col] = ''
    return export_df[export_cols].copy()


def build_chart3_export_xlsx(store_data):
    if not store_data:
        return None
    if isinstance(store_data, pd.DataFrame):
        df = store_data.copy()
    else:
        df = pd.DataFrame(store_data)
    if df.empty:
        return None

    from io import BytesIO

    base_cols = ['test_id', 'test_name', 'top_aida', 'fvp', 'fv', 'project', 'pu', 'tester']
    required_cols = ['test_week'] + base_cols
    for col in required_cols:
        if col not in df.columns:
            df[col] = ''

    status_col = 'export_status' if 'export_status' in df.columns else next(
        (c for c in ['run_status', 'status', 'execution_status'] if c in df.columns),
        None
    )
    if not status_col:
        return None

    status_mapping = {
        'passed': 'Passed',
        'failed': 'Failed',
        'blocked': 'Blocked',
        'planned': 'Planned',
        'requires attention': 'Blocked'
    }
    df['status_norm'] = df[status_col].apply(
        lambda x: status_mapping.get(str(x).strip().lower(), str(x).strip()) if x is not None else ''
    )

    df['test_week_str'] = df['test_week'].apply(lambda x: str(x) if x is not None else '').fillna('')

    parsed = df['test_week_str'].str.extract(r'(\d{2})-CW(\d{2})')
    df['_year'] = pd.to_numeric(parsed[0], errors='coerce')
    df['_cw'] = pd.to_numeric(parsed[1], errors='coerce')

    week_meta = (
        df[['test_week_str', '_year', '_cw']]
        .drop_duplicates()
        .assign(_year_sort=lambda d: d['_year'].fillna(99).astype(int),
                _cw_sort=lambda d: d['_cw'].fillna(99).astype(int))
        .sort_values(['_year_sort', '_cw_sort', 'test_week_str'])
    )
    years_present = week_meta['_year'].dropna().unique().tolist()
    use_short_label = len(years_present) == 1

    label_map = {}
    used_labels = set()
    for _, r in week_meta.iterrows():
        wk = r['test_week_str']
        yr = r['_year']
        cw = r['_cw']
        if pd.notna(yr) and pd.notna(cw):
            if use_short_label:
                label = f'CW{int(cw):02d}'
            else:
                label = f'{int(yr):02d}-CW{int(cw):02d}'
        else:
            label = wk
        if label in used_labels:
            label = wk
        used_labels.add(label)
        label_map[wk] = label

    df['week_label'] = df['test_week_str'].map(label_map).fillna(df['test_week_str'])

    priority = {'Failed': 4, 'Blocked': 3, 'Requires Attention': 3, 'Planned': 1, 'Passed': 0}

    def pick_status(series):
        return series.sort_values(key=lambda s: s.map(lambda x: priority.get(str(x), -1)), ascending=False).iloc[0]

    grouped = (
        df.groupby(base_cols + ['week_label'], dropna=False)['status_norm']
        .apply(pick_status)
        .reset_index()
    )

    pivot = grouped.pivot(index=base_cols, columns='week_label', values='status_norm')

    ordered_week_labels = [label_map[w] for w in week_meta['test_week_str'].tolist() if w in label_map]
    ordered_week_labels = [w for w in ordered_week_labels if w in pivot.columns]
    remaining = [c for c in pivot.columns.tolist() if c not in ordered_week_labels]
    week_cols = ordered_week_labels + remaining
    pivot = pivot.reindex(columns=week_cols)
    pivot = pivot.reset_index()

    def _count_weeks_with_result(row):
        vals = [row.get(c) for c in week_cols]
        return sum(pd.notna(v) and str(v).strip() != '' for v in vals)

    def _count_weeks_passed(row):
        vals = [row.get(c) for c in week_cols]
        vals = [v for v in vals if pd.notna(v) and str(v).strip() != '']
        return sum(str(v).strip() == 'Passed' for v in vals)

    total_weeks = len(week_cols)
    pivot['_weeks_with_result'] = pivot.apply(_count_weeks_with_result, axis=1)
    pivot['_weeks_passed'] = pivot.apply(_count_weeks_passed, axis=1)
    pivot['Test Frequency'] = pivot['_weeks_with_result'].apply(lambda x: (x / total_weeks) if total_weeks > 0 else 0)
    pivot['Pass Rate'] = pivot.apply(
        lambda r: (r['_weeks_passed'] / r['_weeks_with_result']) if r['_weeks_with_result'] > 0 else 0,
        axis=1
    )

    rename_map = {
        'test_id': 'Testcase ID',
        'test_name': 'Testcase Name',
        'top_aida': 'Top AIDA',
        'fvp': 'FVP',
        'fv': 'FV',
        'project': 'Project',
        'pu': 'PU',
        'tester': 'Tester'
    }
    pivot = pivot.rename(columns=rename_map)
    base_headers = [rename_map.get(c, c) for c in base_cols]
    output_cols = base_headers + week_cols + ['Test Frequency', 'Pass Rate']
    pivot_out = pivot[output_cols]

    stats_out = pivot[['Testcase ID', 'Testcase Name', 'Top AIDA', 'FVP', 'FV', 'Project', 'PU', 'Tester', '_weeks_with_result', '_weeks_passed', 'Test Frequency', 'Pass Rate']].copy()
    stats_out = stats_out.rename(columns={'_weeks_with_result': 'Weeks With Result', '_weeks_passed': 'Weeks Passed'})

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        pivot_out.to_excel(writer, index=False, sheet_name='Pivot')
        stats_out.to_excel(writer, index=False, sheet_name='Stats')

        workbook = writer.book
        worksheet = writer.sheets['Pivot']
        stats_ws = writer.sheets['Stats']

        nrows, ncols = pivot_out.shape
        worksheet.autofilter(0, 0, nrows, ncols - 1)
        worksheet.freeze_panes(1, len(base_headers))

        worksheet.set_column(0, 0, 14)
        worksheet.set_column(1, 1, 48)
        worksheet.set_column(2, 2, 46)
        worksheet.set_column(3, 7, 16)

        first_week_col = len(base_headers)
        last_week_col = first_week_col + len(week_cols) - 1
        if len(week_cols) > 0:
            worksheet.set_column(first_week_col, last_week_col, 11)

        tf_col = pivot_out.columns.get_loc('Test Frequency')
        pr_col = pivot_out.columns.get_loc('Pass Rate')

        percent_fmt = workbook.add_format({'num_format': '0%'})
        worksheet.set_column(tf_col, tf_col, 14, percent_fmt)
        worksheet.set_column(pr_col, pr_col, 12, percent_fmt)

        fmt_failed = workbook.add_format({'bg_color': '#FFC7CE'})
        fmt_blocked = workbook.add_format({'bg_color': '#FFD966'})
        fmt_planned = workbook.add_format({'bg_color': '#D9D9D9'})
        fmt_passed = workbook.add_format({'bg_color': '#C6EFCE'})

        if len(week_cols) > 0:
            worksheet.conditional_format(1, first_week_col, nrows, last_week_col, {'type': 'text', 'criteria': 'containing', 'value': 'Failed', 'format': fmt_failed})
            worksheet.conditional_format(1, first_week_col, nrows, last_week_col, {'type': 'text', 'criteria': 'containing', 'value': 'Blocked', 'format': fmt_blocked})
            worksheet.conditional_format(1, first_week_col, nrows, last_week_col, {'type': 'text', 'criteria': 'containing', 'value': 'Planned', 'format': fmt_planned})
            worksheet.conditional_format(1, first_week_col, nrows, last_week_col, {'type': 'text', 'criteria': 'containing', 'value': 'Passed', 'format': fmt_passed})

        stats_rows, stats_cols = stats_out.shape
        stats_ws.autofilter(0, 0, stats_rows, stats_cols - 1)
        stats_ws.freeze_panes(1, 0)
        tf2 = stats_out.columns.get_loc('Test Frequency')
        pr2 = stats_out.columns.get_loc('Pass Rate')
        stats_ws.set_column(tf2, tf2, 14, percent_fmt)
        stats_ws.set_column(pr2, pr2, 12, percent_fmt)
        stats_ws.set_column(0, 0, 14)
        stats_ws.set_column(1, 1, 48)
        stats_ws.set_column(2, 2, 46)
        stats_ws.set_column(3, 7, 16)
        stats_ws.set_column(8, 9, 18)

    buffer.seek(0)
    return buffer.getvalue()

def register_test_coverage_callbacks(app, prefix="de-tc"):
    """注册测试覆盖率分析的回调函数"""
    
    # 主图表更新回调
    @app.callback(
        [Output(f'{prefix}-project-status-chart', 'figure'),
         Output(f'{prefix}-fvp-coverage-chart', 'figure'),
         Output(f'{prefix}-testcase-detail-chart', 'figure'),
         Output(f'{prefix}-fv-dropdown', 'value'),        # 动态更新FV选项
         Output(f'{prefix}-aida-dropdown', 'value'),      # 动态更新AIDA选项
         Output(f'{prefix}-chart3-filtered-store', 'data')],
        [Input(f'{prefix}-year-dropdown', 'value'),
         Input(f'{prefix}-project-dropdown', 'value'),
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
    def update_test_coverage_charts(selected_years, selected_projects, selected_testweeks, selected_pus,
                                   selected_aidas_input, selected_statuses, selected_feature_regions, 
                                   selected_fvps, selected_fvs_input,
                                   click_data_fv, click_data_aida, click_data_test, 
                                   stored_data,
                                   fv_state, aida_state):
        start_total = time.perf_counter()
        print(f"--- 测试覆盖率回调触发: {callback_context.triggered_id if callback_context.triggered else 'Initial load'} ---")
        ctx = callback_context
        if not stored_data:
            print("警告: 数据存储为空")
            empty_fig = create_empty_figure("数据加载失败")
            return empty_fig, empty_fig, empty_fig, [], [], {}
        try:
            source_cache_key = stored_data.get('cache_key') if isinstance(stored_data, dict) else ''
            load_start = time.perf_counter()
            source_tdf = _get_source_dataframe(stored_data)
            print(f"[tc-main][timing] load_source_ms={(time.perf_counter() - load_start) * 1000:.1f}, rows={len(source_tdf)}")
            if source_tdf.empty:
                empty_fig = create_empty_figure("数据加载失败")
                return empty_fig, empty_fig, empty_fig, [], [], {}
            normalize_start = time.perf_counter()
            working_tdf = _normalize_working_dataframe(source_tdf)
            print(f"[tc-main][timing] normalize_ms={(time.perf_counter() - normalize_start) * 1000:.1f}, rows={len(working_tdf)}")

            output_fvs = list(fv_state) if fv_state else ['all']
            output_aidas = list(aida_state) if aida_state else ['all']
            if ctx.triggered:
                triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
                if 'project-status-chart' in triggered_id and click_data_fv and click_data_fv.get('points'):
                    clicked_fv = click_data_fv['points'][0].get('y', '')
                    if clicked_fv:
                        output_fvs = [clicked_fv] if clicked_fv != 'all' else ['all']
                elif 'fvp-coverage-chart' in triggered_id and click_data_aida and click_data_aida.get('points'):
                    clicked_aida = click_data_aida['points'][0].get('y', '')
                    if clicked_aida:
                        output_aidas = [clicked_aida] if clicked_aida != 'all' else ['all']
                elif 'aida-dropdown' in triggered_id:
                    output_aidas = selected_aidas_input if selected_aidas_input else ['all']
                elif 'fv-dropdown' in triggered_id:
                    output_fvs = selected_fvs_input if selected_fvs_input else ['all']

            filter_sig = _build_filter_signature(
                source_cache_key, selected_years, selected_projects, selected_testweeks, selected_pus,
                output_aidas, selected_statuses, selected_feature_regions, selected_fvps, output_fvs
            )
            filtered_cache_key = f"tc-filtered-{filter_sig}"
            cache_hit_start = time.perf_counter()
            filtered_tdf = _get_cached_dataframe_result(filtered_cache_key)
            cache_hit = not filtered_tdf.empty
            print(f"[tc-main][timing] filter_cache_lookup_ms={(time.perf_counter() - cache_hit_start) * 1000:.1f}, hit={cache_hit}")
            if not cache_hit:
                filter_start = time.perf_counter()
                filtered_tdf = _apply_common_filters(
                    working_tdf, selected_years, selected_projects, selected_testweeks, selected_pus,
                    output_aidas, selected_statuses, selected_feature_regions, selected_fvps, output_fvs
                )
                print(f"[tc-main][timing] filter_compute_ms={(time.perf_counter() - filter_start) * 1000:.1f}, rows={len(filtered_tdf)}")
                if not filtered_tdf.empty:
                    _RESULT_CACHE[filtered_cache_key] = {
                        "dataframe": filtered_tdf.copy(),
                        "expires_at": time.time() + _RESULT_CACHE_TTL_SECONDS
                    }
            if filtered_tdf.empty:
                empty_fig = create_empty_figure("筛选后无数据")
                return empty_fig, empty_fig, empty_fig, output_fvs, output_aidas, {}

            has_active_filters = (
                _is_filter_active(selected_projects) or
                _is_filter_active(selected_years) or
                _is_filter_active(selected_testweeks) or
                _is_filter_active(selected_pus) or
                _is_filter_active(output_aidas) or
                _is_filter_active(selected_feature_regions) or
                _is_filter_active(selected_fvps) or
                _is_filter_active(output_fvs) or
                _is_filter_active(selected_statuses)
            )

            chart_start = time.perf_counter()
            fig1 = create_project_status_chart(filtered_tdf)
            fig2 = create_fvp_coverage_chart(filtered_tdf)
            fig3 = create_testcase_detail_chart(filtered_tdf, has_active_filters)
            print(f"[tc-main][timing] render_charts_ms={(time.perf_counter() - chart_start) * 1000:.1f}")

            export_start = time.perf_counter()
            export_df = _build_export_dataframe(filtered_tdf)
            export_cache_key = _cache_dataframe_result(export_df, tag="chart3-export")
            export_store = {
                "cache_key": export_cache_key,
                "rows": int(len(export_df)),
                "source_cache_key": source_cache_key
            }
            print(f"[tc-main][timing] prepare_export_ms={(time.perf_counter() - export_start) * 1000:.1f}, rows={len(export_df)}, key={export_cache_key}")
            print(f"[tc-main][timing] total_ms={(time.perf_counter() - start_total) * 1000:.1f}")
            return fig1, fig2, fig3, output_fvs, output_aidas, export_store
        except Exception as e:
            print(f"回调函数执行失败: {e}")
            import traceback
            traceback.print_exc()
            error_fig = create_empty_figure(f"数据处理失败: {str(e)[:100]}")
            return error_fig, error_fig, error_fig, [], [], {}

    # Phase 1 新增图表的回调函数
    @app.callback(
        [Output(f'{prefix}-status-distribution-pie', 'figure'),
         Output(f'{prefix}-pass-rate-trend-chart', 'figure'),
         Output(f'{prefix}-aida-wordcloud', 'figure'),
         Output(f'{prefix}-kpi-indicators', 'children')],
        [Input(f'{prefix}-year-dropdown', 'value'),
         Input(f'{prefix}-project-dropdown', 'value'),
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
    def update_phase1_charts(selected_years, selected_projects, selected_testweeks, selected_pus,
                           selected_aidas, selected_statuses, selected_feature_regions, 
                           selected_fvps, selected_fvs, stored_data):
        start_total = time.perf_counter()
        try:
            print("--- Phase 1 图表更新 ---")
            if not stored_data:
                empty_fig = create_empty_figure("数据加载失败", height=400)
                empty_kpi = html.Div("数据加载失败", style={'textAlign': 'center', 'color': '#dc3545'})
                return empty_fig, empty_fig, empty_fig, empty_kpi

            source_cache_key = stored_data.get('cache_key') if isinstance(stored_data, dict) else ''
            load_start = time.perf_counter()
            source_tdf = _get_source_dataframe(stored_data)
            print(f"[tc-phase1][timing] load_source_ms={(time.perf_counter() - load_start) * 1000:.1f}, rows={len(source_tdf)}")
            if source_tdf.empty:
                empty_fig = create_empty_figure("数据加载失败", height=400)
                empty_kpi = html.Div("数据加载失败", style={'textAlign': 'center', 'color': '#dc3545'})
                return empty_fig, empty_fig, empty_fig, empty_kpi

            normalize_start = time.perf_counter()
            working_tdf = _normalize_working_dataframe(source_tdf)
            print(f"[tc-phase1][timing] normalize_ms={(time.perf_counter() - normalize_start) * 1000:.1f}, rows={len(working_tdf)}")

            filter_sig = _build_filter_signature(
                source_cache_key, selected_years, selected_projects, selected_testweeks, selected_pus,
                selected_aidas, selected_statuses, selected_feature_regions, selected_fvps, selected_fvs
            )
            filtered_cache_key = f"tc-filtered-{filter_sig}"
            filtered_tdf = _get_cached_dataframe_result(filtered_cache_key)
            if filtered_tdf.empty:
                filter_start = time.perf_counter()
                filtered_tdf = _apply_common_filters(
                    working_tdf, selected_years, selected_projects, selected_testweeks, selected_pus,
                    selected_aidas, selected_statuses, selected_feature_regions, selected_fvps, selected_fvs
                )
                print(f"[tc-phase1][timing] filter_compute_ms={(time.perf_counter() - filter_start) * 1000:.1f}, rows={len(filtered_tdf)}")
                if not filtered_tdf.empty:
                    _RESULT_CACHE[filtered_cache_key] = {
                        "dataframe": filtered_tdf.copy(),
                        "expires_at": time.time() + _RESULT_CACHE_TTL_SECONDS
                    }
            else:
                print(f"[tc-phase1][timing] filter_cache_hit rows={len(filtered_tdf)}")

            total_count = len(filtered_tdf)
            if total_count > 0:
                if 'native_status' in filtered_tdf.columns:
                    status_names = filtered_tdf['native_status'].apply(lambda x: _extract_scalar_value(x).lower())
                elif 'run_status' in filtered_tdf.columns:
                    status_names = filtered_tdf['run_status'].apply(lambda x: _extract_scalar_value(x).lower())
                else:
                    status_names = pd.Series(['unknown'] * total_count)
                passed_count = len(status_names[status_names == 'passed'])
                blocked_count = len(status_names[status_names == 'blocked']) + len(status_names[status_names == 'requires attention'])
                failed_count = len(status_names[status_names == 'failed'])
                planned_count = len(status_names[status_names == 'planned'])
                executed_count = total_count - planned_count
                pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0
                block_rate = (blocked_count / total_count * 100) if total_count > 0 else 0
                fail_rate = (failed_count / total_count * 100) if total_count > 0 else 0
                execution_rate = (executed_count / total_count * 100) if total_count > 0 else 0
            else:
                pass_rate = block_rate = fail_rate = execution_rate = 0

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

            if not _HIDDEN_PHASE1_CHARTS_ENABLED:
                empty_hidden = create_empty_figure("隐藏图表已跳过计算", height=400)
                print(f"[tc-phase1][timing] total_ms={(time.perf_counter() - start_total) * 1000:.1f}, hidden_charts_skipped=True")
                return empty_hidden, empty_hidden, empty_hidden, kpi_indicators

            chart_start = time.perf_counter()
            status_pie_fig = create_enhanced_status_distribution_pie(filtered_tdf)
            pass_rate_fig = create_pass_rate_trend_chart(filtered_tdf)
            aida_heatmap_fig = create_test_aida_wordcloud(filtered_tdf)
            print(f"[tc-phase1][timing] render_charts_ms={(time.perf_counter() - chart_start) * 1000:.1f}")
            print(f"[tc-phase1][timing] total_ms={(time.perf_counter() - start_total) * 1000:.1f}")
            return status_pie_fig, pass_rate_fig, aida_heatmap_fig, kpi_indicators
        except Exception as e:
            print(f"Phase 1 图表创建出错: {e}")
            import traceback
            traceback.print_exc()
            empty_fig = create_empty_figure("图表创建失败", height=400)
            empty_kpi = html.Div("数据处理失败", style={'textAlign': 'center', 'color': '#dc3545'})
            return empty_fig, empty_fig, empty_fig, empty_kpi

    @app.callback(
        [Output(f'{prefix}-download-chart3-xlsx', 'data'),
         Output(f'{prefix}-export-status', 'children'),
         Output(f'{prefix}-export-progress', 'children')],
        Input(f'{prefix}-export-chart3-btn', 'n_clicks'),
        State(f'{prefix}-chart3-filtered-store', 'data'),
        State(f'{prefix}-data-store', 'data'),
        prevent_initial_call=True
    )
    def export_chart3_prefixed(n_clicks, store_data, all_store_data):
        if not n_clicks:
            return None, '', ''
        export_start = time.perf_counter()
        export_df = pd.DataFrame()
        if isinstance(store_data, dict):
            export_df = _get_cached_dataframe_result(store_data.get('cache_key'))
        elif isinstance(store_data, list):
            export_df = pd.DataFrame(store_data)
        if export_df.empty:
            if isinstance(all_store_data, dict):
                source_df = _get_source_dataframe(all_store_data)
                if not source_df.empty:
                    normalized_df = _normalize_working_dataframe(source_df)
                    export_df = _build_export_dataframe(normalized_df)
            elif isinstance(all_store_data, list):
                export_df = pd.DataFrame(all_store_data)
        if export_df.empty:
            return None, '无可导出数据（请先等待图表加载/选择筛选条件）', ''
        try:
            print(f"[chart3 export][timing] prepare_ms={(time.perf_counter() - export_start) * 1000:.1f}, rows={len(export_df)}")
            xlsx_bytes = build_chart3_export_xlsx(export_df)
            if not xlsx_bytes:
                return None, '导出失败：数据字段不完整', ''
            from dash import dcc
            return (
                dcc.send_bytes(xlsx_bytes, filename='测试覆盖率_图表三_导出.xlsx'),
                '已生成，开始下载',
                f'导出记录数: {len(export_df)}'
            )
        except Exception as e:
            return None, f'导出失败: {str(e)[:120]}', ''

    print(f"测试覆盖率回调函数已注册 (前缀: {prefix})")
