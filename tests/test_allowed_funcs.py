from safe_evaluation import solve_expression
from unittest import TestCase


class TestAllowedFuncs(TestCase):

    def test_literal_eval(self):
        expression = solve_expression("[1,2,3,4]")
        self.assertEqual(expression, (1, 2, 3, 4))

    def test_map(self):
        expression = solve_expression("map(lambda x, y: x + 2 + y, [1,2], [10, 20])")
        self.assertEqual(list(expression), [13, 24])

    def test_list(self):
        expression = solve_expression("list(map(lambda x, y: x + 2 + y, [1,2], [10, 20]))")
        self.assertEqual(expression, [13, 24])

    def test_filter(self):
        expression = solve_expression("filter(lambda x: x % 2 == 0, [0,1,2,3,4,5])")
        self.assertEqual(list(expression), [0, 2, 4])

    def test_range(self):
        expression = solve_expression("range(6)")
        self.assertEqual(expression, range(6))

    def test_range_step(self):
        expression = solve_expression("range(6, 13, 3)")
        self.assertEqual(list(expression), [6, 9, 12])

    def test_eval(self):
        with self.assertRaises(Exception):
            solve_expression("eval(2 + 2)")
