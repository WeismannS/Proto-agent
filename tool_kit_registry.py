from types_llm import FunctionDeclaration
from typing import Callable


class ToolKitRegistery:
    _functions: dict[str, Callable] = {}
    _schemas: list[FunctionDeclaration] = []

    @classmethod
    def register(cls, name: str, function: Callable, schema: FunctionDeclaration):
        if name in cls._functions:
            raise ValueError(f"Function '{name}' is already registered.")
        cls._functions[name] = function
        cls._schemas.append(schema)

    @classmethod
    def get_function(cls, name: str):
        return cls._functions.get(name)
