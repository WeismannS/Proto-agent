from dotenv import load_dotenv
import os
from .agent_settings import AgentConfig
from .agent import Agent
import click
from .tool_kits import FileOperationToolkit, SystemInfoToolkit
import tomllib
import tomli_w
from pathlib import Path
from platformdirs import user_config_dir


@click.command(
    help=f"""Main CLI entry point for the Proto Agent 
    Sets up the agent with specified toolkits and configurations, then processes the user prompt.
    Configuration and API key are loaded from a user-specific config directory 
    {str(Path(user_config_dir("proto-agent")))}
    """
)
@click.argument("prompt")
@click.option(
    "--working-directory",
    default="./calculator",
    help="The directory the agent can operate in",
)
@click.option("-v", "--verbose", is_flag=True, help="Enable detailed logging")
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
    read_only: bool,
    no_system: bool,
):
    config_dir = Path(user_config_dir("proto-agent"))
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.toml"
    env_file = config_dir / ".env"
    if not env_file.exists():
        with env_file.open("wb") as f:
            f.write(b"# Add your GEMINI_API_KEY or API_KEY here\n")
    if not config_file.exists():
        default_config = {"model": "gemini/gemini-2.0-flash-001"}
        with config_file.open("wb") as f:
            tomli_w.dump(default_config, f)
    load_dotenv(dotenv_path=str(env_file.resolve()))
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("API_KEY")
    if api_key is None:
        raise Exception(
            "Please provide an api key in your .env as GEMINI_API_KEY or API_KEY"
        )
    config = tomllib.loads(config_file.read_text())
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
        model=config.get("model", "gemini/gemini-2.0-flash-001"),
        working_directory=working_directory,
        tools=tools,
        verbose=verbose,
        permission_required={FileOperationToolkit.RUN_PYTHON_FILE},
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
    main_cli()
