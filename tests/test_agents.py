"""Tests for agent implementations."""


import pytest

from runner.agents.base import AgentConfig, AgentResult, AgentType
from runner.agents.openai_agent import OpenAIAgent
from runner.agents.ollama_agent import OllamaAgent


class TestOpenAIAgent:
    """Tests for OpenAI agent."""

    def test_agent_init_valid(self):
        """Test agent initialization with valid config."""
        config = AgentConfig(
            agent_type=AgentType.OPENAI, model="gpt-4", api_key="test-key-123", name="test-agent"
        )

        agent = OpenAIAgent(config)
        assert agent.config == config
        assert agent.config.model == "gpt-4"

    def test_agent_init_missing_api_key(self):
        """Test agent initialization fails without API key."""
        config = AgentConfig(agent_type=AgentType.OPENAI, model="gpt-4", api_key=None)

        with pytest.raises(ValueError):
            OpenAIAgent(config)

    def test_agent_init_wrong_type(self):
        """Test agent initialization fails with wrong type."""
        config = AgentConfig(agent_type=AgentType.OLLAMA, model="codellama", api_key="test-key")

        with pytest.raises(ValueError):
            OpenAIAgent(config)

    def test_system_prompt(self):
        """Test system prompt generation."""
        config = AgentConfig(agent_type=AgentType.OPENAI, model="gpt-4", api_key="test-key")

        agent = OpenAIAgent(config)
        prompt = agent._get_system_prompt()

        assert "software engineer" in prompt.lower()
        assert "run_command" in prompt
        assert "read_file" in prompt
        assert "write_file" in prompt

    def test_tools_schema(self):
        """Test tools schema generation."""
        config = AgentConfig(agent_type=AgentType.OPENAI, model="gpt-4", api_key="test-key")

        agent = OpenAIAgent(config)
        tools = agent._get_tools_schema()

        assert len(tools) == 4
        tool_names = [t["function"]["name"] for t in tools]
        assert "run_command" in tool_names
        assert "read_file" in tool_names
        assert "write_file" in tool_names
        assert "list_files" in tool_names

    def test_cost_calculation(self):
        """Test cost calculation."""
        config = AgentConfig(agent_type=AgentType.OPENAI, model="gpt-4", api_key="test-key")

        agent = OpenAIAgent(config)

        # Mock token usage
        agent.total_input_tokens = 1000
        agent.total_output_tokens = 500

        cost = agent._calculate_cost()

        # GPT-4: input $0.03/1K, output $0.06/1K
        expected = (1000 / 1000 * 0.03) + (500 / 1000 * 0.06)
        assert cost == expected


class TestOllamaAgent:
    """Tests for Ollama agent."""

    def test_agent_init_valid(self):
        """Test agent initialization."""
        config = AgentConfig(agent_type=AgentType.OLLAMA, model="codellama", name="test-ollama")

        agent = OllamaAgent(config)
        assert agent.config == config
        assert agent.ollama_base_url == "http://localhost:11434"

    def test_agent_init_custom_endpoint(self):
        """Test agent with custom endpoint."""
        config = AgentConfig(
            agent_type=AgentType.OLLAMA, model="codellama", api_endpoint="http://remote:11434"
        )

        agent = OllamaAgent(config)
        assert agent.ollama_base_url == "http://remote:11434"

    def test_agent_init_wrong_type(self):
        """Test agent init fails with wrong type."""
        config = AgentConfig(agent_type=AgentType.OPENAI, model="gpt-4", api_key="test")

        with pytest.raises(ValueError):
            OllamaAgent(config)

    def test_system_prompt(self):
        """Test system prompt."""
        config = AgentConfig(agent_type=AgentType.OLLAMA, model="codellama")

        agent = OllamaAgent(config)
        prompt = agent._get_system_prompt()

        assert "software engineer" in prompt.lower()
        assert "JSON" in prompt


class TestAgentResult:
    """Tests for AgentResult."""

    def test_result_creation(self):
        """Test result creation."""
        result = AgentResult(
            task_id="test-task",
            agent_name="test-agent",
            agent_type=AgentType.OPENAI,
            success=True,
            commands_executed=5,
            duration=10.5,
        )

        assert result.task_id == "test-task"
        assert result.success is True
        assert result.commands_executed == 5
        assert result.duration == 10.5

    def test_result_to_dict(self):
        """Test result serialization."""
        result = AgentResult(
            task_id="test-task",
            agent_name="test-agent",
            agent_type=AgentType.OPENAI,
            success=True,
            cost=0.42,
            token_usage=1500,
        )

        data = result.to_dict()

        assert data["task_id"] == "test-task"
        assert data["success"] is True
        assert data["cost"] == 0.42
        assert data["token_usage"] == 1500


class TestAgentConfig:
    """Tests for AgentConfig."""

    def test_config_creation(self):
        """Test config creation."""
        config = AgentConfig(
            agent_type=AgentType.OPENAI,
            model="gpt-4",
            api_key="test-key",
            temperature=0.5,
            max_tokens=2000,
        )

        assert config.agent_type == AgentType.OPENAI
        assert config.temperature == 0.5
        assert config.max_tokens == 2000

    def test_config_defaults(self):
        """Test config defaults."""
        config = AgentConfig(agent_type=AgentType.OLLAMA, model="codellama")

        assert config.temperature == 0.7
        assert config.max_tokens == 4096
        assert config.max_iterations == 10
        assert config.timeout == 300

    def test_config_to_dict(self):
        """Test config serialization."""
        config = AgentConfig(agent_type=AgentType.OPENAI, model="gpt-4", temperature=0.3)

        data = config.to_dict()

        assert data["agent_type"] == "openai"
        assert data["model"] == "gpt-4"
        assert data["temperature"] == 0.3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
