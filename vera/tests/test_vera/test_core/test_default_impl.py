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

from unittest.mock import AsyncMock, patch

import pytest

from vera.core import default_impl
from vera.core.configuration import VeraConfig
from vera.project_name import PROJECT_NAME


@pytest.mark.anyio
async def test_publish_results_respects_config() -> None:
    # Setup config to disable CSV
    config = VeraConfig(enable_csv_report=False)

    with (
        patch(f"{PROJECT_NAME}.core.default_impl.CONFIG", config),
        patch(
            f"{PROJECT_NAME}.core.default_impl.write_to_file", new_callable=AsyncMock
        ) as mock_write,
    ):
        await default_impl.publish_results([])
        mock_write.assert_not_called()


@pytest.mark.anyio
async def test_publish_results_enabled_by_default() -> None:
    # Setup config to ENABLE CSV (default)
    config = VeraConfig(enable_csv_report=True)

    with (
        patch(f"{PROJECT_NAME}.core.default_impl.CONFIG", config),
        patch(
            f"{PROJECT_NAME}.core.default_impl.write_to_file", new_callable=AsyncMock
        ) as mock_write,
    ):
        await default_impl.publish_results([])
        mock_write.assert_called_once()
