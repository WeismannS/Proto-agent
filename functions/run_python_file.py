from pathlib import Path
from functions.is_in_boundary import is_in_boundary
from subprocess import run
from google.genai import types

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


def run_python_file(working_directory: str, file_path: str, args=[]):
    path = (Path(working_directory) / file_path).resolve()
    if not is_in_boundary(Path(working_directory).resolve(), path):
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
        if len(instance.stdout) > 0:
            res += "No output produced."
        return res
    except Exception as E:
        return f"Error: executing Python file: {E}"
