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

from typing import TYPE_CHECKING

from typer.testing import CliRunner

from vera.main import app as main_app

if TYPE_CHECKING:
    import pathlib

runner = CliRunner()


def test_create_plugin(tmp_path: pathlib.Path) -> None:
    result = runner.invoke(
        main_app,
        [
            "create",
            "--name",
            "test_plugin",
            "--description",
            "A test plugin",
            "--dst-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0

    expected_dir = tmp_path / "test_plugin"
    assert expected_dir.exists()
    assert (expected_dir / "pyproject.toml").exists()
    assert (expected_dir / "src" / "test_plugin" / "plugin_impl.py").exists()

    content = (expected_dir / "pyproject.toml").read_text()
    assert "test-plugin" in content
    assert "A test plugin" in content
