
# Proto-Agent

> **A learning-focused AI agent demonstrating safe code execution patterns with human oversight.**

Proto-Agent is a personal project exploring AI agent concepts in Python. It's a practical implementation of LLM function calling with Google Gemini, featuring human-in-the-loop security and file system operations. While not intended to compete with production AI agents, it serves as a solid foundation for learning and experimentation.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Project Goals

This project was built to explore and demonstrate:
- **AI Agent Architecture**: Clean patterns for LLM function calling
- **Security-First Design**: Human approval for potentially dangerous operations
- **Educational Value**: Readable code that others can learn from and extend
- **Practical Implementation**: Actually works for basic file operations and code execution

**Not intended to be:** A production-ready AI agent or competitor to mainstream tools. This is a personal learning project that others might find useful as a starting point.

## ✨ What It Does

🔒 **Safe Code Execution** - All Python file execution requires user confirmation  
📁 **File Operations** - Read, write, and list files with boundary checking  
🔄 **Conversation Flow** - Maintains context across multiple function calls  
🧮 **Working Example** - Includes a calculator app to demonstrate capabilities  
⚡ **Extensible** - Easy to add new functions via schema definitions  

## 🎯 Great For

- Learning how AI agents work under the hood
- Understanding LLM function calling patterns
- Exploring safe AI-code interaction models
- Building your own AI agent experiments
- Educational projects and AI/ML coursework  
- Exploring safe AI-code interaction models
- Building proof-of-concept automation tools
- Educational AI/ML projects

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

### Usage

**Basic usage:**
```bash
python main.py "List all files in the calculator directory"
```

**With verbose output:**
```bash  
python main.py "Fix any bugs in the calculator and run the tests" --verbose
```

**Example interactions:**
- `"Read the calculator main.py file"`
- `"Run the calculator with the expression 3 + 5 * 2"`  
- `"List all Python files and their sizes"`
- `"Create a new file called hello.py with a hello world function"`

## 🏗️ How It Works

### Simple Architecture

```
Proto-Agent/
├── main.py                # Entry point - CLI interface
├── agent.py               # Main Agent class
├── config.py              # System prompts and configuration
├── agent_settings.py      # Configuration management
├── functions/             # Available AI functions
│   ├── get_file_content.py
│   ├── get_files_info.py
│   ├── run_python_file.py # Sandboxed code execution
│   └── write_file.py
├── calculator/            # Example application
│   ├── main.py           # Calculator CLI
│   ├── tests.py          # Unit tests
│   └── pkg/              # Calculator logic
└── tests.py              # Integration tests
```

### Basic Flow

1. **User Input** → Natural language prompt via CLI
2. **AI Processing** → Gemini interprets intent and selects functions
3. **Security Check** → User approval required for code execution
4. **Function Execution** → Operations within designated working directory  
5. **AI Response** → Results interpreted and presented to user
6. **Context Retention** → Conversation state maintained for multi-step tasks

## 🛡️ Safety Features

- **Sandbox Boundaries**: All operations restricted to working directory
- **User Consent**: Interactive prompts for potentially dangerous operations  
- **Input Validation**: Basic file path and argument checking
- **Execution Limits**: 30-second timeout on code execution
- **Transparency**: All function calls logged and visible

## 🔧 Available Functions

| Function | Description | Security Level |
|----------|-------------|----------------|
| `get_file_content` | Read file contents | Safe |
| `get_files_info` | List directory contents | Safe | 
| `write_file` | Create/modify files | Moderate |
| `run_python_file` | Execute Python scripts | **Requires Approval** |

## 📚 Examples

### Example 1: Code Analysis
```bash
python main.py "Analyze the calculator code and suggest improvements"
```

### Example 2: Bug Fixing  
```bash
python main.py "Find and fix any bugs in the calculator, then run the tests"
```

### Example 3: Documentation Generation
```bash
python main.py "Read all Python files and create a summary of what each function does"
```

## 🚀 Extending the Agent

Want to add your own functions? It's straightforward:

```python
# functions/my_function.py
from google.genai import types

schema_my_function = types.FunctionDeclaration(
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

def my_function(working_directory: str, param: str) -> str:
    # Your implementation here
    return "Success message"
```

Then register it in `functions/call_function.py`. See existing functions for examples.

## 🤝 Contributing

This is a learning project, but contributions are welcome! Areas where you could help:
- Adding new function implementations
- Improving security patterns
- Better error handling
- Documentation improvements
- Example workflows

## 📄 License

MIT License - feel free to use this code for your own learning and projects.

## 🙏 Acknowledgments

- Built with Google Gemini AI for LLM function calling
- Inspired by various AI agent projects and patterns
- Thanks to the Python community for excellent tooling (ruff, uv, etc.)

## ⚠️ Honest Limitations

- **Personal project scope**: Not intended to compete with production AI agents
- **Basic security**: Has safety features but shouldn't be used in untrusted environments
- **API costs**: Google Gemini usage will incur charges
- **Limited functions**: Only basic file operations - extend as needed
- **Educational focus**: Built for learning, not production use

This project demonstrates AI agent concepts in a clean, understandable way. It's a solid foundation for your own experiments, but don't expect it to replace your IDE or compete with commercial AI coding assistants!

---

**Found this helpful? Give it a star ⭐ and feel free to fork it for your own experiments!**
