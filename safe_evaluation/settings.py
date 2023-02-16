from typing import Union

from safe_evaluation.constants import ALLOWED_FUNCS, NUMPY_ALLOWED_FUNCS


class Settings:
    def __init__(
            self, *,
            allowed_funcs: Union[list, None] = None,
            numpy_allowed_funcs: Union[list, None] = None,
            forbidden_funcs: Union[list, None] = None,
            df_startswith: str = '$',
            df_regex: str = r'\${[^\{\}]+}',
            df_name: str = '__df'
    ):
        self.numpy_allowed_funcs = NUMPY_ALLOWED_FUNCS if numpy_allowed_funcs is None else numpy_allowed_funcs
        self.allowed_funcs = ALLOWED_FUNCS.keys() if allowed_funcs is None else allowed_funcs
        self.forbidden_funcs = [] if forbidden_funcs is None else forbidden_funcs
        self.df_startswith = df_startswith
        self.df_regex = df_regex
        self.df_name = df_name

    def _check_allowed_func(self, func_name: str):
        is_numpy_pandas = func_name.startswith(tuple(self.numpy_allowed_funcs))
        return func_name in self.allowed_funcs or is_numpy_pandas

    def _check_forbidden_func(self, func_name: str):
        return func_name not in self.forbidden_funcs

    def is_available(self, func_name: str):
        return self._check_allowed_func(func_name=func_name) and \
               self._check_forbidden_func(func_name=func_name)
