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

from collections import defaultdict
from typing import TYPE_CHECKING, Any

from rich.console import Console
from rich.table import Table

from vera import ScoreRange
from vera.core import utils

if TYPE_CHECKING:
    from vera.core.data_models.csv import CsvRow
    from vera.core.utils import ScoreColor

type _TestCaseIdToScoreRange = dict[int, ScoreRange]
type _TestCaseIdToResults = dict[int, list[int | float]]


class ReportSummary:
    __slots__ = ("all_runs_rows", "ranges", "results")

    def __init__(self, all_runs_rows: list[list[Any]]) -> None:
        self.all_runs_rows: list[list[CsvRow]] = all_runs_rows
        self.results: _TestCaseIdToResults = defaultdict(list)
        self.ranges: _TestCaseIdToScoreRange = {}

    def display(self) -> None:
        if not self.all_runs_rows or not self.all_runs_rows[0]:
            return

        self._set_run_results_and_ranges()
        table: Table = self._build_summary_table()
        console: Console = Console()
        console.print(table)
        if (score := self._get_overall_score()) is not None:
            console.print(score)

    def _set_run_results_and_ranges(self) -> None:
        for run_rows in self.all_runs_rows:
            for row in run_rows:
                test_id: int = row.identifier
                self.results[test_id].append(row.final_score)
                if test_id not in self.ranges:
                    self.ranges[test_id] = row.score_range

    def _build_summary_table(self) -> Table:
        table: Table = Table(title="Test Summary", header_style="bold magenta")
        table.add_column("Test ID", style="cyan")
        table.add_column("Avg Score", justify="right")
        if len(self.all_runs_rows) > 1:
            table.add_column("Min", justify="right")
            table.add_column("Max", justify="right")
            table.add_column("Runs", justify="right")

        for test_id in sorted(self.results):
            scores: list[float] = self.results[test_id]
            avg_score: float = sum(scores) / len(scores)
            score_range: ScoreRange | None = self.ranges.get(test_id)
            color: ScoreColor = "white"
            if score_range is not None:
                color = utils.get_score_color(avg_score, score_range)

            avg_score_str = f"[{color}]{avg_score:.2f}[/{color}]"

            if len(self.all_runs_rows) > 1:
                table.add_row(
                    str(test_id),
                    avg_score_str,
                    f"{min(scores):.2f}",
                    f"{max(scores):.2f}",
                    str(len(scores)),
                )
            else:
                table.add_row(str(test_id), avg_score_str)

        return table

    def _get_overall_score(self) -> str | None:
        all_scores: list[int | float] = [s for scores in self.results.values() for s in scores]
        if not all_scores:
            return None

        total_avg: float = sum(all_scores) / len(all_scores)
        first_range: ScoreRange | None = next(iter(self.ranges.values()), None)
        color: ScoreColor = "green"
        if first_range:
            color = utils.get_score_color(total_avg, first_range)

        return f"\n[bold {color}]Overall Average Score: {total_avg:.2f}[/bold {color}]"
