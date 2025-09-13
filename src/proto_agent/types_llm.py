"""
LLM types module - defines standard types for LLM interactions using LiteLLM
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    """Message roles"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"
    FUNCTION = "function"


@dataclass
class FunctionCall:
    """Represents a function call"""

    name: str
    arguments: Optional[Dict[str, Any]] = None

    @property
    def args(self) -> Optional[Dict[str, Any]]:
        """Alias for arguments to match Google GenAI API"""
        return self.arguments


@dataclass
class ToolCall:
    """Represents a tool call"""

    id: str
    type: str
    function: FunctionCall


@dataclass
class FunctionResponse:
    """Represents a function response"""

    name: str
    response: Dict[str, Any]


@dataclass
class Part:
    """Represents a part of content"""

    text: Optional[str] = None
    function_call: Optional[FunctionCall] = None
    function_response: Optional[FunctionResponse] = None

    @classmethod
    def from_text(cls, text: str) -> "Part":
        """Create a text part"""
        return cls(text=text)

    @classmethod
    def from_function_call(cls, name: str, args: Dict[str, Any]) -> "Part":
        """Create a function call part"""
        return cls(function_call=FunctionCall(name=name, arguments=args))

    @classmethod
    def from_function_response(cls, name: str, response: Dict[str, Any]) -> "Part":
        """Create a function response part"""
        return cls(function_response=FunctionResponse(name=name, response=response))


@dataclass
class Content:
    """Represents message content"""

    role: str
    parts: List[Part]

    def __init__(self, role: str, parts: List[Part]):
        self.role = role
        self.parts = parts


@dataclass
class UsageMetadata:
    """Usage metadata for the response"""

    prompt_token_count: int
    candidates_token_count: int
    total_token_count: int


@dataclass
class GenerateContentResponse:
    """Response from content generation"""

    text: Optional[str]
    function_calls: List[FunctionCall]
    usage_metadata: Optional[UsageMetadata] = None

    def __init__(
        self,
        text: Optional[str] = None,
        function_calls: Optional[List[FunctionCall]] = None,
        usage_metadata: Optional[UsageMetadata] = None,
    ):
        self.text = text
        self.function_calls = function_calls or []
        self.usage_metadata = usage_metadata


@dataclass
class FunctionParameter:
    """Function parameter definition"""

    type: str
    description: Optional[str] = None
    enum: Optional[List[str]] = None


@dataclass
class FunctionDeclaration:
    """Function declaration for tools"""

    name: str
    description: str
    parameters: Dict[str, Any]

    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters


@dataclass
class Tool:
    """Tool definition"""

    function_declarations: List[FunctionDeclaration]

    def __init__(self, function_declarations: List[FunctionDeclaration]):
        self.function_declarations = function_declarations


@dataclass
class GenerateContentConfig:
    """Configuration for content generation"""

    tools: Optional[List[Tool]] = None
    system_instruction: Optional[str] = None
    temperature: float = 1.0
    max_tokens: Optional[int] = None


# Type aliases for compatibility
ToolListUnion = List[Tool]
