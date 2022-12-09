from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from safe_evaluation import solve_expression

from tests.base import BaseTestCase


class TestFactory(BaseTestCase):

    def test_lambda_multiple_variables(self):
        function_str = solve_expression("lambda a, b, c, d: a + b - c * d")
        function_code = lambda a, b, c, d: a + b - c * d
        self.assertEqual(function_str(1, 2, 3, 4), function_code(1, 2, 3, 4))

    def test_np_mean(self):
        function_str = solve_expression("np.mean")
        function_code = np.mean
        self.assertEqual(function_str(list(range(100))), function_code(list(range(100))))

    def test_numpy_mean(self):
        function_str = solve_expression("numpy.mean")
        function_code = np.mean
        self.assertEqual(function_str(list(range(100))), function_code(list(range(100))))

    def test_pandas_date_range(self):
        function_str = solve_expression("pandas.date_range")
        function_code = pd.date_range
        start = datetime(year=2021, month=2, day=5)
        end = datetime(year=2021, month=3, day=5)
        freq = timedelta(days=1)
        self.assertEqual(
            list(function_str(start=start, end=end, freq=freq)),
            list(function_code(start=start, end=end, freq=freq))
        )

    def test_pd_date_range(self):
        function_str = solve_expression("pd.date_range")
        function_code = pd.date_range
        start = datetime(year=2021, month=2, day=5)
        end = datetime(year=2021, month=3, day=5)
        freq = timedelta(days=1)
        self.assertEqual(
            list(function_str(start=start, end=end, freq=freq)),
            list(function_code(start=start, end=end, freq=freq))
        )

    def test_pd_date_range_params(self):
        expression = solve_expression("pd.date_range(start='2021-02-05', end='2021-03-05', freq='1D')")
        self.assertEqual(len(expression), 29)

    def test_np_mean_lambda_kwargs(self):
        function_str = solve_expression("lambda a, axis: np.mean(a=a, axis=axis)")
        function_code = lambda a, axis: np.mean(a=a, axis=axis)
        self.assertEqual(function_str(list(range(100)), None), function_code(list(range(100)), None))

    def test_np_mean_lambda_args(self):
        function_str = solve_expression("lambda a, axis: np.mean(a, axis)")
        function_code = lambda a, axis: np.mean(a, axis)
        self.assertEqual(function_str(list(range(100)), None), function_code(list(range(100)), None))

    def test_np_mean_lambda_mixed_args(self):
        function_str = solve_expression("lambda a, axis: np.mean(a, axis=axis)")
        function_code = lambda a, axis: np.mean(a, axis=axis)
        self.assertEqual(function_str(list(range(100)), None), function_code(list(range(100)), None))

    def test_np_mean_lambda_inversed_args(self):
        function_str = solve_expression("lambda a, axis: np.mean(a=a, axis)")
        with self.assertRaises(SyntaxError):
            function_str(list(range(100)), None)

    def test_sort_values(self):
        df, columns = self._create_df()
        sorted_df = solve_expression("${[df]}.sort_values('col3')", df=df)
        self.assertEqual(sorted_df['col3'].values.tolist(), sorted(df['col3'].values.tolist()))

    def test_sort_values_ascending(self):
        df, columns = self._create_df()
        sorted_df = solve_expression("${[df]}.sort_values('col3', ascending=False)", df=df)
        self.assertEqual(sorted_df['col3'].values.tolist(), sorted(df['col3'].values.tolist(), reverse=True))

    def test_sort_values_by(self):
        df, columns = self._create_df()
        sorted_df = solve_expression("${[df]}.sort_values(['col3', 'col2'])", df=df)
        self.assertEqual(
            list(map(lambda x: tuple(x), sorted_df[['col3', 'col2']].astype(int).values.tolist())),
            sorted(zip(df['col3'].values.tolist(), df['col2'].values.tolist()), key=lambda x: (x[0], x[1]))
        )

    def test_sort_values_ignore_index(self):
        df, columns = self._create_df()
        sorted_df = solve_expression("${[df]}.sort_values('col3', ignore_index=True, ascending=False)", df=df)
        self.assertEqual(sorted_df.index.values.tolist(), [_ for _ in range(len(df))])
