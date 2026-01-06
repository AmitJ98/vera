# Contributing to Vera

Thank you for your interest in contributing to Vera! We welcome contributions of all kinds,
including
bug fixes, new features, documentation improvements, and feedback.

## How to Contribute

### 1. Fork and Clone

Fork the repository on GitHub and clone it to your local machine.

### 2. Set Up Development Environment

We use `uv` for dependency management.

```bash
# Install dependencies
uv sync
```

### 3. Create a Branch

Create a new branch for your changes.

```bash
git checkout -b feature/my-new-feature
```

### 4. Make Your Changes

Implement your changes, following the existing code style.

### 5. Add Tests

Add tests for any new functionality or bug fixes.

### 6. Run Tests

Ensure all tests pass before submitting your PR.

```bash
# Run core tests
uv run pytest vera/tests

# Run built-in plugin tests
uv run pytest builting_plugins/google_sheets_report/tests
```

### 7. Submit a Pull Request

Push your branch to your fork and submit a PR to the main repository.

## Plugin Development

If you are developing a new plugin, please refer to
the [Plugin Development Guide](docs/plugin_development.md).

## Code Style

- Use `ruff` for linting and formatting.
- Follow PEP 8 guidelines.
- Use type hints for all function signatures.

## Communication

If you have questions or want to discuss a new feature, please open an issue on GitHub.
