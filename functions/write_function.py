from functions.is_in_boundary import is_in_boundary
from pathlib import Path

def write_file(working_directory : str, file_path : str, content : str):
    path = (Path(working_directory) / file_path).resolve()
    if is_in_boundary(Path(working_directory).resolve(), path) == False :
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    try :
        with open(path, "w+") as f :
            f.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as E :
        return f"Error: {E}"
        