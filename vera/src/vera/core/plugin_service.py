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
from typing import TYPE_CHECKING, NamedTuple, cast

from pluggy import PluginManager

import vera

from . import default_impl, hook_specs
from .configuration import CONFIG

if TYPE_CHECKING:
    from .hook_specs import PluginService

logger: logging.Logger = logging.getLogger(vera.PROJECT_NAME)


class PluginCreation(NamedTuple):
    plugin_service: PluginService
    registered_plugin_names: list[str]


_cached_service: PluginCreation | None = None


def create_service() -> PluginCreation:
    global _cached_service  # noqa: PLW0603
    if _cached_service is not None:
        return _cached_service

    logger.debug("Initializing PluginManager for project: %s", vera.PROJECT_NAME)
    pm: PluginManager = PluginManager(vera.PROJECT_NAME)
    pm.add_hookspecs(hook_specs.PluginService)
    logger.debug("Loading setuptools entrypoints for: %s", vera.PROJECT_NAME)
    pm.load_setuptools_entrypoints(vera.PROJECT_NAME)
    logger.debug("Registering default implementation")
    pm.register(default_impl)

    logger.debug("Updating configuration")
    pm.hook.update_configuration(config=CONFIG)

    registered_plugin_names: list[str] = _get_registered_plugin_names(pm)
    logger.debug("Registered plugins: %s", registered_plugin_names)

    _cached_service = PluginCreation(cast("PluginService", pm.hook), registered_plugin_names)
    return _cached_service


def _get_registered_plugin_names(pm: PluginManager) -> list[str]:
    return [p[0] for p in pm.list_name_plugin()]
