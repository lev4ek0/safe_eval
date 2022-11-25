from datetime import datetime

import pandas as pd

from unittest import TestCase


class BaseTestCase(TestCase):

    @staticmethod
    def _create_df():
        dates = [datetime(year=2022, month=11, day=11 + i) for i in range(7)]
        return pd.DataFrame({
            'col1': [1, 1, 2, 2, 3, 3, 4],
            'col2': [1, 1, 1, 2, 2, 2, 3],
            'col3': dates,
            'col4': ['dq', 'QW', 'Gh', 'Jh', '67', '-=', '.,'],
            'target': [1, 2, 3, 4, 5, 6, 7]
        }), ['col1', 'col2', 'col3', 'target']  # len = 7
