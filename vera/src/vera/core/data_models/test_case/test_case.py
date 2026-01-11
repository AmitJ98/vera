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

from typing import Annotated

from pydantic import BaseModel, Field, PositiveInt

from .config import TestCaseConfig
from .expected_output import ExpectedOutput
from .input import TestCaseInput


class TestCase[T_Input: TestCaseInput](BaseModel):
    id: PositiveInt
    name: str
    description: str
    input: T_Input
    config: Annotated[TestCaseConfig, Field(default_factory=TestCaseConfig)]
    tags: Annotated[list[str], Field(default_factory=list)]
    expected_output: Annotated[ExpectedOutput | None, Field(default_factory=ExpectedOutput)]
