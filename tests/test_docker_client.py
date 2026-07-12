"""
Tests for Docker client module.

Note: These tests require Docker to be installed and running.
Skipped if Docker is not available.
"""

import pytest

from runner.docker_client import DockerClient


class TestDockerClient:
    """Test suite for DockerClient."""

    @pytest.fixture
    def docker_client(self):
        """Create a Docker client instance."""
        try:
            return DockerClient()
        except Exception as e:
            pytest.skip(f"Docker not available: {e}")

    def test_docker_client_init(self, docker_client):
        """Test DockerClient initialization."""
        assert docker_client is not None
        assert docker_client.client is not None

    def test_dockerfile_exists(self):
        """Test that Dockerfile exists in project root."""
        from pathlib import Path

        dockerfile = Path("Dockerfile")
        assert dockerfile.exists(), "Dockerfile not found in project root"

    def test_dockerfile_content(self):
        """Test that Dockerfile has basic content."""
        from pathlib import Path

        dockerfile = Path("Dockerfile")
        content = dockerfile.read_text()

        assert "FROM ubuntu:22.04" in content
        assert "WORKDIR /workspace" in content
        assert "bash" in content.lower()
