import pandas as pd

from safe_evaluation.expressions import _polish_notation, TypeOfCommand
from unittest import TestCase


class TestParentheses(TestCase):
    @staticmethod
    def _create_df():
        return pd.DataFrame({
            'col1': [1, 1, 2, 2, 3, 3, 4],
            'col2': [1, 1, 1, 2, 2, 2, 3],
            'target': [1, 2, 3, 4, 5, 6, 7]
        }), ['col1', 'col2', 'target']  # len = 7

    def test_polish_notation_default(self):
        df, df_columns = self._create_df()
        stack = ['(', (TypeOfCommand.COLUMN, 'col1'), '<=', (TypeOfCommand.VALUE, 2), ')']
        notation = _polish_notation(stack, df).values.tolist()
        result = [True, True, True, True, False, False, False]
        self.assertEqual(notation, result)

    def test_polish_notation_columns(self):
        df, df_columns = self._create_df()
        stack = ['(', (TypeOfCommand.COLUMN, 'col1'), '<=', (TypeOfCommand.COLUMN, 'col2'), ')']
        notation = _polish_notation(stack, df).values.tolist()
        result = [True, True, False, True, False, False, False]
        self.assertEqual(notation, result)

    def test_polish_notation_ne(self):
        df, df_columns = self._create_df()
        stack = ['~', '(', (TypeOfCommand.COLUMN, 'col1'), '<=', (TypeOfCommand.COLUMN, 'col2'), ')']
        notation = _polish_notation(stack, df).values.tolist()
        result = [False, False, True, False, True, True, True]
        self.assertEqual(notation, result)

    def test_polish_notation_ne_ne_ne(self):
        df, df_columns = self._create_df()
        stack = ['~', '~', '~', '(', (TypeOfCommand.COLUMN, 'col1'), '<=', (TypeOfCommand.COLUMN, 'col2'), ')']
        notation = _polish_notation(stack, df).values.tolist()
        result = [False, False, True, False, True, True, True]
        self.assertEqual(notation, result)

    def test_polish_notation_numbers(self):
        df, df_columns = self._create_df()
        stack = ['(', (TypeOfCommand.VALUE, 1), '<=', (TypeOfCommand.VALUE, 2), ')']
        notation = _polish_notation(stack, df)
        result = True
        self.assertEqual(notation, result)

    def test_polish_notation_xor(self):
        df, df_columns = self._create_df()
        stack = ['(', (TypeOfCommand.COLUMN, 'col1'), '<=', (TypeOfCommand.COLUMN, 'col2'), ')', '^', '(',
                 (TypeOfCommand.COLUMN, 'col1'), '>', (TypeOfCommand.VALUE, 1), ')']
        notation = _polish_notation(stack, df).values.tolist()
        result = [True, True, True, False, True, True, True]
        self.assertEqual(notation, result)

    def test_polish_notation_and(self):
        df, df_columns = self._create_df()
        stack = ['(', (TypeOfCommand.COLUMN, 'col1'), '<=', (TypeOfCommand.COLUMN, 'col2'), ')', '&', '(',
                 (TypeOfCommand.COLUMN, 'col1'), '>', (TypeOfCommand.VALUE, 1), ')']
        notation = _polish_notation(stack, df).values.tolist()
        result = [False, False, False, True, False, False, False]
        self.assertEqual(notation, result)

    def test_polish_notation_or(self):
        df, df_columns = self._create_df()
        stack = ['(', (TypeOfCommand.COLUMN, 'col1'), '<=', (TypeOfCommand.COLUMN, 'col2'), ')', '|', '(',
                 (TypeOfCommand.COLUMN, 'col1'), '>', (TypeOfCommand.VALUE, 1), ')']
        notation = _polish_notation(stack, df).values.tolist()
        result = [True for _ in range(7)]
        self.assertEqual(notation, result)

    def test_right_associated(self):
        df, df_columns = self._create_df()
        stack = [(TypeOfCommand.VALUE, 2), '**', (TypeOfCommand.VALUE, 3), '**', (TypeOfCommand.VALUE, 4)]
        notation = _polish_notation(stack, df)
        result = 2 ** 3 ** 4
        self.assertEqual(notation, result)

    def test_priority_1(self):
        df, df_columns = self._create_df()
        stack = [(TypeOfCommand.VALUE, 2), '+', (TypeOfCommand.VALUE, 2), '*', (TypeOfCommand.VALUE, 2)]
        notation = _polish_notation(stack, df)
        result = 2 + 2 * 2
        self.assertEqual(notation, result)

    def test_priority_2(self):
        df, df_columns = self._create_df()
        stack = ['(', (TypeOfCommand.VALUE, 12), '%', (TypeOfCommand.VALUE, 100), '/',
                 (TypeOfCommand.VALUE, 2), '-', '(', (TypeOfCommand.VALUE, 2), '-',
                 (TypeOfCommand.VALUE, 10), ')', ')', '//', (TypeOfCommand.VALUE, 3), '+',
                 (TypeOfCommand.VALUE, 10.1), '**', (TypeOfCommand.VALUE, 1)]
        notation = _polish_notation(stack, df)
        result = (12 % 100 / 2 - (2 - 10)) // 3 + 10.1 ** 1
        self.assertEqual(notation, result)

    def test_priority_3(self):
        df, df_columns = self._create_df()
        stack = [(TypeOfCommand.VALUE, 3.0), '*', (TypeOfCommand.VALUE, 5.0), '**',
                 (TypeOfCommand.VALUE, 2.0), '/', (TypeOfCommand.VALUE, 2.0), '**',
                 (TypeOfCommand.VALUE, 3.0), '%', '(', (TypeOfCommand.VALUE, 10.0), '/',
                 (TypeOfCommand.VALUE, 2.0), '+', (TypeOfCommand.VALUE, 8.888), ')', '%',
                 (TypeOfCommand.VALUE, 10.0), '**', (TypeOfCommand.VALUE, 2.0), '%',
                 (TypeOfCommand.VALUE, 3.0)]
        notation = _polish_notation(stack, df)
        result = 3 * 5 ** 2 / 2 ** 3 % (10 / 2 + 8.888) % 10 ** 2 % 3
        self.assertEqual(notation, result)

    def test_local_var(self):
        df, df_columns = self._create_df()
        stack = [(TypeOfCommand.VARIABLE, 'v'), '**', (TypeOfCommand.VALUE, 2), '>', (TypeOfCommand.VALUE, 5)]
        notation = _polish_notation(stack, df, {'v': 2})
        result = False
        self.assertEqual(notation, result)

    def test_cycled_applies(self):
        df, df_columns = self._create_df()
        # df['col1'].apply(lambda t: (t == 1) & df['col1'].apply(lambda v: v >= df['col2'].max() + 1)).max()
        stack = [(TypeOfCommand.COLUMN, 'col1'),
                 (TypeOfCommand.METHOD, 'lambda t: (t == 1) & ${col1}.apply(lambda v: v >= ${col2}.max() + 1)', 'apply'),
                 (TypeOfCommand.METHOD, '', 'max')]
        notation = _polish_notation(stack, df).values.tolist()
        result = [False, False, False, False, False, False, True]
        self.assertEqual(notation, result)

    def test_astype(self):
        df, df_columns = self._create_df()
        stack = [(TypeOfCommand.COLUMN, 'col1'),
                 (TypeOfCommand.METHOD, '"str", copy=True', 'astype')]
        notation = _polish_notation(stack, df).values.tolist()
        result = ['1', '1', '2', '2', '3', '3', '4']
        self.assertEqual(notation, result)

    def test_max(self):
        df, df_columns = self._create_df()
        df[2:3] = 7
        stack = [(TypeOfCommand.COLUMN, 'col1'),
                 (TypeOfCommand.METHOD, '', 'max')]
        notation = _polish_notation(stack, df)
        result = 7  # result of max method by one Series is a single number
        self.assertEqual(notation, result)

    def test_quantile(self):
        df, df_columns = self._create_df()
        stack = [(TypeOfCommand.COLUMN, 'col1'),
                 (TypeOfCommand.METHOD, 'q=0.7', 'quantile')]
        notation = _polish_notation(stack, df)
        result = [3]
        self.assertEqual(notation, result)

    def test_apply(self):
        df, df_columns = self._create_df()
        stack = [(TypeOfCommand.COLUMN, 'col1'),
                 (TypeOfCommand.METHOD, ' func = lambda v: v <= 2', 'apply')]
        notation = _polish_notation(stack, df).values.tolist()
        result = [True, True, True, True, False, False, False]
        self.assertEqual(notation, result)

    def test_method_exception(self):
        df, df_columns = self._create_df()
        stack = [(TypeOfCommand.VALUE, 'col1'),
                 (TypeOfCommand.METHOD, 'lambda t: (t == 1) & ${col1}.apply(lambda v: v >= ${col2}.max() + 1)', 'apply')]
        with self.assertRaises(Exception):
            _polish_notation(stack, df)

    def test_analyse_exception(self):
        df, df_columns = self._create_df()
        stack = [(TypeOfCommand.COLUMN, 'col1'),
                 (TypeOfCommand.METHOD, 'int', 'astype')]
        with self.assertRaises(Exception):
            _polish_notation(stack, df)

    def test_operation_exception(self):
        df, df_columns = self._create_df()
        stack = ["*", "*"]
        with self.assertRaises(Exception):
            _polish_notation(stack, df)

    def test_local_var_not_exist(self):
        df, df_columns = self._create_df()
        stack = [(TypeOfCommand.VARIABLE, 'v'), '**', (TypeOfCommand.VALUE, 2), '>', (TypeOfCommand.VALUE, 5)]
        with self.assertRaises(Exception):
            _polish_notation(stack, df, {'b': 2})

    def test_method_not_exist(self):
        df, df_columns = self._create_df()
        stack = [(TypeOfCommand.COLUMN, 'col1'), (TypeOfCommand.METHOD, '', 'maxi')]
        with self.assertRaises(Exception):
            _polish_notation(stack, df)
