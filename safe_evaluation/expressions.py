import operator
import re
from ast import literal_eval
from typing import List, Callable, Union, Optional
from enum import Enum

import numpy as np
import pandas as pd


operators = {
    '<=': operator.le,
    '<': operator.lt,
    '>': operator.gt,
    '>=': operator.ge,
    '!=': operator.ne,
    '==': operator.eq,
    'in': operator.contains,  # todo: doesn't work now
    '&': operator.and_,
    '|': operator.or_,
    '^': operator.xor,
    '~': operator.inv,
    '**': operator.pow,
    '+': operator.add,
    '-': operator.sub,
    '/': operator.truediv,
    '//': operator.floordiv,
    '%': operator.mod,
    '*': operator.mul,
}

allowed_funcs = {
    'range': range,
    'map': map,
    'filter': filter,
    'list': list,
}


class Lambda:
    """
    Class for handling parsed lambda functions
    """

    def __init__(self, df, command, variables, local):
        self.df = df
        self.command = command
        self.local = local
        self.variables = variables

    def __call__(self, *values, **k_values):
        """
        Recursively solves expression inside of lambda function
        """
        keys = [x for x in self.variables if x not in k_values]
        kwargs = dict(zip(keys, values)) | k_values | self.local
        indices = solve_expression(self.command, self.df, kwargs)
        return indices


def _get_priority(operation: str) -> int:
    """
    Returns the priority of operation.
    """

    if operation == 'in':
        return 1
    if operation in {'==', '!=', '>=', '>', '<', '<='}:
        return 2
    if operation == '|':
        return 3
    if operation == '^':
        return 4
    if operation == '&':
        return 5
    if operation in {'+', '-'}:
        return 6
    if operation in {'*', '/', '//', '%'}:
        return 7
    if operation == '~':
        return 8
    if operation == '**':
        return 9
    return -1


def _beautify(el):
    """
    Returns string format for the input element
    """
    if isinstance(el, tuple):
        return str(el[1])
    else:
        return str(el)


def _get_prev_and_next(s, pos):
    """
    Return previous and next stack elements.
    """

    prev_ = ''.join(map(_beautify, s[:pos]))
    next_ = ''.join(map(_beautify, s[pos + 1:]))
    return prev_, next_


class TypeOfCommand(Enum):
    """
    Enumeration class to represent parsed data
    """
    COLUMN = 0
    VALUE = 1
    METHOD = 2
    VARIABLE = 3
    FUNCTION_EXECUTABLE = 4
    FUNCTION = 5


def _raise_excess_parentheses(s, pos):
    prev_, next_ = _get_prev_and_next(s, pos)
    raise Exception(('Excess parenthesis at position: "{expression}"').format(
        expression=f'{prev_} --> {s[pos]} <-- {next_}'))


def _text_inside_parentheses(s: str):
    """
    Returns false if parentheses is not valid
    Returns text inside the outer parentheses
    s:
        example: ['(1)((2)3(4))'] -> 1
        example: ['((2)3(4))'] -> (2)3(4)
    """

    # todo: handle "(", ")" as name of column
    stack = []
    brackets = {'(': ')'}
    brackets_possible = {'(', ')'}
    pos = 0
    amount = -1

    for element in s:
        if element in brackets_possible:
            if element in brackets:
                if amount == -1:
                    amount += 1
                    start = pos
                amount += 1
                stack.append((element, pos))
            else:
                amount -= 1
                if not stack or brackets[stack.pop()[0]] != element:
                    _raise_excess_parentheses(s, pos)
        pos += 1
        if amount == 0:
            return s[start + 1:pos - 1]

    if stack:
        _raise_excess_parentheses(s, stack[-1][1])


def if_else_function(before, middle, end, df, local):
    if solve_expression(command=middle, df=df, local=local):
        value = solve_expression(command=before, df=df, local=local)
    elif end.strip():
        value = solve_expression(command=end, df=df, local=local)
    else:
        value = None
    return value


def _get_stack(command: str, local: dict = None, df = None) -> List[str]:
    """
    Returns splitted command.
    """
    if local is None:
        local = {}

    stack = []
    i = 0

    while i < len(command):
        if if_else_pattern := re.match(r'[^\(\:]*if((?!if|else).)*(else)?[^)]*', command[i:]):
            if_else_string = command[i:i+if_else_pattern.regs[0][1]]
            before_if = re.match(r'((?!if).)*', if_else_string)
            middle_if = re.match(r'((?!else).)*', if_else_string[2 + before_if.regs[0][1]:])
            endif = if_else_string[2 + before_if.regs[0][1] + 4 + middle_if.regs[0][1]:]
            stack.append((TypeOfCommand.FUNCTION, if_else_function(before_if.group(0), middle_if.group(0), endif, df, local)))
            i += if_else_pattern.regs[0][1] - 1
        elif command[i] in {'(', ')'}:
            stack.append(command[i])
        # mathing columns with ${column} format
        elif command[i] == '$':
            # todo: handle "{", "}" as name of column
            column_pattern = re.match(r'\${[^\{\}]+}', command[i:])
            stack.append((TypeOfCommand.COLUMN, column_pattern.string[2:column_pattern.regs[0][1] - 1]))
            i += column_pattern.regs[0][1] - 1
        elif command[i] == '.':
            method_pattern = re.match(r'\.[\w]+\(.*\)', command[i:])
            command_outer = method_pattern.string[:method_pattern.regs[0][1]]
            method_name_pattern = re.match(r'\.[\w]+', command_outer)
            command_inner = _text_inside_parentheses(command_outer)
            stack.append((TypeOfCommand.METHOD, command_inner, method_name_pattern.string[1:method_name_pattern.regs[0][1]]))
            i += method_name_pattern.regs[0][1] + len(command_inner) + 1
        elif function_pattern := re.match(r'[\w.]+\(.*\)', command[i:]):
            command_outer = function_pattern.string[:function_pattern.regs[0][1]]
            function_name_pattern = re.match(r'[\w.]+', command_outer)
            command_inner = _text_inside_parentheses(command_outer)
            stack.append(
                (TypeOfCommand.FUNCTION_EXECUTABLE, command_inner, function_name_pattern.string[:function_name_pattern.regs[0][1]]))
            i += function_name_pattern.regs[0][1] + len(command_inner) + 1
        # mathing strings with 'string' format
        elif command[i] == '\'':
            string_pattern = re.match(r'\'[^\']+\'', command[i:])
            stack.append((TypeOfCommand.VALUE, string_pattern.string[1:string_pattern.regs[0][1] - 1]))
            i += string_pattern.regs[0][1] - 1
        elif command[i] == '\"':
            string_pattern = re.match(r'\"[^\"]+\"', command[i:])
            stack.append((TypeOfCommand.VALUE, string_pattern.string[1:string_pattern.regs[0][1] - 1]))
            i += string_pattern.regs[0][1] - 1
        elif list_pattern := re.match(r'\[[^\]]+\]', command[i:]):
            stack.append((TypeOfCommand.VALUE, literal_eval(list_pattern.string[1:list_pattern.regs[0][1] - 1])))
            i += list_pattern.regs[0][1]
        elif command[i:i + 2] in operators:
            stack.append(command[i:i + 2])
            i += 1
        elif command[i] in operators:
            stack.append(command[i])
        # mathing floats and ints
        elif number_pattern := re.match(r'[-+]?\d*\.?\d+', command[i:]):
            if float_number_pattern := re.match(r'[-+]?\d+\.\d+', command[i:]):
                stack.append((TypeOfCommand.VALUE, float(float_number_pattern.string[:float_number_pattern.regs[0][1]])))
                i += float_number_pattern.regs[0][1] - 1
            else:
                stack.append((TypeOfCommand.VALUE, int(number_pattern.string[:number_pattern.regs[0][1]])))
                i += number_pattern.regs[0][1] - 1
        elif bool_pattern := re.match('True', command[i:]) or re.match('False', command[i:]):
            stack.append((TypeOfCommand.VALUE, bool(bool_pattern.string[:bool_pattern.regs[0][1]])))
            i += bool_pattern.regs[0][1] - 1
        elif lambda_pattern := re.match(r' *lambda [^:]*:', command[i:]):
            # ex: "lambda v: v ** 2 < 34"
            #     command = "v ** 2 < 34"
            command1 = command[i + lambda_pattern.regs[0][1]:]
            # ex: "lambda v: v ** 2 < 34"
            #     local = ["v"]
            variables = command[i:lambda_pattern.regs[0][1] - 1].split('lambda')[1].replace(' ', '').split(',')
            stack.append((TypeOfCommand.FUNCTION, Lambda(df, command1, variables, local)))
            i += lambda_pattern.regs[0][1] - 1 + len(command1)
        elif command[i] != ' ':
            variable_pattern = re.match(r'[\w]*', command[i:])
            if variable_pattern and variable_pattern.string[:variable_pattern.regs[0][1]] in local:
                stack.append((TypeOfCommand.VARIABLE, variable_pattern.string[:variable_pattern.regs[0][1]]))
            else:
                func = command[i:].strip()
                try:
                    function = _handle_function(func)
                except Exception:
                    prev_, next_ = _get_prev_and_next(command, i)
                    raise Exception(('Wrong expression at position {position}: "{expression}"').format(
                        expression=f'{prev_} --> {command[i]} <-- {next_}', position=str(i)))
                else:
                    stack.append((TypeOfCommand.FUNCTION, function))
                    break
        i += 1
    return stack


def _is_valid_parentheses(s: List[str]):
    """
    Validating if parentheses sequence is correct.
    s:
        example: ['(', ')', '(', '(', ')', '(', ')', ')']
        example: ['(', (0, 'column'), '<=', (1, 'value'), ')']
    """

    stack = []
    brackets = {'(': ')'}
    brackets_possible = {'(', ')'}
    pos = 0

    for element in s:
        if element in brackets_possible:
            if element in brackets:
                stack.append((element, pos))
            elif not stack or brackets[stack.pop()[0]] != element:
                _raise_excess_parentheses(s, pos)
        pos += 1

    if stack:
        _raise_excess_parentheses(s, stack[-1][1])


def _get_variable(var, df, local) -> pd.Series:
    """
    Returns series format for any var.
    """
    variable = None
    if isinstance(var, tuple):
        if var[0] == TypeOfCommand.VALUE:
            variable = var[1]
        elif var[0] == TypeOfCommand.COLUMN:
            if var[1] in df.columns:
                variable = df[var[1]]
            else:
                raise Exception(f"The input DataFrame doesn't contain \"{var[1]}\" column")
        elif var[0] == TypeOfCommand.VARIABLE:
            if local and var[1] in local:
                variable = local[var[1]]
            else:
                raise Exception(('Variable "{var}" doesn\'t exist').format(var=f'{var[1]}'))
    else:
        variable = var
    return var if variable is None else variable


def _analyse(string, df=None, local=None):
    """
    Analyses args of the method
    Returns arg in correct format(string, float, bool or lambda)
    """
    if local and string in local:
        return local[string]

    return solve_expression(string, df, local)


def _is_arg(string):
    """
    Checks if argument is arg or kwarg
    """

    if re.match(r' *[\w]* *=', string):
        return False
    return True


def _split_params(s: str):
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
                    _raise_excess_parentheses(s, pos)
        lambda_start = re.match(r' *lambda .*', s[prev: pos])
        whole_lambda = re.match(r' *lambda [^:]*:', s[prev: pos])
        if amount == 0 and element == ',' and (not lambda_start or (lambda_start and whole_lambda)):
            answer.append(s[prev:pos].strip())
            prev = pos + 1
        pos += 1

    if stack:
        _raise_excess_parentheses(s, stack[-1][1])
    answer.append(s[prev:].strip())
    return answer


def _solve_inside_method(command, df, local):
    """
    Gets args as command inside the method
    Returns args and kwargs
    example:
        command = "lambda t: t ** 2 > 34, q = 0.5"
        returns: [Lambda], {q: 0.5}
    """

    if not command:
        return [], {}

    params = _split_params(command)
    args = []
    kwargs = {}
    are_args = True
    for param in params:
        if _is_arg(param):
            if not are_args:
                raise SyntaxError("Positional argument follows keyword argument")
            arg = _analyse(param, df, local)
            args.append(arg)
        else:
            are_args = False
            keyword = param.split('=')[0].replace(' ', '')
            arg = _analyse(param.split('=', maxsplit=1)[1], df, local)
            kwargs[keyword] = arg
    return args, kwargs


def _raise_operation_cant_be_applied(stack, op):
    if not stack:
        raise Exception(('Operation "{operation}" can\'t be applied to Nothing').format(operation=op))


def _operate(stack, op, df, local):
    """
    Calculates result of operations.
    """

    if op == '~':
        _raise_operation_cant_be_applied(stack, op)
        l = stack.pop()

        var1 = _get_variable(l, df, local)
        stack.append(operators[op](var1))
    else:
        _raise_operation_cant_be_applied(stack, op)
        r = stack.pop()
        _raise_operation_cant_be_applied(stack, op)
        l = stack.pop()

        if isinstance(r, tuple) and r[0] == TypeOfCommand.METHOD:
            if hasattr(pd.Series, r[2]):
                var1 = _get_variable(l, df, local)
                if r[2] in {'apply', 'quantile'} and not isinstance(var1, (pd.Series, pd.DataFrame)):
                    raise Exception(('Method "{method}" can only be applied to Series or Dataframe, not {type}')
                                    .format(method=r[2], type=type(var1)))
                args, kwargs = _solve_inside_method(r[1], df, local)
                stack.append(getattr(var1, r[2])(*args, **kwargs))
            else:
                raise Exception(('Method "{method}" doesn\'t exist').format(method=r[2]))
        else:
            var1 = _get_variable(l, df, local)
            var2 = _get_variable(r, df, local)
            stack.append(operators[op](var1, var2))


def _handle_function(func: str) -> Callable:
    if func.startswith('numpy') or func.startswith('np'):
        if '.' in func:
            func = func.split('.')[1]
            return getattr(np, func)
    if func in allowed_funcs:
        return allowed_funcs[func]
    raise Exception(f"Unsupported function {func}")


def _polish_notation(s: List[Union[str, tuple]], df: Optional[pd.DataFrame] = None, local: dict = None):
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
                _operate(stack, op.pop(), df, local)
            op.pop()
        elif element in operators.keys():
            curop = element
            # {'~', '**'} are right associated
            while op and ((curop not in {'~', '**'} and _get_priority(op[-1]) >= _get_priority(curop)) or
                          (curop in {'~', '**'} and _get_priority(op[-1]) > _get_priority(curop))):
                _operate(stack, op.pop(), df, local)
            op.append(curop)
        else:
            stack.append(element)
            if element[0] == TypeOfCommand.METHOD:
                _operate(stack, '', df, local)
            if element[0] == TypeOfCommand.FUNCTION_EXECUTABLE:
                r = stack.pop()
                args, kwargs = _solve_inside_method(r[1], df, local)
                stack.append(_handle_function(r[2])(*args, **kwargs))
            if element[0] == TypeOfCommand.FUNCTION:
                r = stack.pop()
                if stack:
                    raise Exception("There can't be function and something else")
                return r[1]

    while op:
        _operate(stack, op.pop(), df, local)
    if len(stack) > 1:
        raise Exception("2 or more elements left without operations")
    value = stack.pop()
    return _get_variable(value, df, local)


def solve_expression(command: str, df: Optional[pd.DataFrame] = None, local: dict = None):
    """
    Returns result of expression.
    """

    command = command + ' '
    # parse input data
    stack = _get_stack(command, local, df)
    # checks if the parentheses are valid
    _is_valid_parentheses(stack)
    # calculate result of expression
    indices = _polish_notation(stack, df, local)
    return indices
