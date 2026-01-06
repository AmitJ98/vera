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

import json
from typing import TYPE_CHECKING

import pytest
import yaml
from anyio import Path

from vera.core.data_models.test_case.expected_output import ExpectedOutput
from vera.core.data_models.test_case.load_methods import LoadMethods

if TYPE_CHECKING:
    import pathlib


@pytest.mark.anyio
async def test_expected_output_text() -> None:
    eo = ExpectedOutput(content="hello world", load_as=LoadMethods.TEXT)
    result = await eo.get_expected_output(Path("."))
    assert result == "hello world"


@pytest.mark.anyio
async def test_expected_output_json(tmp_path: pathlib.Path) -> None:
    data = {"a": 1, "b": [2, 3]}
    json_file = tmp_path / "test.json"
    json_file.write_text(json.dumps(data))

    eo = ExpectedOutput(file_name="test.json", load_as=LoadMethods.JSON)
    result = await eo.get_expected_output(Path(str(tmp_path)))
    assert result == data


@pytest.mark.anyio
async def test_expected_output_yaml(tmp_path: pathlib.Path) -> None:
    data = {"a": 1, "b": [2, 3]}
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text(yaml.dump(data))

    eo = ExpectedOutput(file_name="test.yaml", load_as=LoadMethods.YAML)
    result = await eo.get_expected_output(Path(str(tmp_path)))
    assert result == data


@pytest.mark.anyio
async def test_expected_output_csv(tmp_path: pathlib.Path) -> None:
    csv_content = "name,score\ntest1,0.8\ntest2,0.9"
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(csv_content)

    eo = ExpectedOutput(file_name="test.csv", load_as=LoadMethods.CSV)
    result = await eo.get_expected_output(Path(str(tmp_path)))
    assert len(result) == 2
    assert result[0]["name"] == "test1"
    assert result[1]["score"] == "0.9"
