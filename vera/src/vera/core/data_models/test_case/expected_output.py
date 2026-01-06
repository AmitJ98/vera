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

import csv
import io
import json
import tomllib
from typing import TYPE_CHECKING, Any, overload

import yaml
from pydantic import BaseModel

from .load_methods import LoadMethods

if TYPE_CHECKING:
    from collections.abc import Callable

    import anyio


class ExpectedOutput(BaseModel):
    file_name: str | None = None
    load_as: LoadMethods = LoadMethods.TEXT
    content: str = ""

    @overload
    async def get_expected_output(self, resources_dir: anyio.Path) -> list[dict[str, Any]]: ...
    @overload
    async def get_expected_output(self, resources_dir: anyio.Path) -> dict[str, Any]: ...

    @overload
    async def get_expected_output(self, resources_dir: anyio.Path) -> bytes: ...

    @overload
    async def get_expected_output(self, resources_dir: anyio.Path) -> str: ...

    async def get_expected_output(self, resources_dir: anyio.Path) -> Any:
        if self.content or self.file_name is None:
            return self.content

        path: anyio.Path = resources_dir / self.file_name
        load_methods_to_func: dict[LoadMethods, Callable[[str], Any]] = {
            LoadMethods.TEXT: lambda x: x,
            LoadMethods.JSON: json.loads,
            LoadMethods.BINARY: lambda x: x.encode(),
            LoadMethods.TOML: tomllib.loads,
            LoadMethods.YAML: yaml.safe_load,
            LoadMethods.CSV: lambda x: list(csv.DictReader(io.StringIO(x))),
        }
        func: Callable[[str], Any] = load_methods_to_func[self.load_as]
        content: str = await path.read_text(encoding="utf-8")
        return func(content)
