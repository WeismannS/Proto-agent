from email import message
from typing import List
from google.genai import types,Client

from Config import MODEL, SYSTEM_PROMPT
from functions.call_function import call_function


def generate_content(client : Client, tools : types.Tool, verbose : bool, prompt :str | None = None, messages : List[types.Content | types.Part] = []) :
    if not messages :
        messages = [types.Content(role="user",parts=[types.Part(text=prompt)])]
    response = client.models.generate_content(contents=messages, model=MODEL, config=types.GenerateContentConfig(tools=[tools], system_instruction=SYSTEM_PROMPT))
    if response.function_calls :
        for function_call in response.function_calls :
            print(f"Calling function: {function_call.name}({function_call.args})")
            function_res = call_function(function_call, verbose)
            if function_res.parts == None or (function_res.parts and  function_res.parts[0].function_response == None):
                raise Exception("Fatal error, function call yields nothing!")
            if function_res.parts[0].function_response and  function_res.parts[0].function_response.response and verbose:
                print(f"-> {function_res.parts[0].function_response.response}")
            if function_call.name and function_call.args:
                messages.append(types.Part.from_function_call(name=function_call.name, args=function_call.args))
            messages.append(function_res)
        return generate_content(client, tools, verbose=verbose, messages=messages)
    return response