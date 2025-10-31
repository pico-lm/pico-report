"""
Pytest configuration and fixtures for pico-report tests.
"""

import os
import pytest
from pico_report import ReporterConfig
from pico_report.client import PicoClient


@pytest.fixture
def mock_api_key():
    """Return a mock API key for testing."""
    return "pk_test_mock_api_key_12345"


@pytest.fixture
def mock_lab_hash():
    """Return a mock lab hash for testing."""
    return "test_lab_hash_abc"


@pytest.fixture
def real_api_key():
    """Return the real API key for integration tests from environment."""
    import os
    api_key = os.getenv("PICO_API_KEY")
    if not api_key:
        pytest.skip("PICO_API_KEY environment variable not set")
    return api_key


@pytest.fixture
def real_lab_hash():
    """Return the real lab hash for integration tests from environment."""
    import os
    lab_hash = os.getenv("PICO_LAB_HASH")
    if not lab_hash:
        pytest.skip("PICO_LAB_HASH environment variable not set")
    return lab_hash


@pytest.fixture
def real_base_url():
    """Return the real base URL for integration tests."""
    return "http://localhost:3000/api/report"


@pytest.fixture
def mock_config(mock_api_key, mock_lab_hash):
    """Return a mock ReporterConfig for testing."""
    return ReporterConfig(
        api_key=mock_api_key,
        lab_hash=mock_lab_hash,
        base_url="https://api.test.picolm.io"
    )


@pytest.fixture
def real_config(real_api_key, real_lab_hash, real_base_url):
    """Return a real ReporterConfig for integration testing."""
    return ReporterConfig(
        api_key=real_api_key,
        lab_hash=real_lab_hash,
        base_url=real_base_url,
        experiment_name="test-experiment"
    )


@pytest.fixture
def sample_metrics():
    """Return sample metrics for testing."""
    return {
        "loss": 0.5,
        "accuracy": 0.85,
        "learning_rate": 0.001,
        "epoch": 1
    }


@pytest.fixture
def sample_experiment_config():
    """Return sample experiment configuration."""
    return {
        "model": "transformer",
        "batch_size": 32,
        "learning_rate": 0.001,
        "num_epochs": 10
    }

