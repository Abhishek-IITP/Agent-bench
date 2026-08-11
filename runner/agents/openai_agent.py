"""
OpenAI agent implementation using GPT models with function calling.

Uses OpenAI's chat completions API with tool use to solve tasks.
Implements retry logic, error handling, and cost tracking.
"""

import asyncio
import json
import time
from typing import Any, Optional

from runner.agents.base import AgentConfig, AgentResult, AgentType, BaseAgent
from runner.docker_client import DockerClient
from runner.logging import get_logger

logger = get_logger(__name__)


class OpenAIAgent(BaseAgent):
    """Agent powered by OpenAI's GPT models."""

    def __init__(self, config: AgentConfig):
        """
        Initialize OpenAI agent.

        Args:
            config: Agent configuration with OpenAI settings
        """
        if config.agent_type != AgentType.OPENAI:
            raise ValueError(f"Expected OpenAI agent type, got {config.agent_type}")

        if not config.api_key:
            raise ValueError("OpenAI API key required")

        super().__init__(config)
        self.logger = logger
        self.client = None  # Lazy-loaded
        self.docker_client = DockerClient()

        # Token and cost tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.estimated_cost = 0.0

        # Model-specific pricing (USD per 1K tokens)
        self.pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        }

    def _get_client(self):
        """Lazily import and initialize OpenAI client."""
        if self.client is None:
            try:
                from openai import AsyncOpenAI

                self.client = AsyncOpenAI(api_key=self.config.api_key)
            except ImportError:
                raise ImportError("OpenAI library required. Install with: pip install openai")

        return self.client

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        return """You are an expert software engineer solving tasks in a Docker container.

You have access to the following tools:
1. run_command(command: str) - Execute a shell command
2. read_file(path: str) - Read file contents
3. write_file(path: str, content: str) - Write to a file
4. list_files(path: str) - List directory contents

Guidelines:
- Always read the task instruction carefully first
- Use run_command to explore the environment
- Create solution files in /workspace/
- Test your solution before declaring completion
- When done, say "TASK_COMPLETE" as your final message

Start by exploring the environment and understanding the requirements."""

    def _get_tools_schema(self) -> list[dict[str, Any]]:
        """Get OpenAI function schema for available tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "run_command",
                    "description": "Execute a shell command in the container",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "Shell command to execute"}
                        },
                        "required": ["command"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to file to read"}
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write content to a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to file to write"},
                            "content": {"type": "string", "description": "Content to write"},
                        },
                        "required": ["path", "content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "List files in a directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Directory path to list"}
                        },
                        "required": ["path"],
                    },
                },
            },
        ]

    async def solve(
        self,
        task_id: str,
        instruction: str,
        environment_files: dict[str, str],
        timeout: Optional[int] = None,
    ) -> AgentResult:
        """
        Solve a task using OpenAI GPT model.

        Args:
            task_id: Task identifier
            instruction: Task instructions
            environment_files: Environment file contents
            timeout: Execution timeout

        Returns:
            AgentResult with execution details
        """
        if timeout is None:
            timeout = self.config.timeout

        start_time = time.time()
        result = self._create_result(task_id)
        trace = result.execution_trace

        try:
            # Create Docker container
            container_id = await self._create_container()
            self.logger.info("Container created", container_id=container_id, task=task_id)

            # Copy environment files
            for filename, content in environment_files.items():
                await self._write_file_in_container(container_id, f"/workspace/{filename}", content)

            # Main solving loop
            messages = [{"role": "user", "content": instruction}]

            iteration = 0
            while iteration < self.config.max_iterations:
                iteration += 1
                elapsed = time.time() - start_time

                if elapsed > timeout:
                    result.error_message = f"Timeout after {timeout}s"
                    break

                # Get response from OpenAI
                self.logger.debug("Calling OpenAI API", iteration=iteration, task=task_id)

                response = await self._call_openai(messages)

                # Track tokens
                if hasattr(response, "usage"):
                    self.total_input_tokens += response.usage.prompt_tokens
                    self.total_output_tokens += response.usage.completion_tokens

                # Process response
                assistant_message = response.choices[0].message

                # Add assistant response to messages
                messages.append({"role": "assistant", "content": assistant_message.content or ""})

                # Check for completion
                if "TASK_COMPLETE" in (assistant_message.content or ""):
                    self.logger.info("Task completed by agent", task=task_id, iterations=iteration)
                    result.success = True
                    break

                # Process tool calls
                if assistant_message.tool_calls:
                    for tool_call in assistant_message.tool_calls:
                        tool_result = await self._execute_tool(
                            container_id,
                            tool_call.function.name,
                            json.loads(tool_call.function.arguments),
                            trace,
                        )

                        # Add tool result to messages
                        messages.append(
                            {
                                "role": "user",
                                "content": json.dumps(
                                    {"tool_call_id": tool_call.id, "result": tool_result}
                                ),
                            }
                        )

                        # Track execution metrics
                        if tool_call.function.name == "run_command":
                            result.commands_executed += 1
                        elif tool_call.function.name == "write_file":
                            result.files_created += 1
                else:
                    # No tool calls and not complete - add agent message to trace
                    self._add_trace_event(
                        trace, "agent_message", assistant_message.content or "No response"
                    )

            # Calculate cost
            result.token_usage = self.total_input_tokens + self.total_output_tokens
            result.cost = self._calculate_cost()
            result.duration = time.time() - start_time

            # Cleanup
            await self._cleanup_container(container_id)

            return result

        except Exception as e:
            self.logger.error("Agent execution failed", task=task_id, error=str(e))
            result.error_message = str(e)
            result.duration = time.time() - start_time
            return result

    async def _call_openai(self, messages: list[dict]) -> Any:
        """Call OpenAI API with retry logic."""
        client = self._get_client()
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = await client.chat.completions.create(
                    model=self.config.model,
                    messages=messages,
                    tools=self._get_tools_schema(),
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )
                return response
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2**attempt
                    self.logger.warning(
                        "OpenAI API error, retrying",
                        attempt=attempt + 1,
                        error=str(e),
                        wait_time=wait_time,
                    )
                    await asyncio.sleep(wait_time)
                else:
                    raise

    async def _execute_tool(
        self,
        container_id: str,
        tool_name: str,
        args: dict[str, Any],
        trace: list[dict[str, Any]],
    ) -> str:
        """Execute a tool and return result."""
        try:
            if tool_name == "run_command":
                command = args.get("command", "")
                self._add_trace_event(trace, "command_start", f"Running: {command}")

                exit_code, stdout, stderr = await self._run_command_in_container(
                    container_id, command
                )

                result = {
                    "exit_code": exit_code,
                    "stdout": stdout[:1000],  # Limit output
                    "stderr": stderr[:500],
                }

                if exit_code != 0:
                    self._add_trace_event(trace, "command_error", f"Command failed: {stderr}")
                else:
                    self._add_trace_event(trace, "command_output", stdout[:500])

                return json.dumps(result)

            elif tool_name == "read_file":
                path = args.get("path", "")
                content = await self._read_file_from_container(container_id, path)
                return json.dumps({"content": content[:2000]})  # Limit output

            elif tool_name == "write_file":
                path = args.get("path", "")
                content = args.get("content", "")
                await self._write_file_in_container(container_id, path, content)
                return json.dumps({"status": "success", "path": path})

            elif tool_name == "list_files":
                path = args.get("path", "/workspace")
                files = await self._list_files_in_container(container_id, path)
                return json.dumps({"files": files})

            else:
                return json.dumps({"error": f"Unknown tool: {tool_name}"})

        except Exception as e:
            self.logger.error("Tool execution failed", tool=tool_name, error=str(e))
            return json.dumps({"error": str(e)})

    async def _create_container(self) -> str:
        """Create a Docker container for task execution."""
        return self.docker_client.create_container(
            image_name=self.config.docker_image,
            memory_limit=self.config.docker_memory,
        )

    async def _cleanup_container(self, container_id: str) -> None:
        """Clean up Docker container."""
        try:
            self.docker_client.remove_container(container_id)
        except Exception as e:
            self.logger.warning("Failed to cleanup container", container=container_id, error=str(e))

    async def _run_command_in_container(
        self,
        container_id: str,
        command: str,
        timeout: int = 30,
    ) -> tuple[int, str, str]:
        """Run a command in the container."""
        exit_code, stdout, stderr = self.docker_client.run_command(
            container_id, command, timeout=timeout
        )
        return exit_code, stdout, stderr

    async def _read_file_from_container(self, container_id: str, path: str) -> str:
        """Read a file from the container."""
        exit_code, stdout, stderr = self.docker_client.run_command(
            container_id, f"cat {path}", timeout=10
        )

        if exit_code != 0:
            raise RuntimeError(f"Failed to read {path}: {stderr}")

        return stdout

    async def _write_file_in_container(
        self,
        container_id: str,
        path: str,
        content: str,
    ) -> None:
        """Write a file in the container."""
        # Use echo with proper escaping
        escaped = content.replace("'", "'\\''")
        command = f"mkdir -p $(dirname {path}) && echo '{escaped}' > {path}"

        exit_code, _, stderr = self.docker_client.run_command(container_id, command, timeout=10)

        if exit_code != 0:
            raise RuntimeError(f"Failed to write {path}: {stderr}")

    async def _list_files_in_container(self, container_id: str, path: str) -> list[str]:
        """List files in a container directory."""
        exit_code, stdout, _ = self.docker_client.run_command(
            container_id, f"ls -la {path} 2>/dev/null || echo 'Directory not found'", timeout=10
        )

        files = []
        for line in stdout.split("\n")[1:]:  # Skip header
            if line.strip():
                parts = line.split()
                if len(parts) >= 9:
                    files.append(parts[-1])

        return files

    def _calculate_cost(self) -> float:
        """Calculate estimated cost of API calls."""
        model_key = self.config.model.lower()

        # Find matching pricing
        pricing = self.pricing.get("gpt-4", self.pricing["gpt-3.5-turbo"])
        for key in self.pricing:
            if key in model_key:
                pricing = self.pricing[key]
                break

        input_cost = (self.total_input_tokens / 1000) * pricing["input"]
        output_cost = (self.total_output_tokens / 1000) * pricing["output"]

        return input_cost + output_cost
