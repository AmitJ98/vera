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

from typing import Protocol


class CliService[P, T](Protocol):
    progress: P
    overall_task_id: T

    def add_task(self, description: str, total: int = 100, *, visible: bool = True) -> T: ...

    def update_task(
        self,
        task_id: T,
        description: str | None = None,
        completed: float | None = None,
        advance: float | None = None,
        *,
        visible: bool | None = None,
    ) -> None: ...

    def remove_task(self, task_id: T) -> None: ...

    def advance_overall(self, amount: float = 1.0) -> None: ...
