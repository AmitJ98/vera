# Vera Core Package (`vera`)

> ⚠️ **NOTICE: Internal Developer Documentation**
>
> This README is intended for contributors working on the **Vera Core Engine** itself.
>
> *   If you want to **use** Vera, please see the [Main README](../README.md) and [Installation Guide](../docs/installation_and_usage.md).
> *   If you want to **write a plugin**, please see the [Plugin Development Guide](../docs/plugin_development.md).

This directory contains the core engine of **Vera**, a plugin-based AI evaluation tool.

## Package Structure

The `vera` package is organized into several key modules:

- **`vera.core`**: The heart of the engine.
    - `hook_specs.py`: Defines the `PluginService` protocol and all available hooks using `pluggy`.
    - `configuration.py`: Manages global configuration (`VeraConfig`), including loading/saving to
      `config.yaml`.
    - `plugin_service.py`: Handles plugin discovery and registration using `PluginManager`.
    - `data_models/`: Pydantic models for test cases, inputs, outputs, and report rows.
    - `default_impl.py`: Provides default implementations for core hooks (e.g., LLM evaluation via
      Gemini).
- **`vera.vtest`**: Logic for executing evaluation suites.
    - `vtest.py`: The `TestingService` which manages the asynchronous execution of test cases
      and result publishing.
- **`vera.config`**: Implementation of the `vera config` CLI command.
- **`vera.create`**: Logic for the `vera create` command, including plugin scaffolding templates.
- **`vera.list`**: Implementation of the `vera list` CLI command.
- **`vera.main`**: The entry point for the Typer CLI application.

## Internal Mechanics

### Plugin System

Vera uses [pluggy](https://pluggy.readthedocs.io/) for its hook-based architecture.

- **Hook Specifications**: Defined in `vera.core.hook_specs.PluginService`.
- **Registration**: Plugins are discovered via `setuptools` entry points under the `vera` group. The
  `default_impl` is always registered first.
- **Hook Calling**: The `PluginCreation.plugin_service` (a `pluggy.HookCaller`) is used throughout
  the app to trigger hooks.

### Asynchronous Execution

The evaluation engine is built on `asyncio` and `anyio`.

- `TestingService.run_tests()` uses `asyncio.TaskGroup` to run test cases in parallel.
- Each test case execution is isolated and includes a configurable timeout.
- Hooks that interact with the LLM or external services are typically `async`.

## Development Guidelines

### Prerequisites

- **Python 3.14+**
- `uv` for dependency management.

### Setup

From the project root:

```bash
uv pip install vera
```

### Running Tests

Tests are located in `vera/tests`. We use `pytest` with `pytest-asyncio`.

```bash
# Run all core tests
cd vera
uv sync
source .venv/bin/activate
pytest tests
```

### Code Style

We use `ruff` for linting and formatting. Configuration is found in `ruff.toml`.
We use `ty` for static type checking.

## CLI Design

The CLI is built with `typer`. Extra arguments not recognized by core commands are passed down to
plugins via hooks (`handle_test_command_extra_args`, etc.), allowing plugins to extend the CLI
seamlessly.
