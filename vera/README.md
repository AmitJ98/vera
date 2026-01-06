# Vera Core Package (`vera`)

This directory contains the core engine of Vera, a plugin-based AI evaluation tool. This README is
intended for developers working on the Vera engine itself. For usage instructions or plugin
development, please refer to the [root README](README.md) and the [documentation](/docs).

## Package Structure

The `vera` package is organized into several key modules:

- **`vera.core`**: The heart of the engine.
    - `hook_specs.py`: Defines the `PluginService` protocol and all available hooks using `pluggy`.
    - `configuration.py`: Manages global configuration (`EveConfig`), including loading/saving to
      `config.yaml`.
    - `plugin_service.py`: Handles plugin discovery and registration using `PluginManager`.
    - `data_models/`: Pydantic models for test cases, inputs, outputs, and report rows.
    - `default_impl.py`: Provides default implementations for core hooks (e.g., LLM evaluation via
      Gemini).
- **`eve.eval`**: Logic for executing evaluation suites.
    - `evaluate.py`: The `EvaluationService` which manages the asynchronous execution of test cases
      and result publishing.
- **`eve.config`**: Implementation of the `eve config` CLI command.
- **`eve.create`**: Logic for the `eve create` command, including plugin scaffolding templates.
- **`eve.list`**: Implementation of the `eve list` CLI command.
- **`eve.main`**: The entry point for the Typer CLI application.

## Internal Mechanics

### Plugin System

Eve uses [pluggy](https://pluggy.readthedocs.io/) for its hook-based architecture.

- **Hook Specifications**: Defined in `eve.core.hook_specs.PluginService`.
- **Registration**: Plugins are discovered via `setuptools` entry points under the `eve` group. The
  `default_impl` is always registered first.
- **Hook Calling**: The `PluginCreation.plugin_service` (a `pluggy.HookCaller`) is used throughout
  the app to trigger hooks.

### Asynchronous Execution

The evaluation engine is built on `asyncio` and `anyio`.

- `EvaluationService.evaluate()` uses `asyncio.TaskGroup` to run test cases in parallel.
- Each test case execution is isolated and includes a configurable timeout.
- Hooks that interact with the LLM or external services are typically `async`.

## Development Guidelines

### Prerequisites

- Python 3.14+
- `uv` for dependency management.

### Setup

From the project root:

```bash
uv pip install -e ./eve
```

### Running Tests

Tests are located in `eve/tests`. We use `pytest` with `pytest-asyncio`.

```bash
# Run all core tests
export PYTHONPATH=$(pwd)/eve/src:$(pwd)/packages/eve_logger/src
python3 -m pytest eve/tests -p no:trio
```

*Note: Some tests may fail if the `trio` plugin is active due to conflict with `asyncio` loops,
hence `-p no:trio`.*

### Code Style

We use `ruff` for linting and formatting. Configuration is found in `eve/ruff.toml`.
We use `ty` for static type checking.

## CLI Design

The CLI is built with `typer`. Extra arguments not recognized by core commands are passed down to
plugins via hooks (`handle_eve_eval_extra_args`, etc.), allowing plugins to extend the CLI
seamlessly.
