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
from pathlib import Path  # noqa: TC003
from typing import Annotated, NamedTuple, cast

import typer

from vera.core import plugin_service
from vera.core.configuration import VeraConfig, get_config_path
from vera.project_name import PROJECT_NAME

app: typer.Typer = typer.Typer(help="Configure Vera.")
logger: logging.Logger = logging.getLogger(PROJECT_NAME)


class ConfigOptions(NamedTuple):
    dst_dir: Path | None
    gemini_api_key: str | None
    report_name: str | None
    enable_csv: bool | None
    log_level: str | None
    context: typer.Context

    @property
    def is_empty(self) -> bool:
        return (
            self.dst_dir is None
            and self.gemini_api_key is None
            and self.report_name is None
            and self.enable_csv is None
            and self.log_level is None
            and not self.context.args
        )


@app.command(
    name="config",
    help="Configure Vera default settings.",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def configure(  # noqa: PLR0913, PLR0917
    ctx: typer.Context,
    dst_dir: Annotated[
        Path | None,
        typer.Option(
            "--dst-dir",
            "-d",
            help=(
                "The default destination directory where the results csv files will be written into"
            ),
        ),
    ] = None,
    gemini_api_key: Annotated[
        str | None,
        typer.Option(
            "--gemini-api-key",
            "-k",
            help="The Gemini API key to use for evaluations",
            hide_input=True,
            prompt="Enter Gemini API Key",
            prompt_required=False,
        ),
    ] = None,
    report_name: Annotated[
        str | None,
        typer.Option(
            help="The base name for the report file (default: report)",
        ),
    ] = None,
    enabled_csv: Annotated[
        bool | None,
        typer.Option(
            "--enable-csv/--disable-csv",
            help="Disable or enable the default CSV report generation",
        ),
    ] = None,
    log_level: Annotated[
        str | None,
        typer.Option(
            "--log-level",
            "-l",
            help="Set the default log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
        ),
    ] = None,
) -> None:
    options: ConfigOptions = ConfigOptions(
        dst_dir=dst_dir,
        gemini_api_key=gemini_api_key,
        report_name=report_name,
        enable_csv=enabled_csv,
        log_level=log_level,
        context=ctx,
    )
    _configure(options)


def _configure(options: ConfigOptions) -> None:
    config: VeraConfig = VeraConfig.load()

    if options.dst_dir is not None:
        config.dst_dir = options.dst_dir
        logger.info("Default destination directory set to: %s", options.dst_dir)

    if options.gemini_api_key is not None:
        config.gemini_api_key = options.gemini_api_key
        logger.info("Gemini API key saved.")

    if options.report_name is not None:
        config.report_name = options.report_name
        logger.info("Report name set to: %s", options.report_name)

    if options.enable_csv is not None:
        config.enable_csv_report = options.enable_csv
        logger.info(
            "Default CSV report generation set to: %s",
            "Enabled" if options.enable_csv else "Disabled",
        )

    if options.log_level is not None:
        config.log_level = options.log_level.upper()
        logger.info("Default log level set to: %s", config.log_level)

    pc = plugin_service.create_service()
    extra_args = list(options.context.args)

    help_results: list[bool | None] = cast(
        "list[bool | None]",
        cast(
            "object",
            pc.plugin_service.display_config_command_help(extra_args=extra_args),
        ),
    )
    if any(help_results):
        raise typer.Exit

    pc.plugin_service.handle_config_command_extra_args(config=config, extra_args=extra_args)

    if extra_args:
        logger.error("Unknown options: %s", extra_args)
        raise typer.Exit(1)

    if options.is_empty:
        config_path = get_config_path()
        logger.info("Config file location: %s", config_path)
        if config_path.exists():
            logger.info("Current configuration:")
            logger.info("  Destination Directory: %s", config.dst_dir or "Not set")
            logger.info(
                "  Gemini API Key: %s",
                "*******" if config.gemini_api_key else "Not set",
            )
            logger.info("  Report Name: %s", config.report_name)
            logger.info("  CSV Report Enabled: %s", config.enable_csv_report)
            logger.info("  Log Level: %s", config.log_level)
            pc.plugin_service.handle_config_command_display(config=config)
        else:
            logger.info("No configuration file found.")
        return

    config.save()
    logger.info("Configuration saved to: %s", get_config_path())
