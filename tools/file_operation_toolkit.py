from tool_kit_registry import ToolKitRegistery
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.get_files_info import get_files_info, schema_get_files_info
from functions.write_file import write_file, schema_write_file
from functions.run_python_file import run_python_file, schema_run_python_file
from google.genai import types
from abc import ABC, abstractmethod


class ToolKit(ABC):
    @abstractmethod
    def _register_functions(self):
        pass

    @property
    @abstractmethod
    def tool(self) -> types.Tool:
        pass


class FileOperationToolkit(ToolKit):
    def __init__(self, include_python_execution: bool = True):
        self.include_python_execution = include_python_execution
        self.schemas = []
        self._register_functions()

    def _register_functions(self):
        self.schemas.append(schema_get_file_content)
        self.schemas.append(schema_get_files_info)
        self.schemas.append(schema_write_file)

        ToolKitRegistery.register(
            "get_file_content", get_file_content, schema_get_file_content
        )
        ToolKitRegistery.register(
            "get_files_info", get_files_info, schema_get_files_info
        )
        ToolKitRegistery.register("write_file", write_file, schema_write_file)

        if self.include_python_execution:
            self.schemas.append(schema_run_python_file)
            ToolKitRegistery.register(
                "run_python_file", run_python_file, schema_run_python_file
            )

    @property
    def tool(self) -> types.Tool:
        return types.Tool(function_declarations=self.schemas)
