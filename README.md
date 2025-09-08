
# Proto-agent

> **Disclaimer:**
> This project is **merely an introduction to AI agents**, created as a personal learning exercise. It is not intended for production use. The code and design are experimental and may lack robustness, security, or best practices required for real-world deployment, Simply put, **do not use this for anything else than simple experimentation**.



This repository is a personal exploration of AI agent concepts in Python. It is not a tool meant for any real-world use, but rather a sandbox to try out ideas and learn about integrating LLMs (Google Gemini) with basic file and code operations. The code demonstrates how an agent might:

* Interpret prompts using an LLM
* Read, write, and list files with boundary checks
* Run Python scripts in a restricted directory
* Use a simple function interface for extensibility
* Include a toy calculator module for demonstration

All features are implemented for experimentation and learning only.


## What This Project Explores

- Using Google Gemini to interpret and act on user prompts
- Implementing file boundary checks for safety
- Running Python code from an agent
- Structuring code for extensibility with new functions
- Building a simple calculator as a test case

## Project Structure

```
AI-Agent/
├── main.py                # Entry point for the AI agent
├── feedback_loop.py       # Handles iterative AI feedback and function calls
├── Config.py              # Configuration and system prompt
├── functions/             # Core function implementations
│   ├── call_function.py
│   ├── get_file_content.py
│   ├── get_files_info.py
│   ├── run_python_file.py
│   ├── write_file.py
├── calculator/            # Example app: Calculator
│   ├── main.py
│   ├── pkg/
│   │   ├── calculator.py
│   │   └── render.py
│   └── tests.py
├── tests.py               # Functionality tests
├── pyproject.toml         # Project metadata and dependencies
├── uv.lock                # Lock file for dependencies
└── README.md              # Project documentation
```

## Setup

1. **Install Python 3.11+**
2. **Install dependencies (recommended):**
	```sh
	uv pip install
	```
	Or, if you prefer pip:
	```sh
	pip install -r requirements.txt
	```
3. **Set up environment variables:**
	- Create a `.env` file with your Google Gemini API key:
	  ```
	  GOOGLE_API_KEY=your_api_key_here
	  ```

## Usage

Run the AI agent with a prompt:

```sh
python main.py "<your prompt>"
# Example:
python main.py "List all files in the calculator directory."
```

To enable verbose output:

```sh
python main.py "<your prompt>" --verbose
```

## Calculator Module

The `calculator` directory contains a simple calculator app that evaluates arithmetic expressions from the command line.

**Usage:**

```sh
cd calculator
python main.py "3 + 5 * 2"
```

**Tests:**

```sh
python tests.py
```

## License

This project is for educational and research purposes.
