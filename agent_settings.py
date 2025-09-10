from dataclasses import dataclass
from pathlib import Path
from google.genai import types


@dataclass
class AgentConfig:
    def __init__(
        self,
        api_key: str,
        working_directory: Path | str,
        model: str = "gemini-2.0-flash-001",
        max_file_size: int = 10_000,
        max_iterations: int = 20,
        tools: list[types.Tool] = [],
        verbose: bool = False,
        allow_exec: bool = False,
    ):
        self.api_key = api_key
        self.working_directory = working_directory
        self.model = model
        self.max_file_size = max_file_size
        self.max_iterations = max_iterations
        self.tools: list[types.Tool] = tools
        self.verbose = verbose
        self.allow_exec = allow_exec
        if not isinstance(self.working_directory, Path):
            self.working_directory = Path(self.working_directory)
        self.working_directory = self.working_directory.resolve()
