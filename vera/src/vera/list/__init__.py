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

import logging
from typing import TYPE_CHECKING

import typer

from vera.core import plugin_service, utils
from vera.project_name import PROJECT_NAME

if TYPE_CHECKING:
    from vera.core.plugin_service import PluginCreation

app: typer.Typer = typer.Typer(help="List plugins.")
logger: logging.Logger = logging.getLogger(PROJECT_NAME)

__all__: list[str] = ["app"]


@app.command(name="list", help="List all registered plugins")
def list_plugins() -> None:
    pc: PluginCreation = plugin_service.create_service()
    names: str = utils.create_plugin_name_display_repr(pc.registered_plugin_names)
    if not names:
        logger.info("[red]No registered plugins found")
        logger.info('Please use "uv pip install -e path/to/plugin" to install a plugin')
    else:
        logger.info("Registered plugins:\n%s", names)
