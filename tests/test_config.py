"""
Unit tests for ReporterConfig.
"""

import os
import pytest
from pico_report import ReporterConfig
from pico_report.exceptions import PicoConfigError


class TestReporterConfig:
    """Test ReporterConfig class."""
    
    def test_valid_config(self, mock_api_key, mock_lab_hash):
        """Test creating a valid config."""
        config = ReporterConfig(
            api_key=mock_api_key,
            lab_hash=mock_lab_hash
        )
        
        assert config.api_key == mock_api_key
        assert config.lab_hash == mock_lab_hash
        assert config.base_url == "https://api.picolm.io"
        assert config.timeout == 30
        assert config.max_retries == 3
    
    def test_custom_base_url(self, mock_api_key, mock_lab_hash):
        """Test config with custom base URL."""
        custom_url = "http://localhost:3000/api"
        config = ReporterConfig(
            api_key=mock_api_key,
            lab_hash=mock_lab_hash,
            base_url=custom_url
        )
        
        assert config.base_url == custom_url
    
    def test_custom_timeout(self, mock_api_key, mock_lab_hash):
        """Test config with custom timeout."""
        config = ReporterConfig(
            api_key=mock_api_key,
            lab_hash=mock_lab_hash,
            timeout=60
        )
        
        assert config.timeout == 60
    
    def test_experiment_name(self, mock_api_key, mock_lab_hash):
        """Test config with experiment name."""
        config = ReporterConfig(
            api_key=mock_api_key,
            lab_hash=mock_lab_hash,
            experiment_name="my-experiment"
        )
        
        assert config.experiment_name == "my-experiment"
    
    def test_empty_api_key(self, mock_lab_hash):
        """Test that empty API key raises error."""
        with pytest.raises(PicoConfigError, match="API key cannot be empty"):
            ReporterConfig(api_key="", lab_hash=mock_lab_hash)
    
    def test_whitespace_api_key(self, mock_lab_hash):
        """Test that whitespace-only API key raises error."""
        with pytest.raises(PicoConfigError, match="API key cannot be empty"):
            ReporterConfig(api_key="   ", lab_hash=mock_lab_hash)
    
    def test_empty_lab_hash(self, mock_api_key):
        """Test that empty lab hash raises error."""
        with pytest.raises(PicoConfigError, match="Lab hash is required"):
            ReporterConfig(api_key=mock_api_key, lab_hash="")
    
    def test_whitespace_lab_hash(self, mock_api_key):
        """Test that whitespace-only lab hash raises error."""
        with pytest.raises(PicoConfigError, match="Lab hash is required"):
            ReporterConfig(api_key=mock_api_key, lab_hash="   ")
    
    def test_invalid_base_url(self, mock_api_key, mock_lab_hash):
        """Test that invalid base URL raises error."""
        with pytest.raises(PicoConfigError, match="Base URL must start with"):
            ReporterConfig(
                api_key=mock_api_key,
                lab_hash=mock_lab_hash,
                base_url="invalid-url"
            )
    
    def test_base_url_trailing_slash_removed(self, mock_api_key, mock_lab_hash):
        """Test that trailing slash is removed from base URL."""
        config = ReporterConfig(
            api_key=mock_api_key,
            lab_hash=mock_lab_hash,
            base_url="https://api.test.com/"
        )
        
        assert config.base_url == "https://api.test.com"
    
    def test_api_key_whitespace_trimmed(self, mock_lab_hash):
        """Test that API key whitespace is trimmed."""
        config = ReporterConfig(
            api_key="  test_key  ",
            lab_hash=mock_lab_hash
        )
        
        assert config.api_key == "test_key"
    
    def test_lab_hash_whitespace_trimmed(self, mock_api_key):
        """Test that lab hash whitespace is trimmed."""
        config = ReporterConfig(
            api_key=mock_api_key,
            lab_hash="  test_hash  "
        )
        
        assert config.lab_hash == "test_hash"
    
    def test_from_env_with_env_vars(self, monkeypatch, mock_api_key, mock_lab_hash):
        """Test creating config from environment variables."""
        monkeypatch.setenv("PICO_API_KEY", mock_api_key)
        monkeypatch.setenv("PICO_LAB_HASH", mock_lab_hash)
        monkeypatch.setenv("PICO_EXPERIMENT_NAME", "env-experiment")
        
        config = ReporterConfig.from_env()
        
        assert config.api_key == mock_api_key
        assert config.lab_hash == mock_lab_hash
        assert config.experiment_name == "env-experiment"
    
    def test_from_env_with_override(self, monkeypatch, mock_api_key, mock_lab_hash):
        """Test that kwargs override environment variables."""
        monkeypatch.setenv("PICO_API_KEY", "env_key")
        monkeypatch.setenv("PICO_LAB_HASH", "env_hash")
        
        config = ReporterConfig.from_env(
            api_key=mock_api_key,
            lab_hash=mock_lab_hash
        )
        
        assert config.api_key == mock_api_key
        assert config.lab_hash == mock_lab_hash
    
    def test_from_env_missing_required(self, monkeypatch):
        """Test that missing required env vars raises error."""
        monkeypatch.delenv("PICO_API_KEY", raising=False)
        monkeypatch.delenv("PICO_LAB_HASH", raising=False)
        
        with pytest.raises(PicoConfigError):
            ReporterConfig.from_env()

