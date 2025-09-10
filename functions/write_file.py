from functions.is_in_boundary import is_in_boundary
from pathlib import Path
from google.genai import types


schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="function to write content to a certain a file, if file doesn't exist it creates it!",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING, description="path to the file to be operated on"
            ),
            "content": types.Schema(
                type=types.Type.STRING, description="Content to be written in the file"
            ),
        },
    ),
)


def write_file(working_directory: str, file_path: str, content: str):
    path = (Path(working_directory) / file_path).resolve()
    if is_in_boundary(Path(working_directory).resolve(), path) == False:
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    try:
        with open(path, "w+") as f:
            f.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as E:
        return f"Error: {E}"
