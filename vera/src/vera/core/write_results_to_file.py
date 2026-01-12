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
import csv
import logging
import pathlib
from typing import TYPE_CHECKING

from anyio import Path

from vera.project_name import PROJECT_NAME

from .configuration import CONFIG

if TYPE_CHECKING:
    from collections.abc import Iterable

    from .data_models.csv import CsvRow

logger: logging.Logger = logging.getLogger(PROJECT_NAME)
_file_lock = asyncio.Lock()


async def write_to_file(rows: Iterable[CsvRow]) -> None:
    if not rows:
        logger.warning("Now rows to write, skipping report file creation")
        return

    logger.debug("Writing results to file")
    first_row: bool = True
    report_dir: Path = await get_report_dir()
    logger.debug("Ensuring report directory exists: %s", report_dir)
    await report_dir.mkdir(exist_ok=True, parents=True)

    async with _file_lock:
        logger.debug("Acquired file lock, creating report file")
        report_file: Path = await create_report_file(report_dir)

    logger.info("Writing results to the specified file path: %s", await report_file.absolute())

    with pathlib.Path(await report_file.absolute()).open("w", encoding="utf-8", newline="") as f:  # noqa: ASYNC230
        writer: csv.DictWriter[str] | None = None
        for row in rows:
            if first_row:
                writer = csv.DictWriter(f, fieldnames=row.model_dump(by_alias=True).keys())
                writer.writeheader()
                first_row = False

            if writer:
                writer.writerow(row.model_dump(by_alias=True))


async def get_report_dir() -> Path:
    if CONFIG.dst_dir is None:
        path: Path = await (await Path.home()).resolve()
        logger.warning(
            "No output destination directory configured. Writing results to the home directory: %s",
            await path.absolute(),
        )
        return path

    path: Path = await Path(CONFIG.dst_dir).resolve()
    return path


async def create_report_file(report_dir: Path) -> Path:
    count: int = 1
    file_name_template: str = f"{CONFIG.report_name}_{{0}}.csv"
    while await (report_dir / file_name_template.format(count)).exists():
        logger.debug(
            "Report file %s already exists, incrementing counter",
            file_name_template.format(count),
        )
        count += 1

    f: Path = report_dir / file_name_template.format(count)
    await f.touch()
    return f
