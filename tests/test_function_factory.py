import numpy as np

from safe_evaluation import solve_expression
from unittest import TestCase


class TestFactory(TestCase):

    def test_lambda_multiple_variables(self):
        function_str = solve_expression("lambda a, b, c, d: a + b - c * d")
        function_code = lambda a, b, c, d: a + b - c * d
        self.assertEqual(function_str(1, 2, 3, 4), function_code(1, 2, 3, 4))

    def test_np_mean(self):
        function_str = solve_expression("np.mean")
        function_code = np.mean
        self.assertEqual(function_str(list(range(100))), function_code(list(range(100))))

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
