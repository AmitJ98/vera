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

from typing import Any


class MockCliService:
    def __init__(self, progress: Any = None, overall_task_id: Any = None) -> None:  # noqa: ANN401
        self.progress = progress
        self.overall_task_id = overall_task_id
        self.tasks: dict[Any, dict[str, Any]] = {}
        self.overall_advances: float = 0.0

    def add_task(self, description: str, total: int = 100, *, visible: bool = True) -> int:
        task_id = len(self.tasks)
        self.tasks[task_id] = {
            "description": description,
            "total": total,
            "visible": visible,
            "completed": 0.0,
        }
        return task_id

    def update_task(
        self,
        task_id: int,
        description: str | None = None,
        completed: float | None = None,
        advance: float | None = None,
        *,
        visible: bool | None = None,
    ) -> None:
        if task_id not in self.tasks:
            return

        task = self.tasks[task_id]
        if description is not None:
            task["description"] = description
        if completed is not None:
            task["completed"] = completed
        if advance is not None:
            task["completed"] += advance
        if visible is not None:
            task["visible"] = visible

    def remove_task(self, task_id: int) -> None:
        if task_id in self.tasks:
            del self.tasks[task_id]

    def advance_overall(self, amount: float = 1.0) -> None:
        self.overall_advances += amount
