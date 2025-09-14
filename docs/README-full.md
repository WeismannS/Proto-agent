# Proto-Agent - Complete Documentation

## What is Proto-Agent?

[Proto-Agent](https://github.com/WeismannS/Proto-agent) is an educational AI agent framework designed to demonstrate capability-based security and modular toolkit architecture. Built as a learning project inspired by [Boot.dev's AI agent course](https://boot.dev), it shows how to implement secure, permission-controlled AI agents with human oversight.

Proto-Agent provides both a **CLI tool** with built-in safety controls and a **Python framework** for building custom agents. The CLI includes human-in-the-loop approval for dangerous operations, while the framework gives you complete control over permission handling.

**As a CLI tool** - Interactive safety controls:

```bash
proto-agent "Run the tests and fix any issues" ./my_project
# Will prompt: "Allow execution of function 'run_python_file'? (y/N):"
```

**As a Python framework** - Programmatic control:

```python
from proto_agent import Agent, AgentConfig
from proto_agent.tool_kits import FileOperationToolkit

agent = Agent(AgentConfig(
    api_key="your_api_key",
    working_directory="./my_project",
    tools=[FileOperationToolkit(enable_execute=False).tool]
))
agent.generate_content("Analyze this codebase and suggest improvements")
```

The main educational value of Proto-Agent comes from its **dual-layer design patterns**:

1. **Capability-based permissions** with individual flags for read/write/execute operations, showing how to implement fine-grained access control in AI agents.
2. **Configurable human oversight** - the CLI implements interactive approval while the framework lets you define your own permission callbacks or run without human intervention.
3. **Modular toolkit architecture** where capabilities are composed from reusable, testable components with clear security boundaries.

For developers learning about AI agents, Proto-Agent provides a well-documented example. You get clear patterns for building secure agents, modular toolkit design that's easy to understand and extend, and capability-based security that shows best practices for production systems.

While not as performant or feature-rich as frameworks like Agno, Proto-Agent focuses on educational clarity and security patterns that are valuable for understanding how to build trustworthy AI automation.

## Getting started

If you're new to Proto-Agent, follow our [quickstart](#quick-start) to build your first Agent with capability controls and learn the core patterns.

After that, check out the [toolkit examples](#examples--use-cases) to see how the modular architecture works in practice.

## Documentation, Community & More examples

- Repository: <a href="https://github.com/WeismannS/Proto-agent" target="_blank" rel="noopener noreferrer">github.com/WeismannS/Proto-agent</a>
- Examples: <a href="#examples--use-cases" target="_blank" rel="noopener noreferrer">Use Cases & Examples</a>
- Architecture: <a href="#architecture-overview" target="_blank" rel="noopener noreferrer">System Architecture</a>
- Inspiration: <a href="https://boot.dev" target="_blank" rel="noopener noreferrer">Boot.dev AI Agent Course</a>

## Design Philosophy

Proto-Agent was built to explore **security and modularity** in AI agent design. As an educational project, it prioritizes:

- **Clear, readable code** that demonstrates key concepts
- **Security by design** with explicit permission models
- **Modular architecture** that's easy to understand and extend
- **Educational value** over raw performance

> Built for learning and experimentation, not production performance.

The framework shows how capability-based security can be implemented without significant complexity, making it a good reference for understanding these patterns. While other frameworks optimize for speed and features, Proto-Agent optimizes for clarity and safety.

### Learning Focus

Proto-Agent helps developers understand:

- How to implement fine-grained permissions in AI agents
- Patterns for human-in-the-loop safety controls
- Modular toolkit architecture and composition
- Security boundaries and input validation
- Function calling patterns with modern LLMs

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Your API key for your chosen LLM (e.g., Google Gemini, OpenAI)

### Installation

```bash
# Install from PyPI
pip install proto-agent

# Or install from source
git clone https://github.com/WeismannS/Proto-agent.git
cd Proto-agent
pip install -e .
```

### Configuration

Proto-Agent uses a user-specific configuration directory for API keys and settings:

```bash
# Your config will be stored at:
# ~/.config/proto-agent/config.toml
# ~/.config/proto-agent/.env

# Add your API key
echo "API_KEY=your_api_key_here" >> ~/.config/proto-agent/.env
```

### CLI Usage (With Human Approval)

The CLI tool includes built-in safety prompts for dangerous operations:

**Safe file analysis:**

```bash
proto-agent "Analyze this codebase structure" ./my_project --read-only
```

**Interactive code execution:**

```bash
proto-agent "Run the test suite and report results" ./my_project
# Will prompt: "Allow execution of function 'run_python_file' with args {...}? (y/N):"
```

**Development workflow with git safety:**

```bash
proto-agent "Review changes and suggest commit message" ./my_project --enable-git
# Git commits require approval, but git status/log/diff do not
```

### Framework Usage (Programmatic Control)

Proto-Agent can be used as a Python library where you control all permission handling:

```python
from proto_agent import Agent, AgentConfig
from proto_agent.tool_kits import FileOperationToolkit, SystemInfoToolkit

# Option 1: No human approval - framework runs autonomously
config = AgentConfig(
    api_key="your_api_key",
    working_directory="./my_project",
    tools=[
        FileOperationToolkit(
            enable_read=True,
            enable_write=False,  # Disable risky operations entirely
            enable_execute=False
        ).tool,
        SystemInfoToolkit(enable_processes=False).tool
    ],
    verbose=True
    # No permission_callback - runs without prompts
)

# Option 2: Custom approval logic
def custom_approval(function_name: str, args: dict) -> bool:
    # Your custom logic here
    if function_name == "run_python_file":
        return "test" in args.get("file_path", "").lower()
    return True  # Allow other operations

config_with_custom_approval = AgentConfig(
    api_key="your_api_key",
    working_directory="./my_project",
    tools=[FileOperationToolkit().tool],
    permission_callback=custom_approval,
    permission_required={"run_python_file"}
)

agent = Agent(config)
response = agent.generate_content("Analyze this project's structure")
print(response.text)
```

**Key Framework Concepts:**

- `permission_callback`: Optional function that controls approval behavior
- `permission_required`: Set of function names that need approval
- **No callback**: Agent runs autonomously (framework mode)
- **Custom callback**: Your own approval logic (programmatic mode)
- **CLI callback**: Interactive terminal prompts (CLI mode)

## Architecture Overview

### Educational Architecture Goals

Proto-Agent demonstrates several important patterns for AI agent security:

```
Security Model:
├── READ: File access, directory listing        [🟢 Safe]
├── WRITE: File modification, creation          [🟡 Moderate]
├── EXECUTE: Code execution, subprocess         [🔴 Requires Approval]
├── SYSTEM: Hardware monitoring, processes      [🟡 Moderate]
└── NETWORK: Interface info, connectivity       [🟡 Moderate]
```

### Modular Toolkit System

```
Proto-Agent/
├── Core Agent (LLM Integration)
├── Toolkit Registry (Function Management)
├── Security Layer (Permission Checks)
└── Toolkits/
    ├── FileOperationToolkit    # File operations
    ├── SystemInfoToolkit       # System monitoring
    ├── GitToolkit             # Version control
    └── CustomToolkit          # Extension examples
```

### CLI vs Framework Architecture

Proto-Agent demonstrates two different approaches to AI agent safety:

**CLI Tool Architecture:**

```
User Command → CLI Parser → Agent Configuration → Human Approval Gates → Toolkit Execution
```

The CLI automatically configures these approval gates:

- `run_python_file` (File execution)
- `git_commit` (Git commits)
- `git_push` (Remote operations)
- `git_branch` (Branch operations)

**Framework Architecture:**

```
Your Code → Agent Configuration → Custom Permission Logic → Toolkit Execution
```

The framework gives you full control:

- Choose which functions require approval
- Implement your own approval logic
- Run completely autonomously
- Integrate with your own UI/workflow

## Available Toolkits

### 📁 FileOperationToolkit

Basic file system operations with security boundaries:

```python
FileOperationToolkit(
    enable_read=True,      # File reading, content access
    enable_write=True,     # File creation, modification
    enable_list=True,      # Directory listing
    enable_execute=False,  # Python script execution
)
```

**Functions**: `get_file_content`, `write_file`, `get_files_info`, `run_python_file`

### 💻 SystemInfoToolkit

System monitoring with selective access controls:

```python
SystemInfoToolkit(
    enable_basic=True,     # Platform info, hostname
    enable_memory=True,    # RAM and swap usage
    enable_disk=True,      # Storage statistics
    enable_cpu=True,       # Processor metrics
    enable_network=False,  # Interface details
    enable_processes=False # Running processes
)
```

**Functions**: `get_system_info`, `get_memory_usage`, `get_cpu_info`, `list_processes`

### 🔧 GitToolkit

Version control operations with permission controls:

```python
GitToolkit(
    enable_read=True,      # Status, logs, diffs
    enable_write=False,    # Commits, staging
    enable_branch=False,   # Branch management
    enable_remote=False,   # Push/pull operations
    enable_history=True    # Commit history, blame
)
```

**Functions**: `git_status`, `git_log`, `git_diff`, `git_commit`, `git_push`

## Security Features

### Educational Security Patterns

**CLI Safety Model** (Interactive Approval):

- **Capability Flags**: Functions only available when explicitly enabled
- **Boundary Checking**: All operations restricted to working directory
- **Human Approval**: Interactive terminal prompts for dangerous operations
- **Pre-configured Gates**: CLI automatically protects risky functions

**Framework Flexibility** (Your Control):

- **Custom Approval Logic**: Implement your own permission callbacks
- **Autonomous Mode**: Run without human intervention when safe
- **Selective Protection**: Choose exactly which functions need approval
- **Integration Ready**: Embed in larger applications with custom UI

### Permission Examples

| Toolkit    | Safe Operations | Moderate Risk | High Risk    |
| ---------- | --------------- | ------------- | ------------ |
| **File**   | Read, List      | Write         | Execute      |
| **System** | Basic Info      | Memory/CPU    | Processes    |
| **Git**    | Status, Log     | Diff, Blame   | Commit, Push |

## Examples & Use Cases

### Example 1: Safe Code Analysis

```bash
proto-agent "Review this code for potential issues" \
  ./my_app --read-only --verbose
```

### Example 2: Framework - Custom Permission Logic

```python
from proto_agent import Agent, AgentConfig
from proto_agent.tool_kits import FileOperationToolkit

# Custom approval logic for learning
def smart_approval(function_name: str, args: dict) -> bool:
    if function_name == "run_python_file":
        file_path = args.get("file_path", "")
        # Only allow test files to run
        return "test" in file_path.lower()
    return True  # Allow other operations

agent = Agent(AgentConfig(
    api_key="your_key",
    working_directory="./test_project",
    tools=[FileOperationToolkit().tool],
    permission_callback=smart_approval,
    permission_required={"run_python_file"}
))

# This will auto-approve test files, reject others
response = agent.generate_content("Run any test files you find")
```

### Example 3: Framework - Autonomous Mode

```python
# No human approval needed - just disable risky operations
safe_agent = Agent(AgentConfig(
    api_key="your_key",
    working_directory="./analysis_project",
    tools=[FileOperationToolkit(
        enable_read=True,
        enable_write=False,  # Completely disable writes
        enable_execute=False  # Completely disable execution
    ).tool]
    # No permission_callback = fully autonomous
))

# Runs completely autonomously
response = safe_agent.generate_content("Analyze all source files and create a summary")
```

### Example 4: Git Integration Example

```bash
proto-agent "Show git status and recent changes" \
  ./my_repo --enable-git --git-read-only
```

## Extending Proto-Agent

### Learning to Build Custom Toolkits

Proto-Agent makes it easy to understand how to build secure, modular toolkits:

```python
from proto_agent.tool_kits import ToolKit
from proto_agent.tool_kit_registry import ToolKitRegistery
from proto_agent.types_llm import FunctionDeclaration, Tool

class ExampleToolkit(ToolKit):
    def __init__(self, enable_basic=True):
        super().__init__()
        self.enable_basic = enable_basic
        self._register_functions()

    def _register_functions(self):
        if self.enable_basic:
            schema = FunctionDeclaration(
                name="example_function",
                description="An example function for learning",
                parameters={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "Test message"}
                    },
                    "required": ["message"]
                }
            )
            self.schemas.append(schema)
            ToolKitRegistery.register("example_function", self._example_func, schema)

    def _example_func(self, working_directory: str, message: str) -> str:
        return f"Example response: {message}"

    @property
    def tool(self) -> Tool:
        return Tool(function_declarations=self.schemas)
```

### Learning Principles

- **Start simple** - Begin with read-only operations
- **Add safety controls** - Implement approval gates for risky operations
- **Validate inputs** - Always check parameters before execution
- **Use clear naming** - Make capability flags obvious
- **Document thoroughly** - Explain security decisions and boundaries

## CLI Reference

```bash
proto-agent "Your prompt here" <working_directory> [OPTIONS]

Options:
  -v, --verbose              Enable detailed logging
  --read-only               Enable only read operations
  --no-system               Disable system monitoring
  --enable-git              Enable git operations toolkit
  --git-read-only           Enable only git read operations
  --help                    Show this message and exit
```

### CLI Examples (Interactive Mode)

**Understanding CLI permissions:**

```bash
proto-agent "What files are here?" ./code --read-only
# No prompts - read operations are always safe
```

**Learning about approval prompts:**

```bash
proto-agent "Run the tests" ./app --verbose
# Will prompt: "Allow execution of function 'run_python_file'...? (y/N):"
```

**Experimenting with different toolkits:**

```bash
proto-agent "Show system info" ./logs --no-system
# Disables system toolkit entirely
```

### Framework Examples (Programmatic Mode)

**Autonomous analysis:**

```python
# No approvals needed - agent runs completely independently
agent = create_safe_agent()
result = agent.generate_content("Analyze this codebase")
```

**Custom permission logic:**

```python
# Your own approval rules
agent = create_agent_with_custom_permissions()
result = agent.generate_content("Review and improve the code")
```

## Educational Value

Proto-Agent demonstrates important concepts for building trustworthy AI agents:

- **Security-first design** with explicit permission boundaries
- **Human oversight patterns** for maintaining control over automation
- **Modular architecture** that separates concerns and enables testing
- **Clear code organization** that's easy to understand and modify

Whether you're learning about AI agents, exploring security patterns, or need a foundation for experimentation, Proto-Agent provides a well-documented example that prioritizes clarity and safety over performance.

This project shows one approach to building agents you can understand and trust, making it valuable for education and as a starting point for more specialized tools.

---

**Interested in learning about secure AI agents? ⭐ Star the repo and start exploring!**
