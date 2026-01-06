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

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from vera import PROJECT_NAME
from vera.main import app


class TestCli:
    runner = CliRunner()

    def test_list_plugins(self) -> None:
        with patch("vera.core.plugin_service.create_service") as mock_create:
            mock_pc = MagicMock()
            mock_pc.registered_plugin_names = [
                "sql_query_assistant",
                f"{PROJECT_NAME}.core.default_impl",
            ]
            mock_create.return_value = mock_pc

            result = self.runner.invoke(app, ["list"])
            assert result.exit_code == 0
            assert "sql_query_assistant" in result.output

    def test_list_plugins_none(self) -> None:
        with patch(f"{PROJECT_NAME}.core.plugin_service.create_service") as mock_create:
            mock_pc = MagicMock()
            mock_pc.registered_plugin_names = [f"{PROJECT_NAME}.core.default_impl"]
            mock_create.return_value = mock_pc

            result = self.runner.invoke(app, ["list"])
            assert result.exit_code == 0
            assert "No registered plugins found" in result.output

    def test_test_command_no_plugins(self) -> None:
        with patch(f"{PROJECT_NAME}.core.plugin_service.create_service") as mock_create:
            mock_pc = MagicMock()
            mock_pc.registered_plugin_names = []
            mock_create.return_value = mock_pc

            result = self.runner.invoke(app, ["test"])
            assert result.exit_code == 1
            assert "No plugins found" in result.output
