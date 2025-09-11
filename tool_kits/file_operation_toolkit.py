from pathlib import Path
from subprocess import run
from tool_kit_registry import ToolKitRegistery
from google.genai import types
from .base_toolkit import ToolKit
from Config import MAX_BYTES


class FileOperationToolkit(ToolKit):
    """
    File operations toolkit with configurable capabilities.
    Provides secure file operations within a working directory boundary.
    """

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
        """
        super().__init__()
        self.enable_read = enable_read
        self.enable_write = enable_write
        self.enable_list = enable_list
        self.enable_execute = enable_execute
        self.max_bytes = max_bytes
        self._register_functions()

    def _is_in_boundary(self, working_directory: Path, path: Path) -> bool:
        """Check if a path is within the working directory boundary"""
        if working_directory.resolve() != path:
            if working_directory.resolve() not in path.parents:
                return False
        return True

    def _get_file_content(self, working_directory: str, file_path: str) -> str:
        """Read the contents of a file and return them"""
        path = (Path(working_directory) / file_path).resolve()
        if not self._is_in_boundary(Path(working_directory), path):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        try:
            if not path.is_file():
                return f'Error: File not found or is not a regular file: "{file_path}"'
            with open(path) as f:
                content = f.read(self.max_bytes)
            metadata = path.stat()
            if metadata.st_size > self.max_bytes:
                content += (
                    f'[...File "{file_path}" truncated at {self.max_bytes} characters]'
                )
            return content
        except Exception as e:
            return f"Error: {e}"

    def _get_files_info(self, working_directory: str, directory: str = ".") -> str:
        """List files and directories with metadata"""
        path = (Path(working_directory) / directory).resolve()
        try:
            if not self._is_in_boundary(Path(working_directory), path):
                return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
            if not path.is_dir():
                return f'Error: "{directory}" is not a directory'
            files_data = ""
            for file in path.iterdir():
                files_data += f"- {file.name}: file_size={file.stat().st_size} bytes, is_dir={file.is_dir()}\n"
            return files_data
        except Exception as e:
            return f"Error: {e}"

    def _write_file(self, working_directory: str, file_path: str, content: str) -> str:
        """Write content to a file, creating it if it doesn't exist"""
        path = (Path(working_directory) / file_path).resolve()
        if not self._is_in_boundary(Path(working_directory).resolve(), path):
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        try:
            with open(path, "w+") as f:
                f.write(content)
                return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        except Exception as e:
            return f"Error: {e}"

    def _run_python_file(
        self, working_directory: str, file_path: str, args: list[str] | None = None
    ) -> str:
        """Execute a Python file and return its output"""
        if args is None:
            args = []
        path = (Path(working_directory) / file_path).resolve()
        if not self._is_in_boundary(Path(working_directory).resolve(), path):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not path.exists():
            return f'Error: File "{file_path}" not found.'
        index = path.name.rfind(".")
        if index == -1 or path.name[index:] != ".py":
            return f'Error: "{file_path}" is not a Python file.'
        try:
            instance = run(
                ["python3", str(path), *args],
                timeout=30,
                capture_output=True,
                cwd=Path(working_directory),
                encoding="utf",
            )
            res = ""
            res += f"STDOUT: {instance.stdout}"
            res += f"STDERR: {instance.stderr}"
            if instance.returncode != 0:
                res += f"Process exited with code {instance.returncode}"
            if len(instance.stdout) == 0:
                res += "No output produced."
            return res
        except Exception as e:
            return f"Error: {e}"

    def _register_functions(self):
        """Register enabled functions with the global registry"""

        if self.enable_read:
            schema_get_file_content = types.FunctionDeclaration(
                name="get_file_content",
                description="Read the contents of a file and return them. Returns the full file content on success.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "file_path": types.Schema(
                            type=types.Type.STRING,
                            description="path for file to be read",
                        )
                    },
                ),
            )
            self.schemas.append(schema_get_file_content)
            ToolKitRegistery.register(
                "get_file_content", self._get_file_content, schema_get_file_content
            )

        if self.enable_list:
            schema_get_files_info = types.FunctionDeclaration(
                name="get_files_info",
                description="List files and directories with metadata. The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "directory": types.Schema(
                            type=types.Type.STRING,
                            description="Directory to list the files for",
                        )
                    },
                ),
            )
            self.schemas.append(schema_get_files_info)
            ToolKitRegistery.register(
                "get_files_info", self._get_files_info, schema_get_files_info
            )

        if self.enable_write:
            schema_write_file = types.FunctionDeclaration(
                name="write_file",
                description="function to write content to a certain a file, if file doesn't exist it creates it!",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "file_path": types.Schema(
                            type=types.Type.STRING,
                            description="path to the file to be operated on",
                        ),
                        "content": types.Schema(
                            type=types.Type.STRING,
                            description="Content to be written in the file",
                        ),
                    },
                ),
            )
            self.schemas.append(schema_write_file)
            ToolKitRegistery.register("write_file", self._write_file, schema_write_file)

        if self.enable_execute:
            schema_run_python_file = types.FunctionDeclaration(
                name="run_python_file",
                description="Execute a Python file located in the calculator directory. Returns the program output or an error.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "file_path": types.Schema(
                            type=types.Type.STRING,
                            description="Relative path to the Python file to execute.",
                        ),
                        "args": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(type=types.Type.STRING),
                            description="Command-line arguments to pass to the Python file.",
                        ),
                    },
                    required=["file_path"],
                ),
            )
            self.schemas.append(schema_run_python_file)
            ToolKitRegistery.register(
                "run_python_file", self._run_python_file, schema_run_python_file
            )

    @property
    def tool(self) -> types.Tool:
        """Get the Tool instance for this toolkit"""
        return types.Tool(function_declarations=self.schemas)
