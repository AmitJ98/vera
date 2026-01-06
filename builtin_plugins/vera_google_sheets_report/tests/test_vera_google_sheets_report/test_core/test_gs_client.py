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

from unittest.mock import MagicMock, patch

from vera_google_sheets_report.core.gs_client import GoogleSheetsClient


@patch("vera_google_sheets_report.core.gs_client.build")
@patch(
    "vera_google_sheets_report.core.gs_client.service_account.Credentials.from_service_account_file"
)
def test_gs_client_init(mock_creds_file: MagicMock, mock_build: MagicMock) -> None:
    mock_creds = MagicMock()
    mock_creds_file.return_value = mock_creds

    client = GoogleSheetsClient("path/to/creds.json")

    mock_creds_file.assert_called_once_with(
        "path/to/creds.json", scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    mock_build.assert_called_once_with(
        "sheets", "v4", credentials=mock_creds, cache_discovery=False
    )
    assert client.service == mock_build.return_value


@patch("vera_google_sheets_report.core.gs_client.build")
@patch(
    "vera_google_sheets_report.core.gs_client.service_account.Credentials.from_service_account_file"
)
def test_append_rows(_: MagicMock, mock_build: MagicMock) -> None:  # noqa: PT019
    mock_service = mock_build.return_value
    client = GoogleSheetsClient("path/to/creds.json")

    values = [["header1", "header2"], ["val1", "val2"]]
    client.append_rows("spread_id", "sheet1!A1", values)

    mock_service.spreadsheets.return_value.values.return_value.append.assert_called_once_with(
        spreadsheetId="spread_id",
        range="sheet1!A1",
        valueInputOption="RAW",
        body={"values": values},
    )


@patch("vera_google_sheets_report.core.gs_client.build")
@patch(
    "vera_google_sheets_report.core.gs_client.service_account.Credentials.from_service_account_file"
)
def test_ensure_sheet_exists_already_exists(_: MagicMock, mock_build: MagicMock) -> None:  # noqa: PT019
    mock_service = mock_build.return_value
    client = GoogleSheetsClient("path/to/creds.json")

    mock_service.spreadsheets.return_value.get.return_value.execute.return_value = {
        "sheets": [{"properties": {"title": "Sheet1"}}]
    }

    client.ensure_sheet_exists("spread_id", "Sheet1")

    mock_service.spreadsheets.return_value.get.assert_called_once_with(spreadsheetId="spread_id")
    mock_service.spreadsheets.return_value.batchUpdate.assert_not_called()


@patch("vera_google_sheets_report.core.gs_client.build")
@patch(
    "vera_google_sheets_report.core.gs_client.service_account.Credentials.from_service_account_file"
)
def test_ensure_sheet_exists_not_exists(_: MagicMock, mock_build: MagicMock) -> None:  # noqa: PT019
    mock_service = mock_build.return_value
    client = GoogleSheetsClient("path/to/creds.json")

    mock_service.spreadsheets.return_value.get.return_value.execute.return_value = {
        "sheets": [{"properties": {"title": "Sheet1"}}]
    }

    client.ensure_sheet_exists("spread_id", "Sheet2")

    mock_service.spreadsheets.return_value.batchUpdate.assert_called_once()
    kwargs = mock_service.spreadsheets.return_value.batchUpdate.call_args.kwargs
    assert kwargs["spreadsheetId"] == "spread_id"
    assert kwargs["body"]["requests"][0]["addSheet"]["properties"]["title"] == "Sheet2"


@patch("vera_google_sheets_report.core.gs_client.build")
@patch(
    "vera_google_sheets_report.core.gs_client.service_account.Credentials.from_service_account_file"
)
def test_ensure_sheet_exists_handles_already_exists_error(
    _: MagicMock,  # noqa: PT019
    mock_build: MagicMock,
) -> None:
    mock_service = mock_build.return_value
    client = GoogleSheetsClient("path/to/creds.json")

    mock_service.spreadsheets.return_value.get.return_value.execute.return_value = {
        "sheets": [{"properties": {"title": "Sheet1"}}]
    }

    # Simulate the error that sheet already exists even if not found in initial get (race condition)
    mock_service.spreadsheets.return_value.batchUpdate.return_value.execute.side_effect = Exception(
        "already exists"
    )

    # Should not raise exception
    client.ensure_sheet_exists("spread_id", "Sheet2")

    mock_service.spreadsheets.return_value.batchUpdate.assert_called_once()
