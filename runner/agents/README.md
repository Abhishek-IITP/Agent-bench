# Agent Framework

Complete agent implementation for solving AgentBench tasks using AI models.

## Overview

The agent framework provides an extensible interface for creating agents that solve benchmark tasks using LLMs or other AI models. Agents interact with task environments through Docker containers and record detailed execution traces.

## Quick Start

### Using OpenAI GPT-4

```python
import asyncio
from runner.agents.base import AgentConfig, AgentType
from runner.agents.openai_agent import OpenAIAgent

config = AgentConfig(
    agent_type=AgentType.OPENAI,
    model="gpt-4",
    api_key="sk-...",  # Set via environment variable
    temperature=0.7,
    max_tokens=4096,
    timeout=300
)

agent = OpenAIAgent(config)

result = asyncio.run(agent.solve(
    task_id="find-database-files",
    instruction="Find all database files in the environment",
    environment_files={"app.log": "..."},
))

print(f"Success: {result.success}")
print(f"Duration: {result.duration}s")
print(f"Cost: ${result.cost}")
```

### Using Ollama Locally

```python
config = AgentConfig(
    agent_type=AgentType.OLLAMA,
    model="codellama",
    api_endpoint="http://localhost:11434",
    timeout=300
)

agent = OllamaAgent(config)
result = asyncio.run(agent.solve(
    task_id="find-database-files",
    instruction="Find all database files",
    environment_files={},
))
```

### Via CLI

```bash
# OpenAI
agentbench agent-run find-database-files \
  --agent openai \
  --model gpt-4 \
  --api-key $OPENAI_API_KEY

# Ollama
agentbench agent-run find-database-files \
  --agent ollama \
  --model codellama
```

## Architecture

### BaseAgent (Abstract)

All agents inherit from `BaseAgent` and must implement:

```python
async def solve(
    self,
    task_id: str,
    instruction: str,
    environment_files: dict[str, str],
    timeout: Optional[int] = None,
) -> AgentResult:
    """Solve a task and return results."""
    pass
```

### Agent Types

#### OpenAIAgent

**Best for**: High-quality reasoning, complex tasks, production systems

- **Models**: GPT-4, GPT-4-Turbo, GPT-3.5-Turbo
- **Method**: Function calling with tool use
- **Cost**: ~$0.01-0.06 per 1K tokens
- **Speed**: 2-10 seconds per task

**Features**:
- Tool use pattern (function calling)
- Token tracking and cost calculation
- Automatic retry with backoff
- Error recovery

**Requirements**:
```bash
pip install openai>=1.0
export OPENAI_API_KEY=sk-...
```

#### OllamaAgent

**Best for**: Privacy, cost savings, local development, offline operation

- **Models**: Codellama, Mistral, Neural-Chat, etc.
- **Method**: Local HTTP API
- **Cost**: Free (compute cost only)
- **Speed**: 5-30 seconds per task (model dependent)

**Features**:
- Local execution (no external APIs)
- Model flexibility
- Health check validation
- Graceful degradation

**Requirements**:
```bash
# Install Ollama: https://ollama.ai
ollama pull codellama
ollama serve
```

### AgentConfig

Configuration for any agent:

```python
@dataclass
class AgentConfig:
    agent_type: AgentType          # openai, ollama
    model: str                     # gpt-4, codellama, etc
    name: str = ""                 # Display name
    
    # API Configuration
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    
    # Generation Parameters
    temperature: float = 0.7       # 0.0-1.0 (creativity)
    max_tokens: int = 4096         # Max output
    
    # Execution Parameters
    max_iterations: int = 10       # Max agent steps
    timeout: int = 300             # Seconds
    
    # Docker Configuration
    docker_image: str = "ubuntu:22.04"
    docker_memory: str = "512m"
```

### AgentResult

Results from agent execution:

```python
@dataclass
class AgentResult:
    task_id: str
    agent_name: str
    agent_type: AgentType
    
    # Execution metrics
    success: bool = False
    commands_executed: int = 0
    files_created: int = 0
    files_modified: int = 0
    
    # Resource usage
    token_usage: int = 0
    cost: float = 0.0
    duration: float = 0.0
    
    # Execution trace
    stdout: str = ""
    stderr: str = ""
    error_message: Optional[str] = None
    execution_trace: list[dict] = []
```

## Tool Use

### Available Tools

Agents can use these tools to interact with the task environment:

#### 1. run_command
Execute shell commands in the container.

```python
# Used by agent
"run_command": {"command": "find . -name *.db"}

# Returns
{
    "exit_code": 0,
    "stdout": "file1.db\nfile2.db",
    "stderr": ""
}
```

#### 2. read_file
Read file contents.

```python
"read_file": {"path": "/workspace/config.json"}
```

#### 3. write_file
Write files to the container.

```python
"write_file": {
    "path": "/workspace/solution.py",
    "content": "#!/usr/bin/env python\n..."
}
```

#### 4. list_files
List directory contents.

```python
"list_files": {"path": "/workspace"}
```

### Tool Limitations

- **Output truncation**: Command output limited to 1000 chars (logs), 500 chars (errors)
- **File size**: Large file contents truncated to 2000 chars
- **Command timeout**: 30 seconds per command
- **Total duration**: Configurable per agent/task (default 300s)

## Performance Optimization

### Token Usage Minimization

```python
# Use smaller models for simple tasks
config = AgentConfig(
    agent_type=AgentType.OPENAI,
    model="gpt-3.5-turbo",  # Cheaper, faster
    max_tokens=2048,         # Limit output
)
```

### Cost Tracking

```python
result = asyncio.run(agent.solve(...))

print(f"Tokens: {result.token_usage}")
print(f"Cost: ${result.cost:.4f}")

# Per model pricing:
# GPT-4: $0.03 input, $0.06 output per 1K
# GPT-3.5: $0.0005 input, $0.0015 output per 1K
```

### Execution Optimization

```python
# Parallel task execution
import asyncio

agents = [OpenAIAgent(config) for _ in range(3)]
tasks = [
    agent.solve(task_id, instruction, files)
    for agent in agents
]

results = asyncio.run(asyncio.gather(*tasks))
```

## Error Handling

### Common Issues

**"API key required"**
```bash
export OPENAI_API_KEY=sk-...
# Or pass in config
config.api_key = os.getenv("OPENAI_API_KEY")
```

**"Cannot connect to Ollama"**
```bash
# Make sure Ollama is running
ollama serve

# Or specify custom endpoint
config.api_endpoint = "http://remote-machine:11434"
```

**"Container creation failed"**
- Ensure Docker daemon is running
- Check memory: `docker system df`
- Verify base image: `docker images | grep ubuntu`

**"Execution timeout"**
```python
# Increase timeout
config.timeout = 600  # 10 minutes

# Or try simpler tasks first
```

## Extending with Custom Agents

Create a custom agent by inheriting from `BaseAgent`:

```python
from runner.agents.base import BaseAgent, AgentConfig, AgentResult

class CustomAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        # Initialize your agent
    
    async def solve(
        self,
        task_id: str,
        instruction: str,
        environment_files: dict[str, str],
        timeout: Optional[int] = None,
    ) -> AgentResult:
        """Implement your solving logic."""
        result = self._create_result(task_id)
        
        try:
            # Your implementation
            container = await self._create_container()
            # ... solve task ...
            result.success = True
        except Exception as e:
            result.error_message = str(e)
        finally:
            await self._cleanup_container(container)
        
        return result
```

Register your agent:

```python
# In CLI
if agent_type == "custom":
    agent = CustomAgent(config)
```

## Testing

Run agent tests:

```bash
pytest tests/test_agents.py -v
```

Test a specific agent:

```python
def test_agent_solves_task():
    config = AgentConfig(
        agent_type=AgentType.OPENAI,
        model="gpt-4",
        api_key="test-key"
    )
    agent = OpenAIAgent(config)
    
    result = asyncio.run(agent.solve(
        task_id="test",
        instruction="Test",
        environment_files={},
        timeout=10
    ))
    
    assert result is not None
```

## Integration with Replay System

Agents automatically record execution traces:

```python
from runner.replay import ReplayStorage

result = asyncio.run(agent.solve(...))

# Access execution trace
for event in result.execution_trace:
    print(f"{event['timestamp']}: {event['type']}")

# Store trace
storage = ReplayStorage()
storage.save_trace(result.execution_trace, run_id)
```

## Integration with Storage

Store agent results:

```python
from runner.storage import Storage

storage = Storage()

# Store task
storage.store_task(task_config)

# Start run
run_id = storage.start_run(task_id, agent_id)

# Store result
storage.store_result(run_id, evaluation_result)

# Store metrics
storage.store_execution_metrics(
    run_id=run_id,
    commands_executed=result.commands_executed,
    files_created=result.files_created,
    tokens_used=result.token_usage,
    cost=result.cost
)
```

## Troubleshooting

### Debug Logging

Enable debug logging to see detailed agent behavior:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

result = asyncio.run(agent.solve(...))
# Detailed logs will show:
# - API calls
# - Tool execution
# - Container operations
# - Token usage
```

### Inspect Execution Trace

```python
result = asyncio.run(agent.solve(...))

for event in result.execution_trace:
    print(f"[{event['timestamp']}] {event['type']}: {event['content'][:100]}")
```

### Replay Execution

```bash
# Show full replay trace
agentbench replay run-uuid-123
```

## Performance Benchmarks

### OpenAI GPT-4
- Task solve time: 5-15 seconds
- Cost per task: $0.02-0.10
- Success rate: 85-95%

### Ollama Codellama
- Task solve time: 10-30 seconds
- Cost per task: $0.00 (compute only)
- Success rate: 60-80%

### Local GPU (optional)
```bash
# With GPU acceleration
ollama pull codellama
CUDA_VISIBLE_DEVICES=0 ollama serve
```

## Best Practices

1. **Use appropriate models**
   - Simple tasks → GPT-3.5
   - Complex tasks → GPT-4
   - Local/offline → Ollama

2. **Optimize token usage**
   - Reduce max_tokens for simple tasks
   - Use temperature appropriately
   - Monitor costs regularly

3. **Error handling**
   - Implement retry logic
   - Log all failures
   - Use timeouts appropriately

4. **Container management**
   - Always cleanup containers
   - Monitor Docker resources
   - Use resource limits

## References

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Execution Replay System](../replay.md)
- [Storage Layer](../storage.md)
- [REST API](../../docs/api.md)

## Support

For issues or questions:
1. Check test cases in `tests/test_agents.py`
2. Review logs with `DEBUG` level
3. Inspect replay traces
4. Check Agent Framework documentation above
