import subprocess
from pathlib import Path
from typing import Optional, List
import json
from ..tool_kit_registry import ToolKitRegistery
from ..types_llm import FunctionDeclaration, Tool
from .base_toolkit import ToolKit


def _run_git_command(working_directory: str, args: List[str]) -> dict:
    """Run a git command and return structured output"""
    try:
        if not Path(working_directory).is_dir():
            return {"error": f"Directory '{working_directory}' does not exist"}

        git_check = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if git_check.returncode != 0:
            return {"error": "Not a git repository"}

        result = subprocess.run(
            ["git"] + args,
            cwd=working_directory,
            capture_output=True,
            text=True,
            timeout=30,
        )

        return {
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "success": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {"error": "Git command timed out"}
    except Exception as e:
        return {"error": f"Failed to run git command: {str(e)}"}


def git_status(working_directory: str) -> str:
    """Get git status with file details"""
    result = _run_git_command(working_directory, ["status", "--porcelain", "-b"])

    if "error" in result:
        return f"Error: {result['error']}"

    if not result["success"]:
        return f"Git status failed: {result['stderr']}"

    lines = result["stdout"].split("\n") if result["stdout"] else []
    status_info = {
        "branch": "unknown",
        "ahead": 0,
        "behind": 0,
        "staged": [],
        "modified": [],
        "untracked": [],
        "deleted": [],
    }

    for line in lines:
        if not line:
            continue

        if line.startswith("##"):
            # Branch info line
            branch_info = line[3:]
            if "..." in branch_info:
                local, remote_info = branch_info.split("...")
                status_info["branch"] = local.strip()
                if "[ahead" in remote_info:
                    # Parse ahead/behind info
                    if "ahead" in remote_info:
                        ahead_part = (
                            remote_info.split("ahead ")[1].split("]")[0].split(",")[0]
                        )
                        status_info["ahead"] = int(ahead_part)
                    if "behind" in remote_info:
                        behind_part = remote_info.split("behind ")[1].split("]")[0]
                        status_info["behind"] = int(behind_part)
            else:
                status_info["branch"] = branch_info.strip()
        else:
            # File status line
            status_code = line[:2]
            filename = line[3:]

            if status_code[0] in "AM":
                status_info["staged"].append(filename)
            if status_code[1] == "M":
                status_info["modified"].append(filename)
            elif status_code[1] == "D":
                status_info["deleted"].append(filename)
            elif status_code == "??":
                status_info["untracked"].append(filename)

    return json.dumps(status_info, indent=2)


def git_log(
    working_directory: str, limit: int = 10, branch: Optional[str] = None
) -> str:
    """Get git commit history"""
    args = ["log", f"-{limit}", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso"]
    if branch:
        args.append(branch)

    result = _run_git_command(working_directory, args)

    if "error" in result:
        return f"Error: {result['error']}"

    if not result["success"]:
        return f"Git log failed: {result['stderr']}"

    commits = []
    for line in result["stdout"].split("\n") if result["stdout"] else []:
        if "|" in line:
            hash_val, author, email, date, message = line.split("|", 4)
            commits.append(
                {
                    "hash": hash_val,
                    "author": author,
                    "email": email,
                    "date": date,
                    "message": message,
                }
            )

    return json.dumps({"commits": commits, "total_shown": len(commits)}, indent=2)


def git_diff(
    working_directory: str, file_path: Optional[str] = None, staged: bool = False
) -> str:
    """Get git diff for files"""
    args = ["diff"]
    if staged:
        args.append("--staged")
    if file_path:
        args.append(file_path)

    result = _run_git_command(working_directory, args)

    if "error" in result:
        return f"Error: {result['error']}"

    if not result["success"]:
        return f"Git diff failed: {result['stderr']}"

    return result["stdout"] if result["stdout"] else "No changes found"


def git_add(working_directory: str, files: List[str]) -> str:
    """Stage files for commit"""
    if not files:
        return "Error: No files specified to add"

    args = ["add"] + files
    result = _run_git_command(working_directory, args)

    if "error" in result:
        return f"Error: {result['error']}"

    if result["success"]:
        return f"Successfully staged {len(files)} file(s): {', '.join(files)}"
    else:
        return f"Failed to stage files: {result['stderr']}"


def git_commit(
    working_directory: str, message: str, files: Optional[List[str]] = None
) -> str:
    """Create a git commit"""
    if not message:
        return "Error: Commit message is required"

    args = ["commit", "-m", message]
    if files:
        args.extend(files)

    result = _run_git_command(working_directory, args)

    if "error" in result:
        return f"Error: {result['error']}"

    if result["success"]:
        return f"Commit created successfully: {message}\n{result['stdout']}"
    else:
        return f"Commit failed: {result['stderr']}"


def git_branch(
    working_directory: str, action: str = "list", branch_name: Optional[str] = None
) -> str:
    """Manage git branches"""
    if action == "list":
        args = ["branch", "-a"]
    elif action == "create" and branch_name:
        args = ["branch", branch_name]
    elif action == "switch" and branch_name:
        args = ["checkout", branch_name]
    elif action == "delete" and branch_name:
        args = ["branch", "-d", branch_name]
    else:
        return "Error: Invalid branch action or missing branch name"

    result = _run_git_command(working_directory, args)

    if "error" in result:
        return f"Error: {result['error']}"

    if result["success"]:
        return (
            result["stdout"]
            if result["stdout"]
            else f"Branch operation '{action}' completed successfully"
        )
    else:
        return f"Branch operation failed: {result['stderr']}"


def git_remote(
    working_directory: str,
    action: str = "list",
    remote_name: Optional[str] = None,
    url: Optional[str] = None,
) -> str:
    """Manage git remotes"""
    if action == "list":
        args = ["remote", "-v"]
    elif action == "add" and remote_name and url:
        args = ["remote", "add", remote_name, url]
    elif action == "remove" and remote_name:
        args = ["remote", "remove", remote_name]
    else:
        return "Error: Invalid remote action or missing parameters"

    result = _run_git_command(working_directory, args)

    if "error" in result:
        return f"Error: {result['error']}"

    if result["success"]:
        return (
            result["stdout"]
            if result["stdout"]
            else f"Remote operation '{action}' completed successfully"
        )
    else:
        return f"Remote operation failed: {result['stderr']}"


def git_push(
    working_directory: str, remote: str = "origin", branch: Optional[str] = None
) -> str:
    """Push changes to remote repository"""
    args = ["push", remote]
    if branch:
        args.append(branch)

    result = _run_git_command(working_directory, args)

    if "error" in result:
        return f"Error: {result['error']}"

    if result["success"]:
        return f"Push successful:\n{result['stdout']}"
    else:
        return f"Push failed: {result['stderr']}"


def git_pull(
    working_directory: str, remote: str = "origin", branch: Optional[str] = None
) -> str:
    """Pull changes from remote repository"""
    args = ["pull", remote]
    if branch:
        args.append(branch)

    result = _run_git_command(working_directory, args)

    if "error" in result:
        return f"Error: {result['error']}"

    if result["success"]:
        return f"Pull successful:\n{result['stdout']}"
    else:
        return f"Pull failed: {result['stderr']}"


def git_blame(
    working_directory: str, file_path: str, line_range: Optional[str] = None
) -> str:
    """Show git blame for a file"""
    if not file_path:
        return "Error: File path is required"

    args = ["blame", "--line-porcelain"]
    if line_range:
        args.extend(["-L", line_range])
    args.append(file_path)

    result = _run_git_command(working_directory, args)

    if "error" in result:
        return f"Error: {result['error']}"

    if not result["success"]:
        return f"Git blame failed: {result['stderr']}"

    return result["stdout"] if result["stdout"] else "No blame information available"


# Schema definitions
schema_git_status = FunctionDeclaration(
    name="git_status",
    description="Get current git repository status including branch, staged/modified files, and tracking info",
    parameters={"type": "object", "properties": {}},
)

schema_git_log = FunctionDeclaration(
    name="git_log",
    description="Show git commit history with author, date, and commit messages",
    parameters={
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Number of commits to show (default: 10)",
            },
            "branch": {
                "type": "string",
                "description": "Specific branch to show history for (optional)",
            },
        },
    },
)

schema_git_diff = FunctionDeclaration(
    name="git_diff",
    description="Show differences between working directory and last commit, or staged changes",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Specific file to show diff for (optional)",
            },
            "staged": {
                "type": "boolean",
                "description": "Show staged changes instead of working directory changes",
            },
        },
    },
)

schema_git_add = FunctionDeclaration(
    name="git_add",
    description="Stage files for commit",
    parameters={
        "type": "object",
        "properties": {
            "files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of file paths to stage",
            }
        },
        "required": ["files"],
    },
)

schema_git_commit = FunctionDeclaration(
    name="git_commit",
    description="Create a commit with staged changes",
    parameters={
        "type": "object",
        "properties": {
            "message": {"type": "string", "description": "Commit message"},
            "files": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific files to commit (optional, uses staged files if not provided)",
            },
        },
        "required": ["message"],
    },
)

schema_git_branch = FunctionDeclaration(
    name="git_branch",
    description="Manage git branches - list, create, switch, or delete branches",
    parameters={
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["list", "create", "switch", "delete"],
                "description": "Branch operation to perform",
            },
            "branch_name": {
                "type": "string",
                "description": "Branch name (required for create/switch/delete)",
            },
        },
        "required": ["action"],
    },
)

schema_git_remote = FunctionDeclaration(
    name="git_remote",
    description="Manage git remotes - list, add, or remove remote repositories",
    parameters={
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["list", "add", "remove"],
                "description": "Remote operation to perform",
            },
            "remote_name": {
                "type": "string",
                "description": "Remote name (required for add/remove)",
            },
            "url": {"type": "string", "description": "Remote URL (required for add)"},
        },
        "required": ["action"],
    },
)

schema_git_push = FunctionDeclaration(
    name="git_push",
    description="Push local commits to remote repository",
    parameters={
        "type": "object",
        "properties": {
            "remote": {
                "type": "string",
                "description": "Remote name (default: origin)",
            },
            "branch": {
                "type": "string",
                "description": "Branch to push (optional, uses current branch)",
            },
        },
    },
)

schema_git_pull = FunctionDeclaration(
    name="git_pull",
    description="Pull changes from remote repository",
    parameters={
        "type": "object",
        "properties": {
            "remote": {
                "type": "string",
                "description": "Remote name (default: origin)",
            },
            "branch": {
                "type": "string",
                "description": "Branch to pull from (optional, uses current branch)",
            },
        },
    },
)

schema_git_blame = FunctionDeclaration(
    name="git_blame",
    description="Show who last modified each line of a file",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to file to show blame for",
            },
            "line_range": {
                "type": "string",
                "description": "Line range to show (e.g., '10,20')",
            },
        },
        "required": ["file_path"],
    },
)


class GitToolkit(ToolKit):
    """
    Git operations toolkit with comprehensive version control capabilities.
    Provides safe Git operations within a working directory boundary.
    """

    GIT_STATUS = "git_status"
    GIT_LOG = "git_log"
    GIT_DIFF = "git_diff"
    GIT_ADD = "git_add"
    GIT_COMMIT = "git_commit"
    GIT_BRANCH = "git_branch"
    GIT_REMOTE = "git_remote"
    GIT_PUSH = "git_push"
    GIT_PULL = "git_pull"
    GIT_BLAME = "git_blame"

    def __init__(
        self,
        enable_read: bool = True,
        enable_write: bool = False,
        enable_branch: bool = False,
        enable_remote: bool = False,
        enable_history: bool = True,
    ):
        """
        Initialize GitToolkit with capability flags.

        Args:
            enable_read: Allow reading git status, logs, diffs
            enable_write: Allow commits, staging, unstaging
            enable_branch: Allow branch creation, switching, merging
            enable_remote: Allow push, pull, fetch operations
            enable_history: Allow viewing commit history and blame
        """
        super().__init__()
        self.enable_read = enable_read
        self.enable_write = enable_write
        self.enable_branch = enable_branch
        self.enable_remote = enable_remote
        self.enable_history = enable_history
        self._register_functions()

    def _register_functions(self):
        """Register enabled functions with the global registry"""

        if self.enable_read:
            self.schemas.append(schema_git_status)
            ToolKitRegistery.register("git_status", git_status, schema_git_status)

            self.schemas.append(schema_git_diff)
            ToolKitRegistery.register("git_diff", git_diff, schema_git_diff)

        if self.enable_history:
            self.schemas.append(schema_git_log)
            ToolKitRegistery.register("git_log", git_log, schema_git_log)

            self.schemas.append(schema_git_blame)
            ToolKitRegistery.register("git_blame", git_blame, schema_git_blame)

        if self.enable_write:
            self.schemas.append(schema_git_add)
            ToolKitRegistery.register("git_add", git_add, schema_git_add)

            self.schemas.append(schema_git_commit)
            ToolKitRegistery.register("git_commit", git_commit, schema_git_commit)

        if self.enable_branch:
            self.schemas.append(schema_git_branch)
            ToolKitRegistery.register("git_branch", git_branch, schema_git_branch)

        if self.enable_remote:
            self.schemas.append(schema_git_remote)
            ToolKitRegistery.register("git_remote", git_remote, schema_git_remote)

            self.schemas.append(schema_git_push)
            ToolKitRegistery.register("git_push", git_push, schema_git_push)

            self.schemas.append(schema_git_pull)
            ToolKitRegistery.register("git_pull", git_pull, schema_git_pull)

    @property
    def tool(self) -> Tool:
        """Get the Tool instance for this toolkit"""
        return Tool(function_declarations=self.schemas)
