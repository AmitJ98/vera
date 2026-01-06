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

if TYPE_CHECKING:
    from rich.progress import Progress, TaskID


class RichCliService:
    def __init__(self, progress: Progress, overall_task_id: TaskID) -> None:
        self.progress: Progress = progress
        self.overall_task_id: TaskID = overall_task_id

    def add_task(
        self,
        description: str,
        total: int = 100,
        *,
        visible: bool = True,
    ) -> TaskID | None:
        if self.progress is not None:
            return self.progress.add_task(description, total=total, visible=visible)

        return None

    def update_task(
        self,
        task_id: TaskID,
        description: str | None = None,
        completed: float | None = None,
        advance: float | None = None,
        *,
        visible: bool | None = None,
    ) -> None:
        if self.progress is not None and task_id is not None:
            self.progress.update(
                task_id,
                description=description,
                completed=completed,
                advance=advance,
                visible=visible,
            )

    def remove_task(self, task_id: TaskID) -> None:
        if self.progress is not None and task_id is not None:
            self.progress.remove_task(task_id)

    def advance_overall(self, amount: float = 1.0) -> None:
        if self.progress is not None and self.overall_task_id is not None:
            self.progress.advance(self.overall_task_id, advance=amount)
