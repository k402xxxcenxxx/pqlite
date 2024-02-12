from unittest.mock import patch
import pytest
from click.testing import CliRunner
from pqlite.cli import main


@pytest.fixture
def runner():
    return CliRunner()


@patch("pqlite.server.DistributedDatabaseServer.start")
def test_cli_default_with_mocked_loop(mock_start, runner):
    result = runner.invoke(main, ["server"])
    assert result.exit_code == 0
    mock_start.assert_called_once()


@patch("pqlite.server.DistributedDatabaseServer.start")
def test_cli_with_mocked_loop(mock_start, runner):
    result = runner.invoke(
        main, ["server", "--host", "localhost", "--port", "5000"]
    )
    assert result.exit_code == 0
    mock_start.assert_called_once()


def test_cli_with_keyboard_interrupt(runner, capfd):
    with patch("socket.socket.accept", side_effect=KeyboardInterrupt):
        result = runner.invoke(
            main, ["server", "--host", "localhost", "--port", "5000"]
        )
        assert (
            result.exit_code == 0
        ), "CLI should handle KeyboardInterrupt gracefully"
        assert (
            "Server shutting down." in result.output
        ), "CLI should show exiting message: Server shutting down."
