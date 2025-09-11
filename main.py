from dotenv import load_dotenv
import os
from agent_settings import AgentConfig
from agent import Agent
import click
from tool_kits.file_operation_toolkit import FileOperationToolkit
from tool_kits.system_info_toolkit import SystemInfoToolkit


@click.command()
@click.argument("prompt")
@click.option(
    "--working-directory",
    default="./calculator",
    help="The directory the agent can operate in",
)
@click.option("-v", "--verbose", is_flag=True, help="Enable detailed logging")
@click.option(
    "-a", "--allow-exec", is_flag=True, help="Allow code execution without prompting"
)
@click.option(
    "--read-only", is_flag=True, help="Enable only read operations (no write/execute)"
)
@click.option(
    "--no-system", is_flag=True, help="Disable system monitoring capabilities"
)
def main_cli(
    prompt: str,
    working_directory: str,
    verbose: bool,
    allow_exec: bool,
    read_only: bool,
    no_system: bool,
):
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        raise Exception("Please provide an api key in your .env")

    tools = []

    if read_only:
        file_toolkit = FileOperationToolkit(
            enable_read=True, enable_write=False, enable_list=True, enable_execute=False
        )
        tools.append(file_toolkit.tool)
    else:
        file_toolkit = FileOperationToolkit(
            enable_read=True, enable_write=True, enable_list=True, enable_execute=True
        )
        tools.append(file_toolkit.tool)

    if not no_system:
        system_toolkit = SystemInfoToolkit(
            enable_basic=True,
            enable_memory=True,
            enable_disk=True,
            enable_cpu=True,
            enable_network=False,
            enable_processes=False,
        )
        tools.append(system_toolkit.tool)

    configuration = AgentConfig(
        api_key=api_key,
        working_directory=working_directory,
        tools=tools,
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
    main_cli()
