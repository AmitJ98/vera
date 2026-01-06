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

import abc
from typing import TYPE_CHECKING, Annotated, NamedTuple, Self

from pydantic import BaseModel, Field

from vera.core import utils

from .test_case.input import TestCaseInput

if TYPE_CHECKING:
    from vera.core.utils import ScoreColor

    from .test_case import TestCase
    from .test_case.output import TestCaseOutput


class ScoreRange(NamedTuple):
    min: float
    max: float


class CsvColumn(BaseModel, abc.ABC):
    pass


class CsvRow[T_In: TestCaseInput, T_Out: TestCaseOutput, T: CsvColumn, E: CsvColumn](
    BaseModel, abc.ABC
):
    identifier: Annotated[int, Field(alias="Test Case ID")]
    final_score: Annotated[int | float, Field(alias="Final Score")]

    @abc.abstractmethod
    def calculate_final_score(self) -> int | float: ...

    @property
    @abc.abstractmethod
    def score_range(self) -> ScoreRange: ...

    def get_score_color(self) -> ScoreColor:
        return utils.get_score_color(self.final_score, self.score_range)

    @classmethod
    @abc.abstractmethod
    def from_columns(
        cls,
        test_case: TestCase[T_In],
        test_output: T_Out,
        llm_checks_columns: T,
        static_checks_columns: E,
    ) -> Self: ...
