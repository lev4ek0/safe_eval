from tests.base import BaseTestCase


class TestAllowedFuncs(BaseTestCase):

    def test_literal_eval(self):
        expression = self.expression.solve("[1,2,3,4]")
        self.assertEqual(expression, (1, 2, 3, 4))

    def test_map(self):
        expression = self.expression.solve("map(lambda x, y: x + 2 + y, [1,2], [10, 20])")
        self.assertEqual(list(expression), [13, 24])

    def test_list(self):
        expression = self.expression.solve("list(map(lambda x, y: x + 2 + y, [1,2], [10, 20]))")
        self.assertEqual(expression, [13, 24])

    def test_filter(self):
        expression = self.expression.solve("filter(lambda x: x % 2 == 0, [0,1,2,3,4,5])")
        self.assertEqual(list(expression), [0, 2, 4])

    def test_range(self):
        expression = self.expression.solve("range(6)")
        self.assertEqual(expression, range(6))

    def test_range_step(self):
        expression = self.expression.solve("range(6, 13, 3)")
        self.assertEqual(list(expression), [6, 9, 12])

    def test_eval(self):
        with self.assertRaises(Exception):
            self.expression.solve("eval(2 + 2)")

    def test_int(self):
        df, columns = self._create_df()
        expression = self.expression.solve("(${col1} < 3).astype(int)", df).values.tolist()
        self.assertEqual(list(expression), [1, 1, 1, 1, 0, 0, 0])

    def test_bool(self):
        df, columns = self._create_df()
        expression = self.expression.solve("${col1}.astype(bool)", df).values.tolist()
        self.assertEqual(list(expression), [True, True, True, True, True, True, True])

    def test_float(self):
        df, columns = self._create_df()
        expression = self.expression.solve("${col1}.astype(float)", df).values.tolist()
        self.assertEqual(list(expression), [1, 1, 2, 2, 3, 3, 4])

    def test_str(self):
        df, columns = self._create_df()
        expression = self.expression.solve("(${col1} < 3).astype(str)", df).values.tolist()
        self.assertEqual(list(expression), ["True", "True", "True", "True", "False", "False", "False"])

    def test_complex(self):
        df, columns = self._create_df()
        expression = self.expression.solve("(${col1} < 3).astype(complex)", df).values.tolist()
        self.assertEqual(list(expression), [1+0j, 1+0j, 1+0j, 1+0j, 0+0j, 0+0j, 0+0j])
