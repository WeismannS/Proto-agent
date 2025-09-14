# Proto-Agent

An educational AI agent framework demonstrating capability-based security and modular toolkit architecture. Built for learning secure AI agent patterns with human oversight and permission controls.

## Features

- **Capability-based security** with granular permission controls
- **CLI tool** with human-in-the-loop approval for dangerous operations
- **Python framework** for building custom agents with programmatic control
- **Modular toolkits** for file operations, system monitoring, and version control
- **Educational focus** - clear, readable code demonstrating AI agent security patterns

## Quick Start

### Installation

```bash
pip install proto-agent # or if you prefer the cli to be used from anywhere: pip install --user proto-agent
```

### Configuration

```bash
proto-agent --help # View CLI options, which include your config path for your OS 
# Example config path for Linux: ~/.config/proto-agent/ will have .env file and config.toml 
```

For Model configuration, please refer to the [Litellm documentation](https://docs.litellm.ai/docs/providers) for your exact name of the model you want to use.
### CLI Usage

```bash
# Safe read-only analysis
proto-agent "Analyze this codebase structure" ./my_project --read-only

# Interactive execution with approval prompts
proto-agent "Run the test suite" ./my_project
# Prompts: "Allow execution of function 'run_python_file'? (y/N):"
```

### Framework Usage

```python
from proto_agent import Agent, AgentConfig
from proto_agent.tool_kits import FileOperationToolkit

# Autonomous mode - no human approval needed
agent = Agent(AgentConfig(
    api_key="your_api_key",
    working_directory="./my_project",
    tools=[FileOperationToolkit(
        enable_read=True,
        enable_write=False,    # Disable risky operations
        enable_execute=False
    ).tool]
))

response = agent.generate_content("Analyze this project's structure")
print(response.text)
```

## Key Concepts

- **CLI Mode**: Interactive approval prompts for dangerous operations
- **Framework Mode**: Full programmatic control over permissions
- **Capability Flags**: Enable/disable specific operations per toolkit
- **Human Oversight**: Configurable approval gates for security

## Available Toolkits

- **📁 FileOperationToolkit**: File reading, writing, and execution
- **💻 SystemInfoToolkit**: System monitoring and resource information
- **🔧 GitToolkit**: Version control operations with safety controls

## Documentation

- **[Complete Documentation](./docs/README-full.md)** - Full guide with examples and architecture
- **[Repository](https://github.com/WeismannS/Proto-agent)** - Source code and issues
- **[Inspiration](https://boot.dev)** - Boot.dev AI Agent Course

## Educational Goals

Proto-Agent prioritizes learning and security over performance:

- Demonstrates secure AI agent design patterns
- Shows human-in-the-loop safety controls
- Provides clear, modular architecture examples
- Emphasizes permission-based security models

Perfect for developers learning about AI agents, security patterns, or needing a foundation for experimentation.

## License

MIT License - see LICENSE file for details.

---

**⭐ Star the repo to support educational AI agent development!**
