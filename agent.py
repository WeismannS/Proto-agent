from typing import List, cast
from google.genai import types, Client

from Config import SYSTEM_PROMPT
from agent_settings import AgentConfig
from functions.run_python_file import run_python_file
from functions.get_file_content import get_file_content
from functions.get_files_info import get_files_info
from functions.write_file import write_file

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


class Agent:
    def __init__(self, settings: AgentConfig):
        self.settings = settings
        self._client = Client(api_key=settings.api_key)

    def call_function(
        self, function_call_part: types.FunctionCall, verbose=False, allow_exec=False
    ):
        if function_call_part.name is None:
            return _create_error_response(
                "Invalid function", f"Unknown function: {function_call_part.name}"
            )
        function_to_run = FUNCTIONS_TABLE.get(function_call_part.name)
        if function_to_run is None:
            return _create_error_response(
                "Invalid function", f"Unknown function: {function_call_part.name}"
            )
        if verbose:
            print(
                f"Calling function: {function_call_part.name}({function_call_part.args})"
            )
        else:
            print(f" - Calling function: {function_call_part.name}")
        if function_to_run == run_python_file and not allow_exec:
            function_arguments = (
                function_call_part.args if function_call_part.args else {}
            )
            file_path = function_arguments.get("file_path", "")

            if not _get_user_confirmation(file_path, function_arguments):
                return _create_error_response(
                    function_call_part.name, f"Refused to run {function_call_part.name}"
                )
        args_dict = (function_call_part.args) if function_call_part.args else {}
        res = function_to_run(self.settings.working_directory, **args_dict)
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"result": res},
                )
            ],
        )

    def generate_content(
        self,
        prompt: str | None = None,
        messages: List[types.Content] | None = None,
    ) -> types.GenerateContentResponse:
        if messages is None:
            if prompt is None:
                raise ValueError("Either prompt or messages must be provided")
            messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]

        working_messages = messages.copy()
        iterations = 0

        while iterations < self.settings.max_iterations:
            response = self._client.models.generate_content(
                contents=working_messages,
                model=self.settings.model,
                config=types.GenerateContentConfig(
                    tools=cast(types.ToolListUnion, self.settings.tools),
                    system_instruction=SYSTEM_PROMPT,
                ),
            )

            if not response.function_calls:
                return response

            function_call_parts = []
            for function_call in response.function_calls:
                if self.settings.verbose:
                    print(
                        f"Calling function: {function_call.name}({function_call.args})"
                    )

                function_call_parts.append(
                    types.Part.from_function_call(
                        name=function_call.name, args=function_call.args
                    )
                )
            working_messages.append(
                types.Content(role="model", parts=function_call_parts)
            )

            function_response_parts = []
            for function_call in response.function_calls:
                function_res = self.call_function(
                    function_call, self.settings.verbose, self.settings.allow_exec
                )

                if (
                    function_res.parts is None
                    or not function_res.parts
                    or function_res.parts[0].function_response is None
                ):
                    raise Exception(
                        f"Function {function_call.name} returned no response"
                    )

                if (
                    self.settings.verbose
                    and function_res.parts[0].function_response
                    and function_res.parts[0].function_response.response
                ):
                    print(f"-> {function_res.parts[0].function_response.response}")
                function_response_parts.extend(function_res.parts)

            working_messages.append(
                types.Content(role="user", parts=function_response_parts)
            )
            iterations += 1

        raise Exception(
            f"Maximum function call iterations ({self.settings.max_iterations}) exceeded"
        )
