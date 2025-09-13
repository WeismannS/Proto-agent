from pathlib import Path
from subprocess import run
from ..tool_kit_registry import ToolKitRegistery
from ..types_llm import FunctionDeclaration, Tool
from .base_toolkit import ToolKit
from ..Config import MAX_BYTES


def _is_in_boundary(working_directory: Path, path: Path) -> bool:
    """Check if a path is within the working directory boundary"""
    if working_directory.resolve() != path:
        if working_directory.resolve() not in path.parents:
            return False
    return True


def get_file_content(
    working_directory: str, file_path: str, max_bytes: int = MAX_BYTES
) -> str:
    """Read the contents of a file and return them"""
    path = (Path(working_directory) / file_path).resolve()
    if not _is_in_boundary(Path(working_directory), path):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    try:
        if not path.is_file():
            return f'Error: File not found or is not a regular file: "{file_path}"'
        with open(path) as f:
            content = f.read(max_bytes)
        metadata = path.stat()
        if metadata.st_size > max_bytes:
            content += f'[...File "{file_path}" truncated at {max_bytes} characters]'
        return content
    except Exception as e:
        return f"Error: {e}"


def get_files_info(working_directory: str, directory: str = ".") -> str:
    """List files and directories with metadata"""
    path = (Path(working_directory) / directory).resolve()
    try:
        if not _is_in_boundary(Path(working_directory), path):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        if not path.is_dir():
            return f'Error: "{directory}" is not a directory'
        files_data = ""
        for file in path.iterdir():
            files_data += f"- {file.name}: file_size={file.stat().st_size} bytes, is_dir={file.is_dir()}\n"
        return files_data
    except Exception as e:
        return f"Error: {e}"


def write_file(working_directory: str, file_path: str, content: str) -> str:
    """Write content to a file, creating it if it doesn't exist"""
    path = (Path(working_directory) / file_path).resolve()
    if not _is_in_boundary(Path(working_directory).resolve(), path):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    try:
        with open(path, "w+") as f:
            f.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f"Error: {e}"


def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    """Execute a Python file and return its output"""
    if args is None:
        args = []
    path = (Path(working_directory) / file_path).resolve()
    if not _is_in_boundary(Path(working_directory).resolve(), path):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    try:
        if not path.is_file():
            return f'Error: File not found or is not a regular file: "{file_path}"'

        cmd = ["python", str(path)] + args
        result = run(
            cmd,
            capture_output=True,
            text=True,
            cwd=working_directory,
            timeout=30,
        )

        res = f"Exit code: {result.returncode}\n"
        if result.stdout:
            res += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            res += f"STDERR:\n{result.stderr}\n"
        if len(result.stdout) == 0 and len(result.stderr) == 0:
            res += "No output produced."
        return res
    except Exception as e:
        return f"Error: {e}"


schema_get_file_content = FunctionDeclaration(
    name="get_file_content",
    description="Read the contents of a file and return them. Returns the full file content on success.",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "path for file to be read",
            }
        },
        "required": ["file_path"],
    },
)

schema_get_files_info = FunctionDeclaration(
    name="get_files_info",
    description="List files and directories with metadata. The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
    parameters={
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "Directory to list the files for",
            }
        },
    },
)

schema_write_file = FunctionDeclaration(
    name="write_file",
    description="function to write content to a certain a file, if file doesn't exist it creates it!",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "path to the file to be operated on",
            },
            "content": {
                "type": "string",
                "description": "Content to be written in the file",
            },
        },
        "required": ["file_path", "content"],
    },
)

schema_run_python_file = FunctionDeclaration(
    name="run_python_file",
    description="Execute a Python file located in the calculator directory. Returns the program output or an error.",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Relative path to the Python file to execute.",
            },
            "args": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Command-line arguments to pass to the Python file.",
            },
        },
        "required": ["file_path"],
    },
)


class FileOperationToolkit(ToolKit):
    """
    File operations toolkit with configurable capabilities.
    Provides secure file operations within a working directory boundary.
    """

    GET_FILE_CONTENT = "get_file_content"
    GET_FILES_INFO = "get_files_info"
    WRITE_FILE = "write_file"
    RUN_PYTHON_FILE = "run_python_file"

    def __init__(
        self,
        enable_read: bool = True,
        enable_write: bool = True,
        enable_list: bool = True,
        enable_execute: bool = True,
        max_bytes: int = MAX_BYTES,
    ):
        """
        Initialize FileOperationToolkit with capability flags.

        Args:
            enable_read: Allow reading file contents
            enable_write: Allow writing/modifying files
            enable_list: Allow listing files and directories
            enable_execute: Allow executing Python files
            max_bytes: Maximum bytes to read from files
            requires_permissions: Set of function names that require user confirmation
        """
        super().__init__()
        self.enable_read = enable_read
        self.enable_write = enable_write
        self.enable_list = enable_list
        self.enable_execute = enable_execute
        self.max_bytes = max_bytes
        self._register_functions()

    def _register_functions(self):
        """Register enabled functions with the global registry"""

        if self.enable_read:
            self.schemas.append(schema_get_file_content)
            ToolKitRegistery.register(
                "get_file_content",
                lambda working_directory, file_path: get_file_content(
                    working_directory, file_path, self.max_bytes
                ),
                schema_get_file_content,
            )

        if self.enable_list:
            self.schemas.append(schema_get_files_info)
            ToolKitRegistery.register(
                "get_files_info", get_files_info, schema_get_files_info
            )

        if self.enable_write:
            self.schemas.append(schema_write_file)
            ToolKitRegistery.register("write_file", write_file, schema_write_file)

        if self.enable_execute:
            self.schemas.append(schema_run_python_file)
            ToolKitRegistery.register(
                "run_python_file", run_python_file, schema_run_python_file
            )

    @property
    def tool(self) -> Tool:
        """Get the Tool instance for this toolkit"""
        return Tool(function_declarations=self.schemas)
