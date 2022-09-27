from safe_evaluation.expressions import _is_valid_parentheses
from unittest import TestCase


class TestParentheses(TestCase):

    def test_valid_parentheses_1(self):
        expression = ['(', ')']
        self.assertEqual(_is_valid_parentheses(expression), None)

    def test_valid_parentheses_2(self):
        expression = ['(', ')', '(', '(', '(', ')', '(', ')', ')', '(', ')', ')']
        self.assertEqual(_is_valid_parentheses(expression), None)

    def test_valid_parentheses_3(self):
        expression = ['(', ')', '(', '(', ')', ')', '(', ')', ')', '(', ')', ')']
        with self.assertRaises(Exception):
            _is_valid_parentheses(expression)

    def test_valid_parentheses_extra_one(self):
        expression = [')']
        with self.assertRaises(Exception):
            _is_valid_parentheses(expression)

    def test_valid_parentheses_not_closed(self):
        expression = ['(']
        with self.assertRaises(Exception):
            _is_valid_parentheses(expression)

    def test_valid_parentheses_empty(self):
        expression = []
        self.assertEqual(_is_valid_parentheses(expression), None)
