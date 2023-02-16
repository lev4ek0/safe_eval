import re
from abc import ABCMeta, abstractmethod
from typing import List, Union, Optional

import pandas as pd

from safe_evaluation.constants import TypeOfCommand, OPERATORS_PRIORITIES


class BaseCalculator(metaclass=ABCMeta):
    @abstractmethod
    def calculate(self, stack, df, local):
        pass


class Calculator(BaseCalculator):
    operators_priorities = OPERATORS_PRIORITIES

    def __init__(self, evaluator):
        self.evaluator = evaluator

    def _analyse(self, string, df=None, local=None):
        """
        Analyses args of the method
        Returns arg in correct format(string, float, bool or lambda)
        """
        if local and string in local:
            return local[string]

        return self.evaluator.solve(string, df, local)

    def _is_arg(self, string):
        """
        Checks if argument is arg or kwarg
        """

        if re.match(r' *[\w]* *=', string):
            return False
        return True

    def _split_params(self, s: str):
        """
        Splits params of method by comma
        """

        # todo: handle "(", ")" as name of column
        stack = []
        brackets = {'(': ')', '{': '}', '[': ']'}
        brackets_possible = {'(', ')', '{', '}', '[', ']'}
        pos = amount = prev = 0
        answer = []

        for element in s:
            if element in brackets_possible:
                if element in brackets:
                    stack.append((element, pos))
                    amount += 1
                else:
                    amount -= 1
                    if not stack or brackets[stack.pop()[0]] != element:
                        self.evaluator.raise_excess_parentheses(s, pos)
            lambda_start = re.match(r' *lambda .*', s[prev: pos])
            whole_lambda = re.match(r' *lambda [^:]*:', s[prev: pos])
            if amount == 0 and element == ',' and (not lambda_start or (lambda_start and whole_lambda)):
                answer.append(s[prev:pos].strip())
                prev = pos + 1
            pos += 1

        if stack:
            self.evaluator.raise_excess_parentheses(s, stack[-1][1])
        answer.append(s[prev:].strip())
        return answer

    def _solve_inside_method(self, command, df, local):
        """
        Gets args as command inside the method
        Returns args and kwargs
        example:
            command = "lambda t: t ** 2 > 34, q = 0.5"
            returns: [Lambda], {q: 0.5}
        """

        if not command:
            return [], {}

        params = self._split_params(command)
        args = []
        kwargs = {}
        are_args = True
        for param in params:
            if self._is_arg(param):
                if not are_args:
                    raise SyntaxError("Positional argument follows keyword argument")
                arg = self._analyse(param, df, local)
                args.append(arg)
            else:
                are_args = False
                keyword = param.split('=')[0].replace(' ', '')
                arg = self._analyse(param.split('=', maxsplit=1)[1], df, local)
                kwargs[keyword] = arg
        return args, kwargs

    def _get_variable(self, var, df, local) -> pd.Series:
        """
        Returns series format for any var.
        """
        variable = None
        if isinstance(var, tuple):
            if var[0] == TypeOfCommand.VALUE:
                variable = var[1]
            elif var[0] == TypeOfCommand.COLUMN:
                try:
                    variable = df[var[1]]
                except KeyError:
                    raise KeyError(('The input DataFrame doesn\'t contain "{var}" column').format(var=f'{var[1]}'))
            elif var[0] == TypeOfCommand.DATAFRAME:
                if len(var) == 1:
                    variable = df
                else:
                    variable = df[var[1]]
            elif var[0] == TypeOfCommand.VARIABLE:
                if local and var[1] in local:
                    variable = local[var[1]]
                else:
                    raise Exception(('Variable "{var}" doesn\'t exist').format(var=f'{var[1]}'))
        else:
            variable = var
        return var if variable is None else variable

    def _raise_operation_cant_be_applied(self, stack, op):
        if not stack:
            raise Exception(('Operation "{operation}" can\'t be applied to Nothing').format(operation=op))

    def _operate(self, stack, op, df, local):
        """
        Calculates result of operations.
        """

        if op == '~':
            self._raise_operation_cant_be_applied(stack, op)
            l = stack.pop()

            var1 = self._get_variable(l, df, local)
            stack.append(self.evaluator.operators[op](var1))
        else:
            self._raise_operation_cant_be_applied(stack, op)
            r = stack.pop()
            self._raise_operation_cant_be_applied(stack, op)
            l = stack.pop()
            var1 = self._get_variable(l, df, local)

            if isinstance(r, tuple) and r[0] == TypeOfCommand.METHOD:
                if hasattr(var1, r[2]):
                    if r[2] in {'apply', 'quantile'} and not isinstance(var1, (pd.Series, pd.DataFrame)):
                        raise Exception(('Method "{method}" can only be applied to Series or Dataframe, not {type}')
                                        .format(method=r[2], type=type(var1)))
                    args, kwargs = self._solve_inside_method(r[1], df, local)
                    args = [list(arg) if isinstance(arg, tuple) else arg for arg in args]
                    kwargs = {k: list(v) if isinstance(v, tuple) else v for k, v in kwargs.items()}
                    stack.append(getattr(var1, r[2])(*args, **kwargs))
                else:
                    raise Exception(('Method "{method}" doesn\'t exist').format(method=r[2]))
            elif isinstance(r, tuple) and r[0] == TypeOfCommand.PROPERTY:
                if hasattr(var1, r[1]):
                    var1 = self._get_variable(l, df, local)
                    stack.append(getattr(var1, r[1]))
                else:
                    raise Exception(('Method "{method}" doesn\'t exist').format(method=r[1]))
            else:
                var1 = self._get_variable(l, df, local)
                var2 = self._get_variable(r, df, local)
                stack.append(self.evaluator.operators[op](var1, var2))

    def _polish_notation(self, s: List[Union[str, tuple]], df: Optional[pd.DataFrame] = None, local: dict = None):
        """
        Returns result of command.
        https://e-maxx.ru/algo/expressions_parsing
        """

        stack = []
        op = []

        for element in s:
            if element == '(':
                op.append(element)
            elif element == ')':
                while op[-1] != '(':
                    self._operate(stack, op.pop(), df, local)
                op.pop()
            elif element in self.evaluator.operators.keys():
                curop = element
                # {'~', '**'} are right associated
                while op and ((curop not in {'~', '**'} and
                               self.operators_priorities.get(op[-1], -1) >= self.operators_priorities.get(curop, -1)) or
                              (curop in {'~', '**'} and
                               self.operators_priorities.get(op[-1], -1) > self.operators_priorities.get(curop, -1))):
                    self._operate(stack, op.pop(), df, local)
                op.append(curop)
            else:
                stack.append(element)
                if element[0] in (TypeOfCommand.METHOD, TypeOfCommand.PROPERTY):
                    self._operate(stack, '', df, local)
                if element[0] == TypeOfCommand.FUNCTION_EXECUTABLE:
                    r = stack.pop()
                    args, kwargs = self._solve_inside_method(r[1], df, local)
                    stack.append(self.evaluator.handle_function(r[2])(*args, **kwargs))
                if element[0] == TypeOfCommand.FUNCTION:
                    r = stack.pop()
                    if stack:
                        raise Exception("There can't be function and something else")
                    return r[1]

        while op:
            self._operate(stack, op.pop(), df, local)
        if len(stack) > 1:
            raise Exception("2 or more elements left without operations")
        value = stack.pop()
        return self._get_variable(value, df, local)

    def calculate(self, stack, df, local):
        output = self._polish_notation(stack, df, local)
        return output

