from safe_evaluation.expressions import _get_stack, TypeOfCommand
from unittest import TestCase


class TestStack(TestCase):

    def test_stack_parentheses(self):
        expression = '()'
        result = ['(', ')']
        self.assertEqual(_get_stack(expression), result)

    def test_stack_columns_and_columns(self):
        expression = '(${col1} != ${col2})'
        result = ['(', (TypeOfCommand.COLUMN, 'col1'), '!=', (TypeOfCommand.COLUMN, 'col2'), ')']
        self.assertEqual(_get_stack(expression), result)

    def test_stack_columns_and_values(self):
        expression = '(${col1} != \'col2\')'
        result = ['(', (TypeOfCommand.COLUMN, 'col1'), '!=', (TypeOfCommand.VALUE, 'col2'), ')']
        self.assertEqual(_get_stack(expression), result)

    def test_double_quote(self):
        expression = '(${col1} != \"col2\")'
        result = ['(', (TypeOfCommand.COLUMN, 'col1'), '!=', (TypeOfCommand.VALUE, 'col2'), ')']
        self.assertEqual(_get_stack(expression), result)

    def test_empty_stack(self):
        expression = ''
        result = []
        self.assertEqual(_get_stack(expression), result)

    def test_wrong_symbol_stack_1(self):
        expression = '({col1} != \'col2\')'
        with self.assertRaises(Exception):
            _get_stack(expression)

    def test_parenthesis_in_column_name(self):
        expression = '(${co}l1} != \'col2\')'
        with self.assertRaises(Exception):
            _get_stack(expression)

    def test_condition_less(self):
        expression = '(${col1} < \"col2\")'
        result = ['(', (TypeOfCommand.COLUMN, 'col1'), '<', (TypeOfCommand.VALUE, 'col2'), ')']
        self.assertEqual(_get_stack(expression), result)

    def test_condition_double_less(self):
        expression = '(${col1} << \"col2\")'
        result = ['(', (TypeOfCommand.COLUMN, 'col1'), '<', '<', (TypeOfCommand.VALUE, 'col2'), ')']
        self.assertEqual(_get_stack(expression), result)

    def test_condition_double_gtl(self):
        expression = '(${col1} <<= \"col2\")'
        result = ['(', (TypeOfCommand.COLUMN, 'col1'), '<', '<=', (TypeOfCommand.VALUE, 'col2'), ')']
        self.assertEqual(_get_stack(expression), result)

    def test_max_empty(self):
        expression = '(${col1}.max())'
        result = ['(', (TypeOfCommand.COLUMN, 'col1'), (TypeOfCommand.METHOD, '', 'max'), ')']
        self.assertEqual(_get_stack(expression), result)

    def test_max_params(self):
        expression = '(${col1}.max(level=1, numeric_only=True))'
        result = ['(', (TypeOfCommand.COLUMN, 'col1'), (TypeOfCommand.METHOD, 'level=1, numeric_only=True', 'max'), ')']
        self.assertEqual(_get_stack(expression), result)

    def test_methods_sequence(self):
        expression = '(${col1}.max(level=1, numeric_only=True).apply(lambda v: v ** 2 < 1))'
        result = ['(', (TypeOfCommand.COLUMN, 'col1'), (TypeOfCommand.METHOD, 'level=1, numeric_only=True', 'max'),
                  (TypeOfCommand.METHOD, 'lambda v: v ** 2 < 1', 'apply'), ')']
        self.assertEqual(_get_stack(expression), result)

    def test_astype(self):
        expression = '(${col1}.astype(int8))'
        result = ['(', (TypeOfCommand.COLUMN, 'col1'), (TypeOfCommand.METHOD, 'int8', 'astype'), ')']
        self.assertEqual(_get_stack(expression), result)

    def test_apply(self):
        expression = '(${col1}.apply(lambda v: v ** 2 > 5))'
        result = ['(', (TypeOfCommand.COLUMN, 'col1'), (TypeOfCommand.METHOD, 'lambda v: v ** 2 > 5', 'apply'), ')']
        self.assertEqual(_get_stack(expression), result)

    def test_local_var(self):
        expression = 'v ** 2 > 5'
        result = [(TypeOfCommand.VARIABLE, 'v'), '**', (TypeOfCommand.VALUE, 2), '>', (TypeOfCommand.VALUE, 5)]
        self.assertEqual(_get_stack(expression, {'v': 2}), result)
