
# Proto-Agent

> **A modular AI agent with capability-based security and extensible toolkit architecture.**

Proto-Agent is a Python-based AI agent that demonstrates modern LLM function calling patterns with Google Gemini. It features a modular toolkit system with fine-grained capability control, human-in-the-loop security, and clean architecture. Built for learning, experimentation, and as a solid foundation for custom AI agent projects.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Key Features

🧩 **Modular Toolkit System** - Self-contained toolkits with capability-based controls  
🔒 **Fine-Grained Security** - Individual flags for read/write/execute permissions  
📊 **System Monitoring** - Real-time system metrics with psutil integration  
🎛️ **Flexible CLI** - Rich command-line interface with mode-specific flags  
🏗️ **Extensible Architecture** - Easy to add new toolkits and capabilities  
🛡️ **Safe by Default** - Human approval required for potentially dangerous operations

## 📦 Available Toolkits

### 📁 FileOperationToolkit
Complete file system operations with boundary protection:
- **Read operations**: `get_file_content`, `get_files_info`  
- **Write operations**: `write_file` with safety validation
- **Code execution**: `run_python_file` with user confirmation
- **Capability flags**: `enable_read`, `enable_write`, `enable_list`, `enable_execute`

### 💻 SystemInfoToolkit  
Comprehensive system monitoring and hardware information:
- **Basic info**: Platform, architecture, Python version
- **Memory monitoring**: Virtual and swap memory usage
- **Disk usage**: Storage statistics and partition information
- **CPU metrics**: Core count, frequency, real-time usage
- **Network info**: Interface details and I/O statistics  
- **Process listing**: Running processes with resource usage
- **Capability flags**: `enable_basic`, `enable_memory`, `enable_disk`, `enable_cpu`, `enable_network`, `enable_processes`

## 🎯 Perfect For

- **Learning AI Agents**: Understand modern LLM function calling patterns and architecture
- **Security Research**: Explore capability-based access control models in AI systems
- **Automation Projects**: Build tools with selective permissions and human oversight
- **Educational Use**: Clean, readable codebase for AI/ML courses and workshops
- **Prototyping**: Solid foundation for experimenting with AI agent concepts
- **Code Examples**: Reference implementation for your own AI agent projects

## 📦 Quick Start

### Prerequisites
- Python 3.11 or higher
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/WeismannS/Proto-agent.git
   cd Proto-agent
   ```

2. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv pip install -e .
   
   # Or using pip
   pip install -e .
   ```

3. **Set up your API key**
   ```bash
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

### Usage Examples

**Basic file operations:**
```bash
python main.py "List all files in the current directory"
```

**Read-only mode (safe exploration):**
```bash
python main.py "Analyze the codebase structure" --read-only
```

**System monitoring:**
```bash
python main.py "Show me system performance metrics" --verbose
```

**Disable system access:**
```bash
python main.py "Help me organize these files" --no-system
```

**Allow code execution:**
```bash
python main.py "Run the calculator tests and fix any issues" --allow-exec
```

## 🏗️ Architecture Overview

### Modular Design

```
Proto-Agent/
├── main.py                     # CLI entry point with toolkit composition
├── agent.py                    # Core Agent class and function calling logic
├── agent_settings.py           # Configuration management
├── tool_kit_registry.py        # Global function registry with collision protection
├── Config.py                   # System prompts and constants
├── tool_kits/                  # Modular toolkit system
│   ├── __init__.py            # Package exports
│   ├── base_toolkit.py        # Abstract base class for all toolkits
│   ├── file_operation_toolkit.py  # File system operations
│   └── system_info_toolkit.py     # System monitoring capabilities
└── calculator/                 # Example application demonstrating usage
    ├── main.py                # Calculator CLI
    ├── tests.py               # Unit tests
    └── pkg/                   # Calculator implementation
```

### Capability-Based Security Model

Each toolkit implements fine-grained permission controls:

```python
# Read-only file access
file_toolkit = FileOperationToolkit(
    enable_read=True,
    enable_write=False,
    enable_list=True,
    enable_execute=False
)

# Limited system monitoring  
system_toolkit = SystemInfoToolkit(
    enable_basic=True,
    enable_memory=True,
    enable_disk=False,
    enable_cpu=False,
    enable_network=False,
    enable_processes=False
)
```

### Data Flow

1. **CLI Parsing** → Click framework processes arguments and flags
2. **Toolkit Composition** → Toolkits instantiated based on capability requirements
3. **Agent Initialization** → LLM client configured with composed toolkits
4. **Function Calling** → Gemini selects and calls registered functions
5. **Security Gates** → Human approval for sensitive operations
6. **Execution** → Functions run within security boundaries
7. **Response** → Results processed and returned to user

## 🛡️ Security Features

### Multi-Layer Protection
- **Capability Flags**: Functions only available if explicitly enabled
- **Boundary Checking**: All file operations restricted to working directory
- **User Confirmation**: Interactive prompts for code execution
- **Registry Protection**: Prevents function name collisions
- **Input Validation**: Parameter checking and type safety
- **Execution Limits**: 30-second timeout on subprocess operations

### Permission Levels
| Permission Level | Operations | Risk Level |
|-----------------|------------|------------|
| **Read-only** | File reading, directory listing | 🟢 Safe |
| **Write** | File creation/modification | 🟡 Moderate |
| **Execute** | Python script execution | 🔴 **Requires Approval** |
| **System** | Hardware monitoring | � Moderate |
| **Network** | Interface information | 🟡 Moderate |
| **Processes** | Process listing | 🟡 Moderate |

## 🔧 CLI Reference

```bash
python main.py "Your prompt here" [OPTIONS]

Options:
  --working-directory TEXT    Directory for agent operations (default: ./calculator)
  -v, --verbose              Enable detailed logging
  -a, --allow-exec           Allow code execution without prompting  
  --read-only               Enable only read operations (no write/execute)
  --no-system               Disable system monitoring capabilities
  --help                    Show this message and exit
```

### Usage Patterns

**Safe exploration:**
```bash
python main.py "What files are in this project?" --read-only
```

**Development workflow:**
```bash
python main.py "Analyze the code, run tests, and suggest improvements" --allow-exec -v
```

**System administration:**
```bash
python main.py "Check system resources and running processes" --verbose
```

**Restricted environment:**
```bash
python main.py "Help organize these files" --read-only --no-system
```

## 🚀 Extending Proto-Agent

### Creating a New Toolkit

1. **Inherit from ToolKit base class:**

```python
# tool_kits/my_custom_toolkit.py
from .base_toolkit import ToolKit
from tool_kit_registry import ToolKitRegistery
from google.genai import types

class MyCustomToolkit(ToolKit):
    def __init__(self, enable_feature_a=True, enable_feature_b=False):
        super().__init__()
        self.enable_feature_a = enable_feature_a
        self.enable_feature_b = enable_feature_b
        self._register_functions()
```

2. **Implement required methods:**

```python
    def _my_function(self, working_directory: str, param: str) -> str:
        """Implementation of your custom function"""
        return f"Result: {param}"

    def _register_functions(self):
        """Register functions based on enabled capabilities"""
        if self.enable_feature_a:
            schema = types.FunctionDeclaration(
                name="my_function",
                description="What this function does",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "param": types.Schema(
                            type=types.Type.STRING,
                            description="Parameter description"
                        )
                    }
                )
            )
            self.schemas.append(schema)
            ToolKitRegistery.register("my_function", self._my_function, schema)

    @property
    def tool(self) -> types.Tool:
        return types.Tool(function_declarations=self.schemas)
```

3. **Add to package exports:**

```python
# tool_kits/__init__.py
from .my_custom_toolkit import MyCustomToolkit

__all__ = ["ToolKit", "FileOperationToolkit", "SystemInfoToolkit", "MyCustomToolkit"]
```

4. **Use in main.py:**

```python
from tool_kits import MyCustomToolkit

# In main_cli function:
custom_toolkit = MyCustomToolkit(enable_feature_a=True)
tools.append(custom_toolkit.tool)
```

### Best Practices

- **Capability flags**: Always implement granular permission controls
- **Error handling**: Return descriptive error messages, don't raise exceptions
- **Security validation**: Check inputs and boundaries in your functions
- **Documentation**: Clear docstrings and parameter descriptions
- **Testing**: Create test cases for your toolkit functions

## 📚 Examples & Use Cases

### Example 1: Code Analysis & Testing
```bash
python main.py "Read all Python files, analyze the code quality, and run any available tests" --allow-exec --verbose
```

### Example 2: System Health Check
```bash
python main.py "Give me a comprehensive system health report including CPU, memory, and disk usage"
```

### Example 3: Safe File Organization
```bash
python main.py "Analyze the file structure and suggest an organization strategy" --read-only
```

### Example 4: Development Workflow
```bash
python main.py "Review the calculator code, identify any bugs, fix them, and verify with tests" --allow-exec
```

### Example 5: Documentation Generation
```bash
python main.py "Read all source files and create comprehensive documentation" --read-only --verbose
```

## 🤝 Contributing

Contributions are welcome! Areas where you can help:

- **New Toolkits**: Database operations, web scraping, API interactions
- **Security Enhancements**: Additional validation layers, audit logging
- **Performance**: Async operations, caching, optimization
- **Documentation**: Tutorials, examples, API documentation
- **Testing**: Unit tests, integration tests, security tests

### Development Setup

```bash
# Install development dependencies
uv add --group dev ruff pytest

# Run linting
uv run ruff check

# Run tests
uv run pytest
```

## 📄 License

MIT License - feel free to use this code for your own projects.

## 🙏 Acknowledgments

- Built with Google Gemini AI for advanced LLM function calling
- Uses psutil for comprehensive system monitoring
- Click framework for professional CLI interface
- Inspired by modern AI agent architectures and security patterns
- Boot.dev for the ai agent course which inspired this project
## ⭐ Why This Matters

Proto-Agent demonstrates how to build **well-architected AI agents** with:
- **Granular control** over AI capabilities through permission flags
- **Professional code organization** with modular, extensible design
- **Educational clarity** for understanding modern AI agent patterns
- **Security-first approach** with human oversight for sensitive operations

Whether you're learning about AI agents, building automation tools, or researching AI safety patterns, Proto-Agent provides a solid, well-architected example to learn from and build upon.

---

**Ready to build your own AI agent? ⭐ Star this repo and start experimenting!**
