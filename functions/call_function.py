from google.genai import types
from Config import ENTRY
from functions.get_file_content import get_file_content
from functions.get_files_info import get_files_info
from functions.write_file import write_file
from functions.run_python_file import run_python_file


FUNCTIONS_TABLE = {
    "get_file_content": get_file_content,
    "get_files_info": get_files_info,
    "write_file": write_file,
    "run_python_file": run_python_file,
}


def _create_error_response(function_name: str, error: str):
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"error": error},
            )
        ],
    )


def _get_user_confirmation(file_path: str, args: dict) -> bool:
    """Get user confirmation for file execution."""
    args_display = {k: v for k, v in args.items() if k != "file_path"}
    choice = input(
        f"Allow execution of '{file_path}' with args {args_display}? (y/N): "
    ).lower()
    return choice in ("y", "yes")


def call_function(
    function_call_part: types.FunctionCall, verbose=False, allow_exec=False
):
    if function_call_part.name == None:
        return _create_error_response(
            "Invalid function", f"Unknown function: {function_call_part.name}"
        )
    function_to_run = FUNCTIONS_TABLE.get(function_call_part.name)
    if function_to_run == None:
        return _create_error_response(
            "Invalid function", f"Unknown function: {function_call_part.name}"
        )
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
    if function_to_run == run_python_file and allow_exec == False:
        file_path = (
            function_call_part.args.get("file_path", "unknown")
            if function_call_part.args
            else "unknown"
        )
        args_without_file_path = (
            {k: v for k, v in function_call_part.args.items() if k != "file_path"}
            if function_call_part.args
            else {}
        )
        if _get_user_confirmation(file_path, args_without_file_path):
            return _create_error_response(
                function_call_part.name, f"Refused to run {function_call_part.name}"
            )
    args_dict = (function_call_part.args) if function_call_part.args else {}
    res = function_to_run(ENTRY, **args_dict)
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_call_part.name,
                response={"result": res},
            )
        ],
    )
