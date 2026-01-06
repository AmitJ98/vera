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

import pathlib
from collections.abc import Iterable  # noqa: TC003
from typing import Any

import anyio
import yaml

import vera
from vera import TestCase

from .core.data_models import (
    LlmChecksColumn,
    SqlQueryInput,
    SqlQueryOutput,
    SqlQueryRow,
    SqlTestCase,
    StaticChecksColumn,
)
from .core.sql_query_assistant import generate_sql
from .core.static_tests import StaticTester

FEATURE_TESTS_DIR: pathlib.Path = pathlib.Path(__file__).parent / "feature_tests"


@vera.hook_impl
def get_test_cases() -> Iterable[TestCase[SqlQueryInput]]:
    """Hook implementation to load SQL-specific test cases.

    It reads from the local 'test_cases.yaml' file and parses them into SqlTestCase models.

    Returns:
        Iterable[TestCase[SqlQueryInput]]: An iterable of SqlTestCase models.

    """
    test_cases_file: pathlib.Path = FEATURE_TESTS_DIR / "test_cases.yaml"
    file_content: str = test_cases_file.read_text(encoding="utf-8")
    test_cases: list[dict[str, Any]] = yaml.safe_load(file_content)
    return [SqlTestCase(**tc) for tc in test_cases]


@vera.hook_impl
async def run_feature(
    test_case: TestCase[SqlQueryInput],
    resources_dir: anyio.Path,
) -> SqlQueryOutput:
    """Hook implementation to execute the SQL Query Assistant feature.

    1. Loads the database schema context from the specified resource file.
    2. Calls the 'generate_sql' function with the context and user query.
    3. Returns the generated SQL wrapped in a SqlQueryOutput model.

    Args:
        test_case: The test case
        resources_dir: The path to the feature's resources dir

    Returns:
        The feature's output

    """
    context = await test_case.input.get_context(resources_dir)
    sql: str = await generate_sql(f"{context}\n\n{test_case.input.user_query}")
    return SqlQueryOutput(sql_query=sql)


@vera.hook_impl
def run_static_tests(
    test_case: TestCase[SqlQueryInput],
    test_output: SqlQueryOutput,
) -> StaticChecksColumn:
    """Hook implementation for programmatic SQL validation.

    Delegates to the EvaluateOutput class to check for prohibited statements (DROP, DELETE).

    Args:
        test_case: The test case input
        test_output: The test case output

    Returns:
        The csv column that describes the results of the tests

    """
    return StaticTester(test_case, test_output).run_static_tests()


@vera.hook_impl
def get_csv_row_class() -> type[SqlQueryRow]:
    """Returns the custom CSV row class for the SQL Query Assistant report.

    Returns:
        type[SqlQueryRow]: The custom CSV row class.

    """
    return SqlQueryRow


@vera.hook_impl
def get_llm_csv_columns_class() -> type[LlmChecksColumn]:
    """Returns the custom LLM evaluation columns for the SQL Query Assistant.

    Returns:
        type[LlmChecksColumn]: The custom LLM evaluation columns class.

    """
    return LlmChecksColumn


@vera.hook_impl
def get_llm_specs_dir() -> anyio.Path:
    """Tells Vera where to find the Markdown specs (Rubric, Safety, etc.) for this plugin.

    Returns:
        anyio.Path: The path to the 'specs' directory.

    """
    return anyio.Path(FEATURE_TESTS_DIR / "specs")


@vera.hook_impl
def get_resources_dir() -> anyio.Path:
    """Tells Vera where to find the resource files (like database schemas) referenced in test cases.

    Returns:
        anyio.Path: The path to the 'resources' directory.
    """
    return anyio.Path(FEATURE_TESTS_DIR / "resources")
