from safe_evaluation import Preprocessor, Evaluator

from tests.base import BaseTestCase


evaluator = Evaluator()
_is_valid_parentheses = Preprocessor(evaluator)._is_valid_parentheses


class TestParentheses(BaseTestCase):

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
