"""Tests for command executor interface."""

import subprocess
from unittest.mock import Mock, patch

import pytest

from dock.adapters import CommandExecutor, SubprocessExecutor


class TestSubprocessExecutor:
    """Tests for SubprocessExecutor implementation."""

    def test_execute_successful_command(self) -> None:
        """Test executing a successful command returns stdout."""
        executor = SubprocessExecutor()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout="command output\n",
                stderr="",
                returncode=0
            )

            result = executor.execute(["echo", "test"])

            assert result == "command output\n"
            mock_run.assert_called_once_with(
                ["echo", "test"],
                capture_output=True,
                text=True,
                check=True
            )

    def test_execute_command_with_output_capture(self) -> None:
        """Test that command output is properly captured."""
        executor = SubprocessExecutor()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout="line1\nline2\nline3\n",
                stderr="",
                returncode=0
            )

            result = executor.execute(["ls", "-la"])

            assert result == "line1\nline2\nline3\n"
            assert mock_run.call_count == 1

    def test_execute_command_with_error_raises_exception(self) -> None:
        """Test that command errors raise CalledProcessError."""
        executor = SubprocessExecutor()

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                returncode=1,
                cmd=["false"],
                output="",
                stderr="command failed"
            )

            with pytest.raises(subprocess.CalledProcessError) as exc_info:
                executor.execute(["false"])

            assert exc_info.value.returncode == 1

    def test_execute_command_without_check(self) -> None:
        """Test executing command without check flag doesn't raise on error."""
        executor = SubprocessExecutor()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout="",
                stderr="error message",
                returncode=1
            )

            result = executor.execute(["false"], check=False)

            assert result == ""
            mock_run.assert_called_once_with(
                ["false"],
                capture_output=True,
                text=True,
                check=False
            )

    def test_execute_handles_empty_output(self) -> None:
        """Test executing command with no output."""
        executor = SubprocessExecutor()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout="",
                stderr="",
                returncode=0
            )

            result = executor.execute(["true"])

            assert result == ""

    def test_command_executor_is_abstract(self) -> None:
        """Test that CommandExecutor cannot be instantiated directly."""
        with pytest.raises(TypeError):
            CommandExecutor()  # type: ignore
