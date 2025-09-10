from pathlib import Path
from Config import MAX_BYTES
from functions.is_in_boundary import is_in_boundary
from google.genai import types

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Read the contents of a file and return them. Returns the full file content on success.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING, description="path for file to be read"
            )
        },
    ),
)


def get_file_content(working_directory: str, file_path: str):
    res = ""
    path = (Path(working_directory) / file_path).resolve()
    if is_in_boundary(Path(working_directory), path) == False:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    try:
        if not path.is_file():
            return f'Error: File not found or is not a regular file: "{file_path}"'
        with open(path) as f:
            res = f.read(MAX_BYTES)
        metadata = path.stat()
        if metadata.st_size > MAX_BYTES:
            res += f'[...File "{file_path}" truncated at 10000 characters]'
    except Exception as E:
        return f"Error: {E}"
    return res
