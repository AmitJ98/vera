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
import pathlib
import shutil
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, NamedTuple

import typer

from vera.project_name import PROJECT_NAME

from . import plugin_template

if TYPE_CHECKING:
    from .plugin_template import PluginDetails

app: typer.Typer = typer.Typer(help="Create new plugins.")
logger: logging.Logger = logging.getLogger(PROJECT_NAME)


class CreateOptions(NamedTuple):
    name: str
    description: str
    dst_dir: Path | None
    override_existing: bool


@app.command(name="create", help="Scaffold a new plugin template.")
def create_plugin(
    name: Annotated[
        str,
        typer.Option(
            help='Name of the feature to create in snake_case. E.g. "response_code_generation"'
        ),
    ],
    description: Annotated[str, typer.Option(help="The description of the project")] = "",
    dest_dir: Annotated[
        Path | None,
        typer.Option(
            "-d",
            "--dst-dir",
            help=(
                "The directory in which to create the plugin. If not specified - defaults to cwd"
            ),
        ),
    ] = None,
    *,
    override_existing: Annotated[bool, typer.Option(help="Override existing directories")] = False,
) -> None:
    options: CreateOptions = CreateOptions(
        name=name,
        description=description,
        dst_dir=dest_dir,
        override_existing=override_existing,
    )
    _create_plugin_template(options)


def _create_plugin_template(o: CreateOptions, /) -> None:
    with tempfile.TemporaryDirectory() as d:
        tmpdir: Path = pathlib.Path(d)
        _copy_template_into_tmpdir(tmpdir, plugin_template.TEMPLATE_PLUGIN_NAME)
        plugin_details: PluginDetails = plugin_template.PluginDetails(o.name, o.description)
        plugin_template.populate(tmpdir, plugin_details)
        results_dir: Path = o.dst_dir if o.dst_dir is not None else pathlib.Path.cwd()
        _copy_from_tmp_to_dst(
            tmp_dir=tmpdir / plugin_details.name,
            dst=results_dir,
            override=o.override_existing,
        )


def _copy_template_into_tmpdir(tmp_dir: Path, template_name: str) -> Path:
    template_dir: Path = pathlib.Path(__file__).parent / template_name
    return template_dir.copy_into(tmp_dir)


def _copy_from_tmp_to_dst(tmp_dir: Path, dst: Path, *, override: bool) -> None:
    dst.mkdir(exist_ok=True, parents=True)
    if override and (d := dst / tmp_dir.name).exists():
        shutil.rmtree(d)

    try:
        tmp_dir.copy_into(dst)
        logger.info("Created a new directory at '%s/%s'", dst, tmp_dir.name)
    except FileExistsError:
        logger.exception("A directory with the name '%s' already exists", tmp_dir.name)
