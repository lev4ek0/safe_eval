import re
from abc import ABCMeta, abstractmethod
from ast import literal_eval
from typing import List

from safe_evaluation.constants import TypeOfCommand


class Lambda:
    """
    Class for handling parsed lambda functions
    """

    def __init__(self, expression, df, command, variables, local):
        self.expression = expression
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
        indices = self.expression.solve(self.command, self.df, kwargs)
        return indices


class BasePreprocessor(metaclass=ABCMeta):
    @abstractmethod
    def prepare(self, command, df, local):
        pass


class Preprocessor(BasePreprocessor):
    def __init__(self, evaluator):
        self.evaluator = evaluator

    def _add_excess_brackets(self, i, endif, command):
        counter = 0
        for j in range(endif.count("(")):
            i += 1
            while i < len(command) and command[i] != ')':
                i += 1
            counter += 1
        return counter - endif.count(")"), i

    def if_else_function(self, before, middle, end, df, local):
        if self.evaluator.solve(command=middle, df=df, local=local):
            value = self.evaluator.solve(command=before, df=df, local=local)
        elif end.strip():
            value = self.evaluator.solve(command=end, df=df, local=local)
        else:
            value = None
        return value

    def _text_inside_parentheses(self, s: str):
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
                        self.evaluator.raise_excess_parentheses(s, pos)
            pos += 1
            if amount == 0:
                return s[start + 1:pos - 1]

        if stack:
            self.evaluator.raise_excess_parentheses(s, stack[-1][1])

    def _get_stack(self, command: str, local: dict = None, df=None) -> List[str]:
        """
        Returns splitted command.
        """
        command += ' '

        local = local or {}

        stack = []
        i = 0

        while i < len(command):
            if if_else_pattern := re.match(r'[^\(\:]*[ ()]if[ ()]((?!if|else).)*(else)?[^)]*', command[i:]):
                if_else_string = command[i:i + if_else_pattern.regs[0][1]]
                before_if = re.match(r'((?!if).)*', if_else_string)
                middle_if = re.match(r'((?!else).)*', if_else_string[2 + before_if.regs[0][1]:])
                endif = if_else_string[2 + before_if.regs[0][1] + 4 + middle_if.regs[0][1]:]
                counter, i = self._add_excess_brackets(i + if_else_pattern.regs[0][1] - 1, endif, command)
                endif += ''.join([')' for i in range(counter)])
                stack.append(
                    (TypeOfCommand.VALUE, self.if_else_function(before_if.group(0), middle_if.group(0), endif, df, local)))
            elif command[i] in {'(', ')'}:
                stack.append(command[i])
            # mathing columns with ${column} format
            elif command[i] == self.evaluator.settings.df_startswith:
                # todo: handle "{", "}" as name of column
                column_pattern = re.match(self.evaluator.settings.df_regex, command[i:])
                if column_pattern:
                    column_name = column_pattern.string[2:column_pattern.regs[0][1] - 1]
                    if column_name == self.evaluator.settings.df_name:
                        stack.append((TypeOfCommand.DATAFRAME,))
                    else:
                        stack.append((TypeOfCommand.COLUMN, column_name))
                    i += column_pattern.regs[0][1] - 1
            elif command[i] == '.':
                method_pattern = re.match(r'\.[\w]+\(.*\)', command[i:])
                property_pattern = re.match(r'\.[\w]+', command[i:])
                if method_pattern:
                    command_outer = method_pattern.string[:method_pattern.regs[0][1]]
                    method_name_pattern = re.match(r'\.[\w]+', command_outer)
                    command_inner = self._text_inside_parentheses(command_outer)
                    stack.append((TypeOfCommand.METHOD, command_inner,
                                  method_name_pattern.string[1:method_name_pattern.regs[0][1]]))
                    i += method_name_pattern.regs[0][1] + len(command_inner) + 1
                else:
                    stack.append((TypeOfCommand.PROPERTY, property_pattern.string[1:property_pattern.regs[0][1]]))
                    i += property_pattern.regs[0][1] - 1
            elif function_pattern := re.match(r'[\w.]+\(.*\)', command[i:]):
                command_outer = function_pattern.string[:function_pattern.regs[0][1]]
                function_name_pattern = re.match(r'[\w.]+', command_outer)
                command_inner = self._text_inside_parentheses(command_outer)
                stack.append(
                    (TypeOfCommand.FUNCTION_EXECUTABLE, command_inner,
                     function_name_pattern.string[:function_name_pattern.regs[0][1]]))
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
            elif len(command) > i + 2 and ((command[i:i + 3] in ('in ', 'in(')) or (
                    command[i: i + 2] in self.evaluator.operators and command[i: i + 2] != 'in')):
                stack.append(command[i:i + 2])
                i += 1
            elif command[i] in self.evaluator.operators:
                stack.append(command[i])
            # mathing floats and ints
            elif number_pattern := re.match(r'[-+]?\d*\.?\d+', command[i:]):
                if float_number_pattern := re.match(r'[-+]?\d+\.\d+', command[i:]):
                    stack.append(
                        (TypeOfCommand.VALUE, float(float_number_pattern.string[:float_number_pattern.regs[0][1]])))
                    i += float_number_pattern.regs[0][1] - 1
                else:
                    stack.append((TypeOfCommand.VALUE, int(number_pattern.string[:number_pattern.regs[0][1]])))
                    i += number_pattern.regs[0][1] - 1
            elif bool_pattern := re.match('True', command[i:]):
                stack.append((TypeOfCommand.VALUE, True))
                i += bool_pattern.regs[0][1] - 1
            elif bool_pattern := re.match('False', command[i:]):
                stack.append((TypeOfCommand.VALUE, False))
                i += bool_pattern.regs[0][1] - 1
            elif lambda_pattern := re.match(r' *lambda [^:]*:', command[i:]):
                # ex: "lambda v: v ** 2 < 34"
                #     command = "v ** 2 < 34"
                command1 = command[i + lambda_pattern.regs[0][1]:]
                # ex: "lambda v: v ** 2 < 34"
                #     local = ["v"]
                variables = command[i:lambda_pattern.regs[0][1] - 1].split('lambda')[1].replace(' ', '').split(',')
                stack.append((TypeOfCommand.FUNCTION, Lambda(self.evaluator, df, command1, variables, local)))
                i += lambda_pattern.regs[0][1] - 1 + len(command1)
            elif command[i] != ' ':
                variable_pattern = re.match(r'[\w]*', command[i:])
                if variable_pattern and variable_pattern.string[:variable_pattern.regs[0][1]] in local:
                    stack.append((TypeOfCommand.VARIABLE, variable_pattern.string[:variable_pattern.regs[0][1]]))
                else:
                    func = command[i:].strip()
                    try:
                        function = self.evaluator.handle_function(func)
                    except Exception:
                        prev_, next_ = self.evaluator.get_prev_and_next(command, i)
                        raise Exception(('Wrong expression at position {position}: "{expression}"').format(
                            expression=f'{prev_} --> {command[i]} <-- {next_}', position=str(i)))
                    else:
                        if callable(function):
                            stack.append((TypeOfCommand.FUNCTION, function))
                        else:
                            stack.append((TypeOfCommand.VALUE, function))
                        break
            i += 1
        return stack

    def _is_valid_parentheses(self, s: List[str]):
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
                    self.evaluator.raise_excess_parentheses(s, pos)
            pos += 1

        if stack:
            self.evaluator.raise_excess_parentheses(s, stack[-1][1])

    def prepare(self, command, df, local):
        # parse input data
        stack = self._get_stack(command, local, df)
        # checks if the parentheses are valid
        self._is_valid_parentheses(stack)
        return stack
