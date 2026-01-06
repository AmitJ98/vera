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

import dataclasses
import logging
from typing import TYPE_CHECKING, Self, cast

import typer

from vera.core import exceptions, utils
from vera.project_name import PROJECT_NAME

if TYPE_CHECKING:
    from vera.core.plugin_service import PluginCreation


logger: logging.Logger = logging.getLogger(PROJECT_NAME)


@dataclasses.dataclass(slots=True, frozen=True)
class TestSetup:
    pc: PluginCreation

    def handle_command_extrac_args(self, context: typer.Context) -> Self:
        extra_args: list[str] = list(context.args)
        help_results: list[bool | None] = cast(
            "list[bool | None]",
            cast(
                "object",
                self.pc.plugin_service.display_test_command_help(extra_args=extra_args),
            ),
        )
        if any(help_results):
            raise typer.Exit

        self.pc.plugin_service.handle_test_command_extra_args(extra_args=extra_args)

        if extra_args:
            logger.error("Unknown options: %s", extra_args)
            raise typer.Exit(1)

        return self

    def validate_llm_api_key(self) -> Self:
        try:
            _ = self.pc.plugin_service.get_llm_configuration().api_key
        except exceptions.ApiKeyNotFoundError as e:
            logger.exception("API key not found")
            raise typer.Exit(1) from e

        return self

    def log_plugin_names(self) -> Self:
        names: str = utils.create_plugin_name_display_repr(self.pc.registered_plugin_names)
        if names:
            logger.info("Running with selected plugins:\n%s", names)
        else:
            logger.info(
                "[red]No plugins found[/red]\nPlease install at least one plugin to evaluate."
                '\nUse "uv pip install -e path/to/plugin" to install a plugin.'
            )
            raise typer.Exit(1)

        return self
