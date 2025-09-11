from google.genai import types


from typing import Callable


class ToolKitRegistery:
    _functions: dict[str, Callable] = {}
    _schemas: list[types.FunctionDeclaration] = []

    @classmethod
    def register(cls, name: str, function: Callable, schema: types.FunctionDeclaration):
        cls._functions[name] = function
        cls._schemas.append(schema)

    @classmethod
    def get_function(cls, name: str):
        return cls._functions.get(name)
