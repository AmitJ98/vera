# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from typer.testing import CliRunner

from vera.main import app
from vera.project_name import PROJECT_NAME

runner = CliRunner()


def test_test_unknown_option() -> None:
    with patch(f"{PROJECT_NAME}.core.plugin_service.create_service") as mock_create:
        mock_pc = MagicMock()
        mock_pc.registered_plugin_names = ["some_plugin"]
        mock_pc.plugin_service.display_test_command_help.return_value = [None]
        mock_create.return_value = mock_pc

        with (
            patch(
                f"{PROJECT_NAME}.vtest._get_filtered_test_cases",
                return_value=[MagicMock()],
            ),
            patch(f"{PROJECT_NAME}.vtest.Progress"),
        ):
            result = runner.invoke(app, ["test", "--unknown-opt"])
            assert result.exit_code == 1
            assert "Unknown options: ['--unknown-opt']" in result.output


def test_config_unknown_option() -> None:
    with patch(f"{PROJECT_NAME}.core.plugin_service.create_service") as mock_create:
        mock_pc = MagicMock()
        mock_pc.plugin_service.display_config_command_help.return_value = [None]
        mock_create.return_value = mock_pc

        result = runner.invoke(app, ["config", "--unknown-opt"])
        assert result.exit_code == 1
        assert "Unknown options: ['--unknown-opt']" in result.output


def test_test_help_plugin_signal() -> None:
    with patch(f"{PROJECT_NAME}.core.plugin_service.create_service") as mock_create:
        mock_pc = MagicMock()
        mock_pc.registered_plugin_names = ["some_plugin"]
        # Plugin signals help was displayed
        mock_pc.plugin_service.display_test_command_help.return_value = [True]
        mock_create.return_value = mock_pc

        result = runner.invoke(app, ["test", "--any-arg"])
        assert result.exit_code == 0  # Should exit gracefully


def test_test_plugin_consumes_arg() -> None:
    with patch(f"{PROJECT_NAME}.core.plugin_service.create_service") as mock_create:
        mock_pc = MagicMock()
        mock_pc.registered_plugin_names = ["some_plugin"]
        mock_pc.plugin_service.display_test_command_help.return_value = [False]

        def mock_handle(extra_args: list[str]) -> None:
            if "--plugin-opt" in extra_args:
                extra_args.remove("--plugin-opt")

        mock_pc.plugin_service.handle_test_command_extra_args.side_effect = mock_handle
        mock_create.return_value = mock_pc

        with (
            patch(
                f"{PROJECT_NAME}.vtest._get_filtered_test_cases",
                return_value=[MagicMock()],
            ),
            patch(f"{PROJECT_NAME}.vtest.Progress"),
            patch(
                f"{PROJECT_NAME}.vtest.TestingService.run_tests",
                new_callable=AsyncMock,
            ),
        ):
            result = runner.invoke(app, ["test", "--plugin-opt"])
            assert result.exit_code == 0
