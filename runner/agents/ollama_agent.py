"""
Ollama agent implementation for local LLM inference.

Uses local Ollama instance for task solving without external API calls.
Implements streaming responses and tool parsing.
"""

import json
import time
from typing import Any, Optional

import httpx

from runner.agents.base import AgentConfig, AgentResult, AgentType, BaseAgent
from runner.docker_client import DockerClient
from runner.logging import get_logger

logger = get_logger(__name__)


class OllamaAgent(BaseAgent):
    """Agent powered by local Ollama models."""

    def __init__(self, config: AgentConfig):
        """
        Initialize Ollama agent.

        Args:
            config: Agent configuration with Ollama settings
        """
        if config.agent_type != AgentType.OLLAMA:
            raise ValueError(f"Expected Ollama agent type, got {config.agent_type}")

        super().__init__(config)
        self.logger = logger
        self.docker_client = DockerClient()

        # Ollama settings
        self.ollama_base_url = config.api_endpoint or "http://localhost:11434"
        self.timeout = 60

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        return """You are an expert software engineer solving tasks in a Docker container.

You have access to the following tools through function calls:
1. run_command - Execute a shell command
2. read_file - Read file contents
3. write_file - Write to a file
4. list_files - List directory contents

When you need to use a tool, respond with JSON in this format:
{"tool": "tool_name", "args": {"param": "value"}}

Guidelines:
- Always read the task instruction carefully first
- Use run_command to explore the environment
- Create solution files in /workspace/
- Test your solution before declaring completion
- When done, respond with: {"status": "TASK_COMPLETE"}

Start by exploring the environment and understanding the requirements."""

    async def solve(
        self,
        task_id: str,
        instruction: str,
        environment_files: dict[str, str],
        timeout: Optional[int] = None,
    ) -> AgentResult:
        """
        Solve a task using local Ollama model.

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
            # Check Ollama connectivity
            await self._check_ollama_health()

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

                # Get response from Ollama
                self.logger.debug("Calling Ollama API", iteration=iteration, task=task_id)

                response = await self._call_ollama(messages)

                # Process response
                full_response = response.strip()

                # Check for completion
                if "TASK_COMPLETE" in full_response or '"status": "TASK_COMPLETE"' in full_response:
                    self.logger.info("Task completed by agent", task=task_id, iterations=iteration)
                    result.success = True
                    break

                # Try to parse tool call
                tool_call_result = await self._parse_and_execute_tool(
                    container_id, full_response, trace
                )

                # Add assistant response and tool result to messages
                messages.append({"role": "assistant", "content": full_response})

                if tool_call_result:
                    messages.append(
                        {"role": "user", "content": f"Tool result: {json.dumps(tool_call_result)}"}
                    )

                    # Track execution metrics
                    if isinstance(tool_call_result, dict) and "tool" in tool_call_result:
                        if tool_call_result["tool"] == "run_command":
                            result.commands_executed += 1
                        elif tool_call_result["tool"] == "write_file":
                            result.files_created += 1
                else:
                    # Add agent message to trace
                    self._add_trace_event(trace, "agent_message", full_response)

            # Calculate duration
            result.duration = time.time() - start_time

            # Cleanup
            await self._cleanup_container(container_id)

            return result

        except Exception as e:
            self.logger.error("Agent execution failed", task=task_id, error=str(e))
            result.error_message = str(e)
            result.duration = time.time() - start_time
            return result

    async def _check_ollama_health(self) -> None:
        """Check if Ollama is running and model is available."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.ollama_base_url}/api/tags")

                if response.status_code != 200:
                    raise RuntimeError(f"Ollama health check failed: {response.status_code}")

                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]

                if not any(self.config.model in name for name in model_names):
                    self.logger.warning(
                        "Model not found, available models",
                        requested=self.config.model,
                        available=model_names,
                    )

        except Exception as e:
            raise RuntimeError(f"Cannot connect to Ollama at {self.ollama_base_url}: {e}")

    async def _call_ollama(self, messages: list[dict]) -> str:
        """Call Ollama API and get response."""
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            "temperature": self.config.temperature,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.ollama_base_url}/api/chat", json=payload)

                if response.status_code != 200:
                    raise RuntimeError(f"Ollama API error: {response.status_code}")

                result = response.json()
                return result.get("message", {}).get("content", "")

        except Exception as e:
            self.logger.error("Ollama API call failed", error=str(e))
            raise

    async def _parse_and_execute_tool(
        self,
        container_id: str,
        response: str,
        trace: list[dict[str, Any]],
    ) -> Optional[dict[str, Any]]:
        """Parse response for tool calls and execute them."""
        try:
            # Try to extract JSON tool call
            start_idx = response.find("{")
            end_idx = response.rfind("}") + 1

            if start_idx == -1 or end_idx == 0:
                return None

            tool_json = response[start_idx:end_idx]
            tool_call = json.loads(tool_json)

            tool_name = tool_call.get("tool")
            args = tool_call.get("args", {})

            if not tool_name:
                return None

            return await self._execute_tool(container_id, tool_name, args, trace)

        except (json.JSONDecodeError, ValueError):
            return None

    async def _execute_tool(
        self,
        container_id: str,
        tool_name: str,
        args: dict[str, Any],
        trace: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Execute a tool and return result."""
        try:
            if tool_name == "run_command":
                command = args.get("command", "")
                self._add_trace_event(trace, "command_start", f"Running: {command}")

                exit_code, stdout, stderr = await self._run_command_in_container(
                    container_id, command
                )

                result = {
                    "tool": "run_command",
                    "exit_code": exit_code,
                    "stdout": stdout[:1000],
                    "stderr": stderr[:500],
                }

                if exit_code != 0:
                    self._add_trace_event(trace, "command_error", f"Command failed: {stderr}")
                else:
                    self._add_trace_event(trace, "command_output", stdout[:500])

                return result

            elif tool_name == "read_file":
                path = args.get("path", "")
                content = await self._read_file_from_container(container_id, path)
                return {"tool": "read_file", "content": content[:2000]}

            elif tool_name == "write_file":
                path = args.get("path", "")
                content = args.get("content", "")
                await self._write_file_in_container(container_id, path, content)
                return {"tool": "write_file", "status": "success", "path": path}

            elif tool_name == "list_files":
                path = args.get("path", "/workspace")
                files = await self._list_files_in_container(container_id, path)
                return {"tool": "list_files", "files": files}

            else:
                return {"error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            self.logger.error("Tool execution failed", tool=tool_name, error=str(e))
            return {"tool": tool_name, "error": str(e)}

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
        for line in stdout.split("\n")[1:]:
            if line.strip():
                parts = line.split()
                if len(parts) >= 9:
                    files.append(parts[-1])

        return files
