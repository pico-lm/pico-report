# Pico Report Tests

This directory contains comprehensive tests for the pico-report package.

## Test Structure

- `conftest.py` - Pytest fixtures and configuration
- `test_config.py` - Unit tests for PicoConfig
- `test_client.py` - Unit tests for PicoClient (mocked)
- `test_integrations.py` - Unit tests for PicoReporter
- `test_utils.py` - Unit tests for utility functions
- `test_integration_real.py` - Integration tests with real API

## Running Tests

### Run all unit tests (no API required)
```bash
pytest tests/ -v
```

### Run only unit tests (exclude integration tests)
```bash
pytest tests/ -v -m "not integration"
```

### Run integration tests (requires running API)
```bash
pytest tests/ -v -m integration
```

### Run specific test file
```bash
pytest tests/test_config.py -v
```

### Run with coverage
```bash
pytest tests/ --cov=pico_report --cov-report=html
```

## Integration Tests

Integration tests require a running Pico backend API at `localhost:3000/api`.

Before running integration tests:

1. **Set up your credentials:**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your actual credentials
   # PICO_API_KEY=your_actual_api_key
   # PICO_LAB_HASH=your_actual_lab_hash
   # PICO_BASE_URL=http://localhost:3000/api/report
   ```

2. **Start your Pico backend server**

3. **Ensure the API is accessible at `http://localhost:3000/api/report`**

Alternatively, export environment variables directly:
```bash
export PICO_API_KEY=your_actual_api_key
export PICO_LAB_HASH=your_actual_lab_hash
export PICO_BASE_URL=http://localhost:3000/api/report
```

## Test Coverage

The test suite covers:

- ✅ Configuration validation and environment variable loading
- ✅ Client initialization and connection handling
- ✅ Metrics logging functionality
- ✅ Experiment creation and management
- ✅ Error handling (auth errors, upload errors, network errors)
- ✅ PicoReporter high-level interface
- ✅ Utility functions (checkpoint metadata, JSON serialization, etc.)
- ✅ Real API integration tests

## CI/CD Integration

To run tests in CI/CD:

```bash
# Install dependencies
pip install -e ".[dev]"

# Run unit tests only (no API required)
pytest tests/ -v -m "not integration"
```

For integration testing in CI, you'll need to:
1. Start the Pico backend as a service
2. Pass the API credentials as environment variables
3. Run integration tests with `-m integration`

