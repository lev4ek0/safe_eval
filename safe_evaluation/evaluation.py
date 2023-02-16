from typing import Callable, Optional

import numpy as np
import pandas as pd

from safe_evaluation.calculation import Calculator
from safe_evaluation.constants import OPERATORS, ALLOWED_FUNCS
from safe_evaluation.preprocessing import Preprocessor
from safe_evaluation.settings import Settings


class Evaluator:
    allowed_funcs = ALLOWED_FUNCS
    operators = OPERATORS

    def __init__(self, preprocessor=Preprocessor, calculator=Calculator):
        self.preprocessor = preprocessor(self)
        self.calculator = calculator(self)
        self.settings = Settings()

    def change_settings(self, settings: Settings):
        self.settings = settings

    def _beautify(self, el):
        """
        Returns string format for the input element
        """
        if isinstance(el, tuple):
            return str(el[1])
        else:
            return str(el)

    def get_prev_and_next(self, s, pos):
        """
        Return previous and next stack elements.
        """

        prev_ = ''.join(map(self._beautify, s[:pos]))
        next_ = ''.join(map(self._beautify, s[pos + 1:]))
        return prev_, next_

    def raise_excess_parentheses(self, s, pos):
        prev_, next_ = self.get_prev_and_next(s, pos)
        raise Exception(('Excess parenthesis at position: "{expression}"').format(
            expression=f'{prev_} --> {s[pos]} <-- {next_}'))

    def handle_function(self, func: str) -> Callable:
        if func.startswith(('numpy', 'np', 'pandas', 'pd')) and self.settings.is_available(func) and '.' in func:
            method = func.split('.')[1]
            package = np if func.startswith('n') else pd
            return getattr(package, method)
        if self.settings.is_available(func):
            return self.allowed_funcs[func]
        raise Exception(f"Unsupported function {func}")

    def solve(self, command: str, df: Optional[pd.DataFrame] = None, local: dict = None):
        stack = self.preprocessor.prepare(command, df, local)
        output = self.calculator.calculate(stack, df, local)
        return output
