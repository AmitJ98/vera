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

import argparse
import asyncio
import getpass
import logging
from collections.abc import Iterable  # noqa: TC003

import vera
from vera import CsvRow, VeraConfig

from .core.gs_client import GoogleSheetsClient

logger: logging.Logger = logging.getLogger(vera.PROJECT_NAME)


class GoogleSheetsConfig(VeraConfig):
    gs_credentials: str | None = None
    gs_spreadsheet_id: str | None = None
    gs_user: str | None = None
    gs_password: str | None = None
    gs_combine: bool = False


@vera.hook_impl
def display_test_command_help(extra_args: list[str]) -> bool:
    """Displays help for additional CLI arguments for the 'eval' command.

    Returns:
        bool: True if help was displayed, False otherwise.
    """
    if "--gs-help" not in extra_args:
        return False

    logger.debug("Showing Google Sheets 'eval' help")
    parser: argparse.ArgumentParser = _get_gs_test_command_parser()
    parser.print_help()
    extra_args.remove("--gs-help")
    return True


@vera.hook_impl
def handle_test_command_extra_args(extra_args: list[str]) -> None:
    """Parses extra arguments for the 'eval' command."""
    logger.debug("Parsing extra 'eval' arguments for Google Sheets plugin: %s", extra_args)
    parser: argparse.ArgumentParser = _get_gs_test_command_parser()
    args, remaining = parser.parse_known_args(extra_args)
    extra_args[:] = remaining
    config: VeraConfig[GoogleSheetsConfig] = GoogleSheetsConfig.get()
    config.gs_combine = args.gs_combine
    logger.debug("GS Combine set to: %s", config.gs_combine)


def _get_gs_test_command_parser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Google Sheets Report 'eval' options:",
        add_help=False,
    )
    parser.add_argument(
        "--gs-combine",
        action="store_true",
        default=False,
        help="Combine results from different suites into a single Google Sheet.",
    )
    return parser


@vera.hook_impl
def display_config_command_help(extra_args: list[str]) -> bool:
    """Displays help for additional CLI arguments for the 'config' command.

    Returns:
        bool: True if help was displayed, False otherwise.

    """
    if "--gs-help" not in extra_args:
        return False

    logger.debug("Showing Google Sheets 'config' help")
    parser: argparse.ArgumentParser = _get_gs_config_command_parser()
    parser.print_help()
    extra_args.remove("--gs-help")
    return True


@vera.hook_impl
def handle_config_command_extra_args(config: VeraConfig, extra_args: list[str]) -> None:
    """Parses extra arguments for the 'config' command."""
    logger.debug("Parsing extra 'config' arguments for Google Sheets plugin: %s", extra_args)
    parser: argparse.ArgumentParser = _get_gs_config_command_parser()
    args, remaining = parser.parse_known_args(extra_args)
    extra_args[:] = remaining

    gs_config: GoogleSheetsConfig = config.as_type(GoogleSheetsConfig)
    if args.gs_credentials:
        gs_config.gs_credentials = args.gs_credentials
        logger.info("GS Credentials set to: %s", args.gs_credentials)

    if args.gs_spreadsheet_id:
        gs_config.gs_spreadsheet_id = args.gs_spreadsheet_id
        logger.info("GS Spreadsheet ID set to: %s", args.gs_spreadsheet_id)

    if args.gs_user:
        gs_config.gs_user = args.gs_user
        logger.info("GS User set to: %s", args.gs_user)

    if args.gs_password:
        if args.gs_password is True:
            logger.debug("Prompting for GS password")
            gs_config.gs_password = getpass.getpass("Enter Google Sheets Password: ")
        else:
            gs_config.gs_password = args.gs_password
        logger.info("GS Password updated.")


def _get_gs_config_command_parser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Google Sheets Report 'config' options:",
        add_help=False,
    )
    parser.add_argument(
        "--gs-credentials",
        type=str,
        help="Path to the Google Sheets service account credentials JSON file.",
    )
    parser.add_argument(
        "--gs-spreadsheet-id",
        type=str,
        help="The ID of the Google Spreadsheet to publish results to.",
    )
    parser.add_argument("--gs-user", type=str, help="Google Sheets username for tracking.")
    parser.add_argument(
        "--gs-password",
        nargs="?",
        const=True,
        help="Google Sheets password. Use without value to prompt for it.",
    )
    return parser


@vera.hook_impl
def handle_config_command_display(config: VeraConfig) -> None:
    """Displays Google Sheets configuration."""
    gs_config: GoogleSheetsConfig = config.as_type(GoogleSheetsConfig)
    if gs_config.gs_spreadsheet_id:
        logger.info("  GS Spreadsheet ID: %s", gs_config.gs_spreadsheet_id)
    if gs_config.gs_credentials:
        logger.info("  GS Credentials Path: %s", gs_config.gs_credentials)
    if gs_config.gs_user:
        logger.info("  GS User: %s", gs_config.gs_user)
    if gs_config.gs_password:
        logger.info("  GS Password: %s", "*******" if gs_config.gs_password else "Not set")


@vera.hook_impl
async def publish_results(rows: Iterable[CsvRow], run_index: int) -> None:
    """Publishes results to Google Sheets."""
    config: VeraConfig[GoogleSheetsConfig] = GoogleSheetsConfig.get()
    gs_credentials: str = config.gs_credentials or ""
    gs_spreadsheet_id: str = config.gs_spreadsheet_id or ""
    gs_combine: bool = config.gs_combine

    if not gs_credentials or not gs_spreadsheet_id:
        logger.debug("Google Sheets configuration incomplete. Skipping GS reporting.")
        return

    logger.info("Publishing results to Google Sheets (Run %s)...", run_index + 1)
    await asyncio.to_thread(
        _publish_to_gs,
        rows=rows,
        run_index=run_index,
        credentials=gs_credentials,
        spreadsheet_id=gs_spreadsheet_id,
        combine=gs_combine,
    )
    logger.info("Successfully published results to Google Sheets.")


def _publish_to_gs(
    rows: Iterable[CsvRow],
    run_index: int,
    credentials: str,
    spreadsheet_id: str,
    *,
    combine: bool,
) -> None:
    client: GoogleSheetsClient = GoogleSheetsClient(credentials)
    header, data = get_header_and_data_from_rows(rows)
    if not data:
        logger.warning("No data to publish to Google Sheets.")
        return

    sheet_name = "Combined Results" if combine else f"Run {run_index + 1}"
    logger.debug("Target sheet: '%s'", sheet_name)
    client.ensure_sheet_exists(spreadsheet_id, sheet_name)

    values = [header, *data] if (run_index == 0 or not combine) else data
    logger.debug("Appending %d rows to sheet '%s'", len(data), sheet_name)
    client.append_rows(spreadsheet_id, f"'{sheet_name}'!A1", values)


def get_header_and_data_from_rows(rows: Iterable[CsvRow]) -> tuple[list[str], list[list[str]]]:
    data: list[list[str]] = []
    header: list[str] = []
    for i, row in enumerate(rows):
        row_dict = row.model_dump(by_alias=True)
        if i == 0:
            header = list(row_dict.keys())

        data.append(list(row_dict.values()))

    return header, data
