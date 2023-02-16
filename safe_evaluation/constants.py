import operator
from enum import Enum

import numpy as np


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
    PROPERTY = 6
    DATAFRAME = 7


ALLOWED_FUNCS = {
    'range': range,
    'map': map,
    'filter': filter,
    'list': list,
    'bool': bool,
    'int': int,
    'float': float,
    'complex': complex,
    'str': str,
}

NUMPY_ALLOWED_FUNCS = [
    'np',
    'numpy',
    'pd',
    'pandas',
]

OPERATORS = {
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

OPERATORS_PRIORITIES = {
    'in': 1,

    # comparison
    '==': 2,
    '>=': 2,
    '>': 2,
    '<': 2,
    '<=': 2,

    '|': 3,
    '^': 4,
    '&': 5,

    # +-
    '+': 6,
    '-': 6,

    # *, /, //, %
    '*': 7,
    '/': 7,
    '//': 7,
    '%': 7,

    '~': 8,
    '**': 9,
}
