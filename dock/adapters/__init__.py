"""Command execution abstractions for dock tool."""

import subprocess
from abc import ABC, abstractmethod


class CommandExecutor(ABC):
    """Abstract interface for executing system commands."""

    @abstractmethod
    def execute(self, command: list[str], check: bool = True) -> str:
        """
        Execute command and return stdout.

        Args:
            command: List of command arguments
            check: If True, raise CalledProcessError on non-zero exit

        Returns:
            Command stdout as string

        Raises:
            CalledProcessError: If check=True and command fails
        """
        pass


class SubprocessExecutor(CommandExecutor):
    """Real command executor using subprocess."""

    def execute(self, command: list[str], check: bool = True) -> str:
        """
        Execute command using subprocess.

        Args:
            command: List of command arguments
            check: If True, raise CalledProcessError on non-zero exit

        Returns:
            Command stdout as string

        Raises:
            CalledProcessError: If check=True and command fails
        """
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout
