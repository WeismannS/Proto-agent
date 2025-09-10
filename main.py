from dotenv import load_dotenv
from google.genai import types
import os
from agent_settings import AgentConfig
from agent import Agent
from functions.get_files_info import schema_get_files_info
from functions.write_file import schema_write_file
from functions.get_file_content import schema_get_file_content
from functions.run_python_file import schema_run_python_file
import click

@click.command()
@click.argument("prompt")
@click.option("--working-directory", default="./calculator", help="The directory the agent can operate in")
@click.option("-v", "--verbose", is_flag=True, help="Enable detailed logging")
@click.option("-a", "--allow-exec", is_flag=True, help="Allow code execution without prompting")
def main(prompt: str, working_directory: str, verbose: bool, allow_exec: bool):
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise Exception("Please provide an api key in your .env")
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
        working_directory=working_directory,
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
    load_dotenv()
    main()
