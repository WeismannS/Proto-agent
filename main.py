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
import argparse


def main(api_key : str, prompt : str, verbose : bool = False) :
    gemini_client = genai.Client(api_key=api_key)
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
    parser = argparse.ArgumentParser(prog="Proto-agent", description="an Ai agent that can read, write and run python files in a contained directory")
    parser.add_argument("prompt", type=str)
    parser.add_argument("-v", "--verbose", required=False,action="store_true")
    args = parser.parse_args()
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key == None :
        raise Exception("Please provide an api key in your .env")
    main(api_key, args.prompt, args.verbose)
    