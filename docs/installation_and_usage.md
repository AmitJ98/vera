# Installation and Usage

This guide covers how to set up **Vera** and use its command-line interface efficiently.

## Prerequisites

- **Python 3.14+**
- **[uv](https://github.com/astral-sh/uv)** (Recommended for fast package management)
- A **Gemini API Key** (for the default LLM Judge)

## Project Structure

If you are working with the source repository, it helps to understand the layout:

- **`vera/`**: The core engine package.
- **`builtin_plugins/`**: Official plugins maintained by the Vera team (e.g., Google Sheets integration).
- **`plugin_example/`**: Reference implementations for learning (e.g., SQL Query Assistant).
- **`docs/`**: Documentation files.

## Installation & Setup

### 1. Create a Virtual Environment

We recommend using `uv` for a fast and reliable environment setup.

```shell
# Create a virtual environment with Python 3.14
uv venv --python 3.14
source .venv/bin/activate
```

### 2. Install Vera

Install the Vera engine. If you are developing Vera itself, use editable mode (`-e`).

```shell
# Standard install
uv pip install vera

# OR Editable install (for contributors)
uv pip install -e vera
```

### 3. Install a Plugin

Vera relies on plugins to test specific features. You can install the provided **SQL Query Assistant** example to get started.

```shell
uv pip install plugin_example/vera_sql_query_assistant
```

## Quick Start

Follow these steps to run your first test:

1. **Configure your API Key**:

   ```shell
   vera config -k
   ```
   *(You will be prompted to enter your Gemini API key securely)*

2. **Verify Plugin Installation**:

   ```shell
   vera list
   ```
   You should see `vera_sql_query_assistant` in the output list.

3. **Run Evaluation**:

   ```shell
   # Run the test and save results to the './out' directory
   vera test --dst-dir ./out --runs-count 1
   ```

## CLI Reference

### `vera list`

Lists all registered plugins currently installed and recognized by the system. This helps verify that your custom feature plugins are correctly loaded.

### `vera test`

The core command. Evaluates installed features using the registered plugins.

**Options:**

- `-t, --test-tag TEXT`: Only run tests that match the specified tags. Can be used multiple times to filter the test suite.
- `-d, --dst-dir PATH`: The destination directory for CSV report files. Defaults to the configured path or current directory.
- `-r, --runs-count INTEGER`: Execute the full test suite multiple times. Essential for measuring the consistency/variance of LLM responses. Defaults to 1.
- `--create-csv / --no-create-csv`: Enable or disable the default CSV report generation.
- `-v, --verbose`: Enable verbose output (DEBUG logs, file paths, and more details).
- `-q, --quiet`: Suppress standard output; only print error logs.

### `vera config`

Persistently configures Vera's default settings. Settings are stored in `config.yaml` within the user's config directory.

**Options:**

- `-d, --dst-dir PATH`: Set the default destination directory for all future runs.
- `-k, --gemini-api-key TEXT`: Securely set the Gemini API key.
- `--disable-csv / --enable-csv`: Toggle the default behavior for CSV report generation.
- `-l, --log-level TEXT`: Set the default logging level (e.g., `DEBUG`, `INFO`, `WARNING`).

### `vera create`

Scaffolds a new plugin template to help you start developing your own evaluations quickly.

**Options:**

- `--name TEXT` (Required): The name of your new feature/plugin (e.g., "my_new_feature").
- `--description TEXT`: A short description of what the plugin tests.
- `--plugins-dir PATH`: The directory where the plugin structure will be created. Defaults to `./vera_plugins`.
- `--override-existing`: Forcefully overwrite an existing directory if it exists.