from safe_evaluation.expressions import solve_expression

from tests.base import BaseTestCase


class TestProperties(BaseTestCase):

    def test_dtype(self):
        df, columns = self._create_df()
        expression = solve_expression("${col3}.dtype", df)

        self.assertEqual(expression, df["col3"].dtype)

    def test_dt_day(self):
        df, columns = self._create_df()
        expression = solve_expression("${col3}.dt.day", df).values.tolist()
        self.assertEqual(expression, [11, 12, 13, 14, 15, 16, 17])

    def test_str_lower(self):
        df, columns = self._create_df()
        expression = solve_expression("${col4}.str.lower()", df).values.tolist()
        self.assertEqual(expression, ['dq', 'qw', 'gh', 'jh', '67', '-=', '.,'])

    def test_dt_day_of_week(self):
        df, columns = self._create_df()
        expression = solve_expression("${col3}.dt.dayofweek", df).values.tolist()
        self.assertEqual(expression, [4, 5, 6, 0, 1, 2, 3])

    def test_empty(self):
        df, columns = self._create_df()
        expression = solve_expression("${col3}.empty", df)
        self.assertEqual(expression, False)

    def test_shape(self):
        df, columns = self._create_df()
        expression = solve_expression("${col3}.shape", df)
        self.assertEqual(expression, (7,))

    def test_index(self):
        df, columns = self._create_df()
        expression = solve_expression("${col3}.index", df)
        expression_index = [expression.start, expression.stop, expression.step]
        df_index = [df['col3'].index.start, df['col3'].index.stop, df['col3'].index.step]
        self.assertEqual(expression_index, df_index)