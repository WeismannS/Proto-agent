from typing import List
from google.genai import types, Client

from Config import MODEL, SYSTEM_PROMPT
from functions.call_function import call_function


def generate_content(
    client: Client,
    tools: types.Tool,
    verbose: bool,
    allow_exec: bool,
    prompt: str | None = None,
    messages: List[types.Content] | None = None,
    max_iterations: int = 20,
) -> types.GenerateContentResponse:
    if messages is None:
        if prompt is None:
            raise ValueError("Either prompt or messages must be provided")
        messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]

    working_messages = messages.copy()
    iterations = 0

    while iterations < max_iterations:
        response = client.models.generate_content(
            contents=working_messages,
            model=MODEL,
            config=types.GenerateContentConfig(
                tools=[tools], system_instruction=SYSTEM_PROMPT
            ),
        )

        if not response.function_calls:
            return response

        function_call_parts = []
        for function_call in response.function_calls:
            if verbose:
                print(f"Calling function: {function_call.name}({function_call.args})")

            function_call_parts.append(
                types.Part.from_function_call(
                    name=function_call.name, args=function_call.args
                )
            )
        working_messages.append(types.Content(role="model", parts=function_call_parts))

        function_response_parts = []
        for function_call in response.function_calls:
            function_res = call_function(function_call, verbose, allow_exec)

            if (
                function_res.parts == None
                or not function_res.parts
                or function_res.parts[0].function_response is None
            ):
                raise Exception(f"Function {function_call.name} returned no response")

            if (
                verbose
                and function_res.parts[0].function_response
                and function_res.parts[0].function_response.response
            ):
                print(f"-> {function_res.parts[0].function_response.response}")
            function_response_parts.extend(function_res.parts)

        working_messages.append(
            types.Content(role="user", parts=function_response_parts)
        )
        iterations += 1

    raise Exception(f"Maximum function call iterations ({max_iterations}) exceeded")
