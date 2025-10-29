# Testing Guide

## Quick Start

```bash
# Install dependencies
poetry install

# Run all unit tests (no API required)
poetry run pytest tests/ -m "not integration" -v

# Run integration tests (requires API + credentials)
poetry run pytest tests/test_integration_real.py -v
```

## Test Suite Overview

- **57 unit tests** - Run without API (mocked)
- **10 integration tests** - Run against real API (note you need the pico-labs-app running locally)
- **Coverage**: Config, Client, Reporter, Utils, Real API

## 🧪 Running Tests

### Unit Tests (No API Required)
```bash
poetry run pytest tests/ -m "not integration"
```

### Integration Tests (Requires API)
```bash
# 1. Set up credentials (see below)
# 2. Start your API at http://localhost:3000
# 3. Run tests
poetry run pytest tests/test_integration_real.py -v
```

### Specific Test Files
```bash
poetry run pytest tests/test_config.py -v      # Configuration tests
poetry run pytest tests/test_client.py -v      # Client tests
poetry run pytest tests/test_utils.py -v       # Utility tests
```

Note the structure of texts: 

```
tests/
├── conftest.py              # Shared fixtures
├── test_config.py          # Configuration (15 tests)
├── test_client.py          # HTTP client (10 tests)
├── test_integrations.py    # High-level API (12 tests)
├── test_utils.py           # Utilities (15 tests)
└── test_integration_real.py # Real API (10 tests)
```

### Setup for Integration Tests

Integration tests need real API credentials:

```bash
# 1. Copy example file
cp .env.example .env

# 2. Update .env with real credentials

# PICO_API_KEY=your_actual_api_key
# PICO_LAB_HASH=your_actual_lab_hash
# PICO_BASE_URL=http://localhost:3000/api/report
```

