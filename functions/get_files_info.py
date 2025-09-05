from typing import List
from pathlib import Path
from functions.is_in_boundary import is_in_boundary


def get_files_info(working_directory : str, directory=".") : 
    files_data = ""
    path = (Path(working_directory) / directory).resolve()
    try :
        if is_in_boundary(Path(working_directory), path) :
                return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        if not path.is_dir() :
            return f'Error: "{directory}" is not a directory'
        for file in path.iterdir() :
            files_data += (f"- {file.name}: file_size={file.stat().st_size} bytes, is_dir={file.is_dir()}\n")
    except Exception as E :
        return f"Error: {E}"
    return "".join(files_data)