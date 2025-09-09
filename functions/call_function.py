from google.genai import types
from functions import run_python_file
from functions.get_file_content import get_file_content
from functions.get_files_info import get_files_info
from functions.write_file import write_file
from functions.run_python_file import run_python_file


functions_table = {
    "get_file_content" : get_file_content,
    "get_files_info" : get_files_info,
    "write_file" : write_file,
    "run_python_file" : run_python_file
}
def call_function(function_call_part : types.FunctionCall, verbose=False):
    if function_call_part.name == None :
        return types.Content(
            role="tool",
            parts=[
            types.Part.from_function_response(
            name="invalid name",
            response={"error": f"Unknown function: {function_call_part.name}"},
            )])
    function_to_run = functions_table.get(function_call_part.name or "")
    if function_to_run == None :
        return types.Content(
            role="tool",
            parts=[
            types.Part.from_function_response(
            name=function_call_part.name,
            response={"error": f"Unknown function: {function_call_part.name}"},
            )])
    if verbose :
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else :
        print(f" - Calling function: {function_call_part.name}")
    args_dict = (function_call_part.args) if function_call_part.args else {}
    res = function_to_run("./calculator", **args_dict)
    return types.Content(
    role="tool",
    parts=[
        types.Part.from_function_response(
            name=function_call_part.name,
            response={"result": res},
        )
    ],
)

