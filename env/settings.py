def _get_settings(division):
    nalf_settings = {
        'a': {
            'table': {
                'link_to_table': 'https://nalffutsal.pl/?page_id=16',
                'table_dividers': None,
                'table_special_fields': {
                    'first-place': [1],
                    'second-place': [2],
                    'third-place': [3],
                    'demotion': [7, 8]
                }
            },
            'nr_of_regular_season_matches': 56,
        },
        'b': {
            'table': {
                'link_to_table': 'https://nalffutsal.pl/?page_id=36',
                'table_dividers': [5],
                'table_special_fields': {
                    'promotion': [1, 2],
                    'demotion': [9, 10, 11]
                }
            },
            'nr_of_regular_season_matches': 55,
        }
    }
    return nalf_settings[division]
