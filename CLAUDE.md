# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`ghostfolio-py` is an unofficial Python REST API client for [Ghostfolio](https://ghostfol.io), a wealth management application. The library wraps Ghostfolio's HTTP API into a simple Python class.

## Commands

### Linting
```bash
# Run ruff linter
ruff check ghostfolio/

# Run ruff formatter
ruff format ghostfolio/

# Run pre-commit hooks on all files
pre-commit run --all-files
```

### Documentation
```bash
# Generate HTML docs locally (opens browser)
generate-docs --open

# Generate without opening browser
generate-docs
```

### Building & Publishing
```bash
# Build wheel and source distribution
uv build

# Install in editable mode for development
pip install -e .
```

## Architecture

The entire library is a single class `Ghostfolio` in `ghostfolio/__init__.py`.

### Authentication Flow
The client uses Ghostfolio's anonymous token auth. On first API call, `_refresh_jwt_token()` exchanges the access token for a short-lived JWT via `/api/v1/auth/anonymous/`. The JWT is cached and automatically refreshed after 30 days.

### Request Pipeline
All requests flow through:
1. `get()` / `post()` / `put()` — public methods that call `_url()` to build the endpoint
2. `_url()` — constructs URLs, selecting v1 or v2 API based on `api_version` param
3. `_process_response()` — central response handler that logs errors and returns parsed JSON

### API Coverage
- **Portfolio**: `performance()`, `holdings()`, `holding()`, `details()`, `investments()`, `dividends()`
- **Transactions**: `orders()`, `import_transactions()`
- **Accounts/Admin**: `accounts()`, `market_data_admin()`, `market_data()`, `asset_profiles()`

The `get()`/`post()`/`put()` methods are also public, allowing callers to hit any endpoint not yet wrapped.

## Linting Configuration

Ruff is configured in `pyproject.toml` with line length 120 and rule sets: E, W, DJ, F, I, UP, B, Q, PL. Pre-commit runs ruff with `--fix` on every commit.

## No Test Suite

There are currently no tests in this repository.
