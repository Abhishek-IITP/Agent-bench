"""
Docker client for task execution.

Provides a wrapper around the Docker SDK for building images, creating containers,
and running commands inside containers.
"""

import io
import tarfile
from pathlib import Path
from typing import Optional

import docker

from runner.logging import get_logger

logger = get_logger(__name__)


class DockerClient:
    """Docker client for task execution."""

    def __init__(self):
        """Initialize Docker client."""
        try:
            self.client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.error("Failed to initialize Docker client", error=str(e))
            raise

    def build_image(self, dockerfile_path: str, image_name: str, tag: str = "latest") -> str:
        """
        Build a Docker image from a Dockerfile.

        Args:
            dockerfile_path: Path to Dockerfile
            image_name: Name for the image (e.g., 'agentbench-base')
            tag: Tag for the image

        Returns:
            Image ID of the built image
        """
        dockerfile_path = Path(dockerfile_path)
        build_context = dockerfile_path.parent

        logger.info("Building Docker image", dockerfile=dockerfile_path, image=image_name, tag=tag)

        try:
            image, build_logs = self.client.images.build(
                dockerfile=dockerfile_path.name,
                path=str(build_context),
                tag=f"{image_name}:{tag}",
                rm=True,
            )

            # Log build output
            for log_entry in build_logs:
                if "stream" in log_entry:
                    logger.debug("Build log", message=log_entry["stream"].strip())

            logger.info("Image built successfully", image_id=image.id, image=image_name)
            return image.id

        except Exception as e:
            logger.error("Failed to build Docker image", error=str(e))
            raise

    def create_container(
        self,
        image_name: str,
        volumes: Optional[dict] = None,
        working_dir: str = "/workspace",
        memory_limit: str = "512m",
    ) -> str:
        """
        Create a Docker container.

        Args:
            image_name: Name of the image (with tag, e.g. 'agentbench-base:latest')
            volumes: Volume mounts (dict of host_path -> container_path)
            working_dir: Working directory in container
            memory_limit: Memory limit (e.g., '512m', '1g')

        Returns:
            Container ID
        """
        logger.info("Creating Docker container", image=image_name, volumes=volumes)

        try:
            container = self.client.containers.create(
                image_name,
                volumes=volumes,
                working_dir=working_dir,
                mem_limit=memory_limit,
                stdin_open=True,
                tty=True,
            )
            container.start()

            logger.info("Container created and started", container_id=container.id)
            return container.id

        except Exception as e:
            logger.error("Failed to create container", error=str(e))
            raise

    def run_command(
        self,
        container_id: str,
        command: str,
        timeout: Optional[int] = 60,
    ) -> tuple[int, str, str]:
        """
        Run a command inside a container.

        Args:
            container_id: Container ID
            command: Command to execute
            timeout: Timeout in seconds

        Returns:
            (exit_code, stdout, stderr)
        """
        logger.info("Running command in container", container=container_id, command=command)

        try:
            container = self.client.containers.get(container_id)

            result = container.exec_run(
                command,
                stdout=True,
                stderr=True,
                workdir="/workspace",
            )

            exit_code = result.exit_code
            stdout = result.output.decode("utf-8", errors="ignore") if result.output else ""
            stderr = ""

            logger.info("Command executed", container=container_id, exit_code=exit_code)

            return exit_code, stdout, stderr

        except Exception as e:
            logger.error("Failed to run command", container=container_id, error=str(e))
            return 1, "", str(e)

    def copy_to_container(
        self,
        container_id: str,
        local_path: Path,
        container_path: str,
    ) -> None:
        """
        Copy files from host to container.

        Args:
            container_id: Container ID
            local_path: Local file or directory path
            container_path: Path inside container
        """
        logger.info(
            "Copying to container",
            container=container_id,
            local=local_path,
            remote=container_path,
        )

        try:
            container = self.client.containers.get(container_id)
            local_path = Path(local_path)

            if not local_path.exists():
                raise FileNotFoundError(f"Path not found: {local_path}")

            # Create tar archive of the file/directory
            tar_buffer = io.BytesIO()
            with tarfile.open(fileobj=tar_buffer, mode="w") as tar:
                if local_path.is_file():
                    tar.add(local_path, arcname=local_path.name)
                else:
                    tar.add(local_path, arcname=local_path.name)

            tar_buffer.seek(0)
            container.put_archive(container_path, tar_buffer)

            logger.info("Files copied to container", container=container_id)

        except Exception as e:
            logger.error("Failed to copy to container", error=str(e))
            raise

    def copy_from_container(
        self,
        container_id: str,
        container_path: str,
        local_path: Path,
    ) -> None:
        """
        Copy files from container to host.

        Args:
            container_id: Container ID
            container_path: Path inside container
            local_path: Local destination path
        """
        logger.info(
            "Copying from container",
            container=container_id,
            remote=container_path,
            local=local_path,
        )

        try:
            container = self.client.containers.get(container_id)
            local_path = Path(local_path)
            local_path.parent.mkdir(parents=True, exist_ok=True)

            # Check if path exists in container first
            exit_code, _, _ = self.run_command(container_id, f"test -e {container_path}", timeout=5)
            if exit_code != 0:
                logger.warning(
                    "Container path does not exist",
                    container=container_id,
                    path=container_path,
                )
                return

            tar_data, _ = container.get_archive(container_path)

            with tarfile.open(fileobj=tar_data, mode="r|*") as tar:
                tar.extractall(path=local_path.parent)

            logger.info("Files copied from container", container=container_id)

        except Exception as e:
            logger.error("Failed to copy from container", error=str(e))
            # Don't raise - log and continue, as files may not exist

    def remove_container(self, container_id: str, force: bool = True) -> None:
        """
        Remove a container.

        Args:
            container_id: Container ID
            force: Force removal even if running
        """
        logger.info("Removing container", container=container_id)

        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)
            logger.info("Container removed", container=container_id)

        except Exception as e:
            logger.error("Failed to remove container", error=str(e))
            # Don't raise - just log the error

    def container_exists(self, container_id: str) -> bool:
        """
        Check if a container exists.

        Args:
            container_id: Container ID

        Returns:
            True if container exists
        """
        try:
            self.client.containers.get(container_id)
            return True
        except Exception:
            return False

    def get_container_logs(self, container_id: str, tail: int = 100) -> str:
        """
        Get container logs.

        Args:
            container_id: Container ID
            tail: Number of lines to retrieve

        Returns:
            Container logs as string
        """
        logger.info("Retrieving container logs", container=container_id)

        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=tail).decode("utf-8", errors="ignore")
            return logs

        except Exception as e:
            logger.error("Failed to retrieve logs", error=str(e))
            return ""
