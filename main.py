import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os
from feedback_loop import generate_content
from functions.call_function import call_function
from functions.get_files_info import schema_get_files_info
from functions.write_file import schema_write_file
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
from Config import SYSTEM_PROMPT
def main(api_key : str, verbose : bool = False) :
    prompt = sys.argv[1]
    messages = [types.Content(role="user",parts=[types.Part(text=prompt)])]
    gemini_client = genai.Client(api_key=api_key)
    system_prompt = SYSTEM_PROMPT

    tools = types.Tool(function_declarations=[schema_get_files_info,schema_run_python_file, schema_get_file_content,schema_write_file])
    
    response = generate_content(gemini_client,tools,verbose, prompt)
    if not response :
        return
    print(response.text)
    if (verbose and response.usage_metadata) :
        print(f"User prompt: {prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")


if __name__ == "__main__" :
    verbose = False
    if (length := len(sys.argv)) == 1 :
        print("Please provide a valid prompt!")
        exit(1)
    elif length == 3 and sys.argv[2] == '--verbose' :
        verbose = True
    elif length == 2 :
        pass
    else :
        print("Please provide a single prompt and an optional --verbose")
        exit(1)
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key == None :
        raise Exception("Please provide an api key in your .env")
    main(api_key, verbose)
    