"""
Base ToolKit class for all toolkit implementations.
Provides common interface and functionality for all toolkits.
"""

from abc import ABC, abstractmethod
from ..types_llm import Tool


class ToolKit(ABC):
    """Abstract base class for all toolkits"""

    def __init__(self):
        """Initialize toolkit with empty schemas list"""
        self.schemas = []

    @abstractmethod
    def _register_functions(self):
        """Register functions with the global registry. Must be implemented by subclasses."""
        pass

    @property
    @abstractmethod
    def tool(self) -> Tool:
        """Get the Tool instance for this toolkit. Must be implemented by subclasses."""
        pass

    def get_enabled_functions(self) -> list[str]:
        """Get list of function names that are enabled in this toolkit"""
        return [schema.name for schema in self.schemas]

    def __repr__(self) -> str:
        """String representation of the toolkit"""
        return f"{self.__class__.__name__}(functions={len(self.schemas)})"
