from dotenv import load_dotenv
import os
from .agent_settings import AgentConfig
from .agent import Agent
import click
from .tool_kits import FileOperationToolkit, SystemInfoToolkit

def create_agent(
    api_key: str,
    working_directory: str = "./calculator",
    verbose: bool = False,
    allow_exec: bool = False,
    read_only: bool = False,
    no_system: bool = False,
) -> Agent:
    """
    Create and configure an Agent instance for use as a library.

    Args:
        api_key: The API key for the LLM service.
        working_directory: Directory the agent can operate in.
        verbose: Enable detailed logging.
        allow_exec: Allow code execution without prompting.
        read_only: Enable only read operations.
        no_system: Disable system monitoring.

    Returns:
        Configured Agent instance.
    """
    
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

    return Agent(configuration)


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
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("API_KEY")
    if api_key is None:
        raise Exception(
            "Please provide an api key in your .env as GEMINI_API_KEY or API_KEY"
        )

    agent = create_agent(
        api_key=api_key,
        working_directory=working_directory,
        verbose=verbose,
        allow_exec=allow_exec,
        read_only=read_only,
        no_system=no_system,
    )

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
