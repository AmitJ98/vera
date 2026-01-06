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

import datetime as dt
import json
import logging
from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    from collections.abc import MutableMapping

__all__: list[str] = ["LogFormatter"]

_LOG_RECORD_BUILTIN_ATTRS: frozenset[str] = frozenset((
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
))


class LogFormatter(logging.Formatter):
    def __init__(self, *, fmt_keys: dict[str, str] | None = None) -> None:
        super().__init__()
        self.fmt_keys: dict[str, str] = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        message: dict = self._prepare_log_dict(record)
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord) -> dict[str, str]:
        always_fields: dict[str, str] = {
            "message": record.getMessage(),
            "level": record.levelname,
            "timestamp": dt.datetime.fromtimestamp(record.created, dt.UTC).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        return self._get_message(always_fields, record)

    def _get_message(
        self,
        always_fields: MutableMapping[str, str],
        record: logging.LogRecord,
    ) -> dict[str, str]:
        # The log message will contain all always_fields + the keys received in the
        # config + all key values received in extra kw.
        message: dict[str, str] = {
            key: (
                msg_val
                if (msg_val := always_fields.pop(val, None)) is not None
                else getattr(record, val)
            )
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        message.update({
            key: val for key, val in vars(record).items() if key not in _LOG_RECORD_BUILTIN_ATTRS
        })

        return message
