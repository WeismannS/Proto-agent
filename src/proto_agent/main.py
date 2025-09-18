from dotenv import load_dotenv
import os


from proto_agent.Config import SYSTEM_PROMPT
from .agent_settings import AgentConfig
from .agent import Agent
import click
from .tool_kits import FileOperationToolkit, SystemInfoToolkit, GitToolkit
import tomllib
import tomli_w
from pathlib import Path
from platformdirs import user_config_dir


def _get_user_confirmation(function_name: str, args: dict) -> bool:
    """Get user confirmation for function execution."""
    args_display = {k: v for k, v in args.items() if k != "file_path"}
    choice = input(
        f"Allow execution of function '{function_name}' with args {args_display}? (y/N): "
    ).lower()
    return choice in ("y", "yes")


@click.command(
    help=f"""Main CLI entry point for the Proto Agent 
    Sets up the agent with specified toolkits and configurations, then processes the user prompt.
    Configuration and API key are loaded from a user-specific config directory 
    {str(Path(user_config_dir("proto-agent")))}
    """
)
@click.argument(
    "prompt",
)
@click.argument(
    "working-directory",
)
@click.option("-v", "--verbose", is_flag=True, help="Enable detailed logging")
@click.option(
    "--read-only", is_flag=True, help="Enable only read operations (no write/execute)"
)
@click.option(
    "--no-system", is_flag=True, help="Disable system monitoring capabilities"
)
@click.option("--enable-git", is_flag=True, help="Enable git operations toolkit")
@click.option(
    "--git-read-only",
    is_flag=True,
    help="Enable only git read operations (status, log, diff, blame)",
)
def main_cli(
    prompt: str,
    working_directory: str,
    verbose: bool,
    read_only: bool,
    no_system: bool,
    enable_git: bool,
    git_read_only: bool,
):
    config_dir = Path(user_config_dir("proto-agent"))
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.toml"
    env_file = config_dir / ".env"
    if not env_file.exists():
        with env_file.open("wb") as f:
            f.write(b"# Add your API_KEY here\n")
    if not config_file.exists():
        default_config = {"model": "gemini/gemini-2.0-flash-001"}
        with config_file.open("wb") as f:
            tomli_w.dump(default_config, f)
    load_dotenv(dotenv_path=str(env_file.resolve()))
    api_key = os.environ.get("API_KEY")
    if api_key is None:
        raise Exception("Please provide an api key in your .env API_KEY")
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

    if enable_git:
        if git_read_only:
            git_toolkit = GitToolkit(
                enable_read=True,
                enable_write=False,
                enable_branch=False,
                enable_remote=False,
                enable_history=True,
            )
        else:
            git_toolkit = GitToolkit(
                enable_read=True,
                enable_write=True,
                enable_branch=True,
                enable_remote=True,
                enable_history=True,
            )
        tools.append(git_toolkit.tool)
    configuration = AgentConfig(
        api_key=api_key,
        model=config.get("model", ""),
        working_directory=working_directory,
        tools=tools,
        verbose=verbose,
        permission_callback=_get_user_confirmation,
        permission_required={
            FileOperationToolkit.RUN_PYTHON_FILE,
            GitToolkit.GIT_COMMIT,
            GitToolkit.GIT_PUSH,
            GitToolkit.GIT_BRANCH,
        },
        system_prompt=config.get(("system_prompt"), SYSTEM_PROMPT),
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
