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

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from vera.core import exceptions
from vera.core.data_models.csv import CsvColumn, CsvRow
from vera.core.data_models.test_case.output import TestCaseOutput
from vera.project_name import PROJECT_NAME

if TYPE_CHECKING:
    from collections.abc import Coroutine, Iterable

    import anyio

    from vera.core.data_models.test_case import TestCase, TestCaseInput
    from vera.core.hook_specs import CliService
    from vera.core.plugin_service import PluginService

type EvalTask = Coroutine[Any, Any, CsvColumn]

logger: logging.Logger = logging.getLogger(PROJECT_NAME)


class TestingService[
    T_Input: TestCaseInput,
    T_Output: TestCaseOutput,
    T_Row: CsvRow,
    T_TaskId,
]:
    def __init__(
        self,
        test_cases: Iterable[TestCase[T_Input]],
        plugin_service: PluginService[T_Input, T_Output, T_Row],
        cli_service: CliService[Any, T_TaskId],
    ) -> None:
        self.plugin_service: PluginService[T_Input, T_Output, T_Row] = plugin_service
        self.csv_rows: list[T_Row] = []
        self.test_cases: Iterable[TestCase[T_Input]] = test_cases
        self.cli_service: CliService[Any, T_TaskId] = cli_service

    async def run_tests(self) -> None:
        strict_errors: list[Exception] = []
        try:
            async with asyncio.TaskGroup() as tg:
                for test_case in self.test_cases:
                    tg.create_task(self._run_task(test_case, strict_errors))

        except* Exception:
            logger.exception("TaskGroup failed during test suite execution")

        if strict_errors:
            msg: str = "Strict mode test failures"
            raise ExceptionGroup(msg, strict_errors)

    async def _run_task(self, test_case: TestCase, strict_errors: list[Exception]) -> None:
        try:
            await self.process_single_case(test_case)
        except exceptions.TestCaseTestingError as e:
            strict_errors.append(e)
        except Exception as e:
            logger.exception("Unexpected error in test task for test case %s", test_case.id)
            if test_case.config.strict_mode:
                strict_errors.append(e)

    async def process_single_case(self, test_case: TestCase) -> None:
        task_id: T_TaskId = self.cli_service.add_task(f"[cyan]Test {test_case.id}[/cyan]")
        try:
            logger.debug("Test case %s details: %s", test_case.id, test_case.model_dump())
            async with asyncio.timeout(test_case.config.timeout_seconds):
                output: T_Output = await self._run_feature_stage(test_case, task_id)
                static_cols, llm_cols = await self._run_testing_stage(test_case, output, task_id)
                await self._finalize_row_stage(test_case, output, static_cols, llm_cols, task_id)

        except TimeoutError as e:
            self._handle_timeout(test_case, task_id, e)

        except Exception as e:  # noqa: BLE001
            self._handle_error(test_case, task_id, e)

        finally:
            await self._cleanup_task(task_id)

    async def _run_feature_stage(self, test_case: TestCase, task_id: T_TaskId) -> T_Output:
        self.cli_service.update_task(
            task_id,
            description=f"Test {test_case.id}: [yellow]Running feature...[/yellow]",
            completed=10,
        )

        resources_dir: anyio.Path = self.plugin_service.get_resources_dir()
        logger.debug("Test case %s: using resources_dir: %s", test_case.id, resources_dir)

        logger.debug("Test case %s: running feature", test_case.id)
        output: T_Output = await self.plugin_service.run_feature(
            test_case=test_case, resources_dir=resources_dir
        )
        logger.debug("Test case %s: feature output: %s", test_case.id, output.model_dump())
        return output

    async def _run_testing_stage(
        self,
        test_case: TestCase,
        output: T_Output,
        task_id: T_TaskId,
    ) -> tuple[CsvColumn, CsvColumn]:
        self.cli_service.update_task(
            task_id,
            description=f"Test {test_case.id}: [yellow]Evaluating...[/yellow]",
            completed=40,
        )

        logger.debug("Test case %s: starting evaluation and test tasks", test_case.id)
        static_task: EvalTask = asyncio.to_thread(
            self.plugin_service.run_static_tests,
            test_case=test_case,
            test_output=output,
        )
        llm_task: EvalTask = self.plugin_service.llm_evaluation(
            test_case=test_case,
            test_output=output,
            plugin_service=self.plugin_service,
        )

        static_checks_cols, llm_checks_cols = await asyncio.gather(static_task, llm_task)
        logger.debug("Test case %s: evaluation tasks completed", test_case.id)
        return static_checks_cols, llm_checks_cols

    async def _finalize_row_stage(
        self,
        test_case: TestCase,
        output: T_Output,
        static_checks_cols: CsvColumn,
        llm_checks_cols: CsvColumn,
        task_id: T_TaskId,
    ) -> None:
        self.cli_service.update_task(
            task_id,
            description=f"Test {test_case.id}: [yellow]Finalizing...[/yellow]",
            completed=80,
        )

        row_class: type[T_Row] = self.plugin_service.get_csv_row_class()
        row: T_Row = row_class.from_columns(
            test_case=test_case,
            test_output=output,
            llm_checks_columns=llm_checks_cols,
            static_checks_columns=static_checks_cols,
        )
        logger.debug("Test case %s: row created with score %s", test_case.id, row.final_score)
        self.csv_rows.append(row)

        color: str = row.get_score_color()
        self.cli_service.update_task(
            task_id,
            description=f"Test {test_case.id}: [{color}]Score {row.final_score:.2f}[/{color}]",
            completed=100,
        )

    def _handle_timeout(self, test_case: TestCase, task_id: T_TaskId, e: TimeoutError) -> None:
        self.cli_service.update_task(
            task_id,
            description=f"Test {test_case.id}: [red]Timeout[/red]",
            completed=100,
        )
        logger.error("Test case %s reached timeout", test_case.id)
        if test_case.config.strict_mode:
            msg: str = f"Failed to run test case {test_case.id}."
            raise exceptions.TestCaseTestingError(msg) from e

    def _handle_error(self, test_case: TestCase, task_id: T_TaskId, e: Exception) -> None:
        self.cli_service.update_task(
            task_id, description=f"Test {test_case.id}: [red]Error[/red]", completed=100
        )
        logger.error("Error processing test case %s", test_case.id)
        if test_case.config.strict_mode:
            msg: str = f"Failed to run test case {test_case.id}."
            raise exceptions.TestCaseTestingError(msg) from e

    async def _cleanup_task(self, task_id: T_TaskId) -> None:
        await asyncio.sleep(0.5)
        self.cli_service.remove_task(task_id)
        self.cli_service.advance_overall()

    async def publish_results(self, run_index: int) -> None:
        logger.debug("Publishing results for %s rows", len(self.csv_rows))
        await asyncio.gather(
            *self.plugin_service.publish_results(
                rows=sorted(self.csv_rows, key=lambda tc: tc.identifier),
                run_index=run_index,
            )
        )
        logger.debug("Results published successfully")
