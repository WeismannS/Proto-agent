from dataclasses import dataclass
from pathlib import Path
from .types_llm import Tool


@dataclass
class AgentConfig:
    def __init__(
        self,
        api_key: str,
        working_directory: Path | str,
        model: str,
        max_iterations: int = 20,
        tools: list[Tool] = [],
        verbose: bool = False,
        allow_exec: bool = False,
        permission_required: set = set(),
    ):
        self.api_key = api_key
        self.working_directory = working_directory
        self.model = model
        self.max_iterations = max_iterations
        self.tools: list[Tool] = tools
        self.verbose = verbose
        self.allow_exec = allow_exec
        self.permission_required = permission_required
        if not isinstance(self.working_directory, Path):
            self.working_directory = Path(self.working_directory)
        self.working_directory = self.working_directory.resolve()
