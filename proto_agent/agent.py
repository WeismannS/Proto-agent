from typing import List
from litellm import completion
import json

from .Config import SYSTEM_PROMPT
from .agent_settings import AgentConfig
from .tool_kit_registry import ToolKitRegistery
from .types_llm import (
    Content,
    Part,
    FunctionCall,
    GenerateContentResponse,
    UsageMetadata,
)


def _create_error_response(function_name: str, error: str):
    return Content(
        role="tool",
        parts=[
            Part.from_function_response(
                name=function_name,
                response={"error": error},
            )
        ],
    )


def _get_user_confirmation(file_path: str, args: dict) -> bool:
    """Get user confirmation for file execution."""
    args_display = {k: v for k, v in args.items() if k != "file_path"}
    choice = input(
        f"Allow execution of '{file_path}' with args {args_display}? (y/N): "
    ).lower()
    return choice in ("y", "yes")


class Agent:
    def __init__(self, settings: AgentConfig):
        self.settings = settings
        self._last_tool_call_ids = []

        self._litellm_tools = None
        if self.settings.tools:
            self._litellm_tools = self._convert_tools_to_litellm(self.settings.tools)

        self._litellm_messages = []

        if SYSTEM_PROMPT:
            self._litellm_messages.append({"role": "system", "content": SYSTEM_PROMPT})

    def _convert_content_to_litellm_message(self, content: Content) -> List[dict]:
        """Convert a single Content message to LiteLLM format"""
        messages = []

        if content.role == "user":
            content_parts = []
            for part in content.parts:
                if part.text:
                    content_parts.append(part.text)

            if content_parts:
                messages.append({"role": "user", "content": " ".join(content_parts)})

        elif content.role == "assistant":
            has_function_calls = any(part.function_call for part in content.parts)
            text_parts = [part.text for part in content.parts if part.text]

            if has_function_calls:
                tool_calls = []
                for i, part in enumerate(content.parts):
                    if part.function_call:
                        tool_call_id = self._last_tool_call_ids[i]
                        tool_calls.append(
                            {
                                "id": tool_call_id,
                                "type": "function",
                                "function": {
                                    "name": part.function_call.name,
                                    "arguments": json.dumps(
                                        part.function_call.arguments or {}
                                    ),
                                },
                            }
                        )

                message = {
                    "role": "assistant",
                    "content": " ".join(text_parts) if text_parts else None,
                    "tool_calls": tool_calls,
                }
                messages.append(message)
            elif text_parts:
                messages.append({"role": "assistant", "content": " ".join(text_parts)})

        elif content.role == "tool":
            # Convert tool responses and use the stored tool call IDs
            for i, part in enumerate(content.parts):
                if part.function_response:
                    tool_call_id = self._last_tool_call_ids[i]
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": json.dumps(part.function_response.response),
                        }
                    )

        return messages

    def _convert_tools_to_litellm(self, tools):
        """Convert our tool format to LiteLLM tools format"""
        litellm_tools = []

        for tool in tools:
            for func_decl in tool.function_declarations:
                litellm_tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": func_decl.name,
                            "description": func_decl.description,
                            "parameters": func_decl.parameters,
                        },
                    }
                )

        return litellm_tools

    def call_function(
        self, function_call_part: FunctionCall, verbose=False, allow_exec=False
    ):
        if function_call_part.name is None:
            return _create_error_response(
                "Invalid function", f"Unknown function: {function_call_part.name}"
            )
        function_to_run = ToolKitRegistery.get_function(function_call_part.name)
        if function_to_run is None:
            return _create_error_response(
                "Invalid function", f"Unknown function: {function_call_part.name}"
            )
        if verbose:
            print(
                f"Calling function: {function_call_part.name}({function_call_part.args})"
            )
        else:
            print(f" - Calling function: {function_call_part.name}")
        if function_to_run.__name__ == "run_python_file" and not allow_exec:
            function_arguments = (
                function_call_part.args if function_call_part.args else {}
            )
            file_path = function_arguments.get("file_path", "")

            if not _get_user_confirmation(file_path, function_arguments):
                return _create_error_response(
                    function_call_part.name, f"Refused to run {function_call_part.name}"
                )
        args_dict = (function_call_part.args) if function_call_part.args else {}
        res = function_to_run(
            working_directory=self.settings.working_directory, **args_dict
        )
        return Content(
            role="tool",
            parts=[
                Part.from_function_response(
                    name=function_call_part.name,
                    response={"result": res},
                )
            ],
        )

    def generate_content(
        self,
        prompt: str | None = None,
        messages: List[Content] | None = None,
    ) -> GenerateContentResponse:
        if messages is None:
            if prompt is None:
                raise ValueError("Either prompt or messages must be provided")
            messages = [Content(role="user", parts=[Part(text=prompt)])]

        for message in messages:
            new_litellm_messages = self._convert_content_to_litellm_message(message)
            self._litellm_messages.extend(new_litellm_messages)

        working_messages = messages.copy()
        iterations = 0

        while iterations < self.settings.max_iterations:
            try:
                response = completion(
                    api_key=self.settings.api_key,
                    model=self.settings.model,
                    messages=self._litellm_messages,
                    tools=self._litellm_tools,
                    temperature=1.0,
                )
                choices = getattr(response, "choices", [])
                if not choices:
                    raise Exception("No choices returned from LiteLLM")

                message = getattr(choices[0], "message", None)
                if not message:
                    raise Exception("No message in response choice")

                response_text = getattr(message, "content", "")

                # Check for tool calls
                tool_calls = getattr(message, "tool_calls", None)
                if not tool_calls:
                    # Create usage metadata
                    usage_metadata = None
                    usage = getattr(response, "usage", None)
                    if usage:
                        usage_metadata = UsageMetadata(
                            prompt_token_count=getattr(usage, "prompt_tokens", 0),
                            candidates_token_count=getattr(
                                usage, "completion_tokens", 0
                            ),
                            total_token_count=getattr(usage, "total_tokens", 0),
                        )

                    return GenerateContentResponse(
                        text=response_text,
                        function_calls=[],
                        usage_metadata=usage_metadata,
                    )
                function_calls = []
                function_call_parts = []
                self._last_tool_call_ids = []

                for i, tool_call in enumerate(tool_calls):
                    func_obj = getattr(tool_call, "function", None)
                    if not func_obj:
                        continue

                    func_name = getattr(func_obj, "name", "") or ""
                    func_args = getattr(func_obj, "arguments", "{}") or "{}"
                    tool_call_id = getattr(tool_call, "id", f"call_{i}")

                    self._last_tool_call_ids.append(tool_call_id)

                    function_call = FunctionCall(
                        name=func_name,
                        arguments=json.loads(func_args) if func_args else {},
                    )
                    function_calls.append(function_call)

                    if self.settings.verbose:
                        print(
                            f"Calling function: {function_call.name}({function_call.args})"
                        )

                    function_call_parts.append(
                        Part.from_function_call(
                            name=function_call.name, args=function_call.args or {}
                        )
                    )

                assistant_parts = []
                if response_text:
                    assistant_parts.append(Part(text=response_text))
                assistant_parts.extend(function_call_parts)

                assistant_content = Content(role="assistant", parts=assistant_parts)
                working_messages.append(assistant_content)

                assistant_litellm_messages = self._convert_content_to_litellm_message(
                    assistant_content
                )
                self._litellm_messages.extend(assistant_litellm_messages)

                function_response_parts = []
                for function_call in function_calls:
                    function_res = self.call_function(
                        function_call, self.settings.verbose, self.settings.allow_exec
                    )

                    if (
                        function_res.parts is None
                        or not function_res.parts
                        or function_res.parts[0].function_response is None
                    ):
                        raise Exception(
                            f"Function {function_call.name} returned no response"
                        )

                    if (
                        self.settings.verbose
                        and function_res.parts[0].function_response
                        and function_res.parts[0].function_response.response
                    ):
                        print(f"-> {function_res.parts[0].function_response.response}")
                    function_response_parts.extend(function_res.parts)

                tool_content = Content(role="tool", parts=function_response_parts)
                working_messages.append(tool_content)

                tool_litellm_messages = self._convert_content_to_litellm_message(
                    tool_content
                )
                self._litellm_messages.extend(tool_litellm_messages)

                iterations += 1

            except Exception as e:
                raise Exception(f"Error in LiteLLM completion: {str(e)}")

        raise Exception(
            f"Maximum function call iterations ({self.settings.max_iterations}) exceeded"
        )
