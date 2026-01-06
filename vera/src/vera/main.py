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

import typer
from typer import Typer

from . import config, create, vtest
from . import list as list_plugins
from .core import plugin_service
from .core.configuration import CONFIG
from .logger import setup_logging

if TYPE_CHECKING:
    from .core.plugin_service import PluginCreation

app: Typer = typer.Typer(help="Vera: AI Feature Evaluation Tool")
app.add_typer(vtest.app)
app.add_typer(create.app)
app.add_typer(list_plugins.app)
app.add_typer(config.app)


@app.callback()
def callback() -> None:
    setup_logging(level=CONFIG.log_level)


def main() -> None:
    pc: PluginCreation = plugin_service.create_service()
    pc.plugin_service.extend_cli(app=app)
    setup_logging(level=CONFIG.log_level)
    app()


if __name__ == "__main__":
    main()
