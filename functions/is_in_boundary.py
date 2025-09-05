from pathlib import Path

def is_in_boundary(working_directory : Path, path : Path)  : 
    if (working_directory.resolve() != path) :
        if working_directory not in path.parents :
            print(path)
            return False 
    return True