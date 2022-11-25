from safe_evaluation import solve_expression

from tests.base import BaseTestCase


class TestIfElse(BaseTestCase):

    def test_default(self):
        df, columns = self._create_df()
        command = "0 if v < 9 else 10"
        expression = solve_expression(command=command, df=df, local={'v': 5})
        self.assertEqual(expression, 0)

    def test_brackets_0(self):
        df, columns = self._create_df()
        command = "2 if v < 2 else (0 if v < 8 else 1) | (v == 5)"
        expression = solve_expression(command=command, df=df, local={'v': 1})
        self.assertEqual(expression, 2)

    def test_brackets_1(self):
        df, columns = self._create_df()
        command = "2 if v < 2 else (0 if v < 8 else 1) | (v == 5)"
        expression = solve_expression(command=command, df=df, local={'v': 7})
        self.assertEqual(expression, 0)

    def test_brackets_2(self):
        df, columns = self._create_df()
        command = "2 if v < 2 else (0 if v < 8 else 1) | (v == 5)"
        expression = solve_expression(command=command, df=df, local={'v': 5})
        self.assertEqual(expression, 1)

    def test_brackets_3(self):
        df, columns = self._create_df()
        command = "2 if v < 2 else (0 if v < 8 else 1 & (v == 10))"
        expression = solve_expression(command=command, df=df, local={'v': 10})
        self.assertEqual(expression, 1)

    def test_brackets_4(self):
        df, columns = self._create_df()
        command = "2 if v < 2 else (0 if v < 8 else 1 & (v == 10))"
        expression = solve_expression(command=command, df=df, local={'v': 9})
        self.assertEqual(expression, 0)

    def test_brackets_5(self):
        df, columns = self._create_df()
        command = "2 if v < 2 else (0 if v < 8 else 1 & v == 10)"
        expression = solve_expression(command=command, df=df, local={'v': 10})
        self.assertEqual(expression, False)

    def test_apply_inside(self):
        df, columns = self._create_df()
        command = "${col1}.apply(lambda v: 0 if v < 2 else (1 if v < 3 else 2))"
        expression = solve_expression(command=command, df=df).values.tolist()
        self.assertEqual(expression, [0, 0, 1, 1, 2, 2, 2])

    def test_inside(self):
        df, columns = self._create_df()
        command = "0 if v < 2 else (1 if v < 3 else 2)"
        expression = solve_expression(command=command, df=df, local={'v': 1})
        self.assertEqual(expression, 0)
