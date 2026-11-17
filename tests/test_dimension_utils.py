import unittest

import pandas as pd

from dimension_utils import build_chart_dimension, normalize_dimension_value, sort_dimension_with_unknown_last


class TestDimensionUtils(unittest.TestCase):
    def test_fv_unknown_ratio_matches_source_missing_rate(self):
        df = pd.DataFrame(
            {
                'fv': ['Audio', '', None, 'Unknown', '未分类数据', '  ', 'HVAC']
            }
        )
        chart_dimension = build_chart_dimension(df, 'fv')
        source_missing_rate = (df['fv'].apply(normalize_dimension_value) == '').mean()
        unknown_ratio = (chart_dimension == 'Unknown').mean()
        self.assertAlmostEqual(unknown_ratio, source_missing_rate)
        self.assertEqual(chart_dimension.tolist(), ['Audio', 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'Unknown', 'HVAC'])

    def test_aida_unknown_ratio_matches_source_missing_rate_with_fallback(self):
        df = pd.DataFrame(
            {
                'top_aida': [None, '', 'Phone', 'Unknown', '未分类数据', None],
                'aida_english': ['Media', None, '', 'Audio', '', 'Unknown']
            }
        )
        chart_dimension = build_chart_dimension(df, 'top_aida', 'aida_english')
        source_missing_mask = (
            (df['top_aida'].apply(normalize_dimension_value) == '')
            & (df['aida_english'].apply(normalize_dimension_value) == '')
        )
        source_missing_rate = source_missing_mask.mean()
        unknown_ratio = (chart_dimension == 'Unknown').mean()
        self.assertAlmostEqual(unknown_ratio, source_missing_rate)
        self.assertEqual(chart_dimension.tolist(), ['Media', 'Unknown', 'Phone', 'Audio', 'Unknown', 'Unknown'])

    def test_sort_dimension_with_unknown_last_preserves_unknown_count(self):
        totals = pd.DataFrame(
            {
                'dimension': ['Unknown', 'Audio', 'Phone', '未分类数据'],
                '缺陷数量': [50, 30, 20, 10]
            }
        )
        ordered = sort_dimension_with_unknown_last(totals, 'dimension')
        self.assertEqual(ordered, ['Audio', 'Phone', 'Unknown', '未分类数据'])
        self.assertEqual(sum(v in {'Unknown', '未分类数据'} for v in ordered), 2)


if __name__ == '__main__':
    unittest.main()
