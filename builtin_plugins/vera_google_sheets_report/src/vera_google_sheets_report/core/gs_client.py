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

from google.oauth2 import service_account
from googleapiclient.discovery import build

import vera

logger: logging.Logger = logging.getLogger(vera.PROJECT_NAME)


class GoogleSheetsClient:
    def __init__(self, credentials_path: str) -> None:
        logger.debug("Initializing Google Sheets client with credentials: %s", credentials_path)
        self.creds = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )
        self.service = build("sheets", "v4", credentials=self.creds, cache_discovery=False)

    def append_rows(self, spreadsheet_id: str, range_name: str, values: list[list]) -> None:
        logger.debug(
            "Appending %d rows to spreadsheet %s at range %s",
            len(values),
            spreadsheet_id,
            range_name,
        )
        body = {"values": values}
        try:
            self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body,
            ).execute()
        except Exception:
            logger.exception("Failed to append rows to Google Sheets")
            raise

    def ensure_sheet_exists(self, spreadsheet_id: str, sheet_name: str) -> None:
        logger.debug("Checking if sheet '%s' exists in spreadsheet %s", sheet_name, spreadsheet_id)
        spreadsheet = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = spreadsheet.get("sheets", [])
        for sheet in sheets:
            if sheet.get("properties", {}).get("title") == sheet_name:
                logger.debug("Sheet '%s' already exists.", sheet_name)
                return

        logger.info("Creating new sheet '%s' in spreadsheet %s", sheet_name, spreadsheet_id)
        body = {"requests": [{"addSheet": {"properties": {"title": sheet_name}}}]}
        try:
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body,
            ).execute()
            logger.info("Successfully created sheet '%s'.", sheet_name)
        except Exception as e:
            if "already exists" in str(e):
                logger.debug("Sheet '%s' was created by another process.", sheet_name)
            else:
                logger.exception("Failed to create sheet in Google Sheets")
                raise
