from dotenv import load_dotenv
from google.genai import types
import os
from agent_settings import AgentConfig
from agent import Agent
from functions.get_files_info import schema_get_files_info
from functions.write_file import schema_write_file
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
import argparse


def main(api_key: str, args: argparse.Namespace):
    verbose = args.verbose
    allow_exec = args.allow_exec
    prompt = args.prompt
    tool = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_run_python_file,
            schema_get_file_content,
            schema_write_file,
        ]
    )
    configuration = AgentConfig(
        api_key=api_key,
        working_directory="./calculator",
        tools=[tool],
        allow_exec=allow_exec,
        verbose=verbose,
    )
    agent = Agent(configuration)
    response = agent.generate_content(prompt=prompt)
    if not response:
        return
    print(response.text)
    if verbose and response.usage_metadata:
        print(f"User prompt: {prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Proto-agent",
        description="an Ai agent that can read, write and run python files in a contained directory",
    )
    parser.add_argument("prompt", type=str)
    parser.add_argument("-v", "--verbose", required=False, action="store_true")
    parser.add_argument("-a", "--allow-exec", required=False, action="store_true")
    args = parser.parse_args()
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise Exception("Please provide an api key in your .env")
    main(api_key, args)
