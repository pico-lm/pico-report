"""
Unit tests for PicoClient with mocked HTTP requests.
"""

import json
import time
import pytest
from unittest.mock import Mock, patch
from pico_report import PicoClient, ReporterConfig
from pico_report.exceptions import PicoAuthError, PicoUploadError


class TestPicoClient:
    """Test PicoClient class with mocked requests."""
    
    @patch('pico_report.client.requests.Session')
    def test_client_initialization(self, mock_session_class, mock_config):
        """Test client initialization."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock the heartbeat response
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response
        
        client = PicoClient(config=mock_config)
        
        assert client.config == mock_config
        mock_session.get.assert_called_once()
    
    @patch('pico_report.client.requests.Session')
    def test_client_initialization_without_config(self, mock_session_class, mock_api_key, mock_lab_hash, monkeypatch):
        """Test client initialization from environment variables."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock the heartbeat response
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_session.get.return_value = mock_response
        
        monkeypatch.setenv("PICO_API_KEY", mock_api_key)
        monkeypatch.setenv("PICO_LAB_HASH", mock_lab_hash)
        
        client = PicoClient()
        
        assert client.config.api_key == mock_api_key
        assert client.config.lab_hash == mock_lab_hash
    
    @patch('pico_report.client.requests.Session')
    def test_connection_validation_failure(self, mock_session_class, mock_config):
        """Test that connection validation failure raises error."""
        from requests.exceptions import RequestException
        
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock failed heartbeat
        mock_session.get.side_effect = RequestException("Connection failed")
        
        with pytest.raises(PicoAuthError, match="Failed to connect"):
            PicoClient(config=mock_config)
    
    @patch('pico_report.client.requests.Session')
    def test_log_metrics(self, mock_session_class, mock_config, sample_metrics):
        """Test logging metrics."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock heartbeat
        heartbeat_response = Mock()
        heartbeat_response.raise_for_status = Mock()
        
        # Mock metrics response
        metrics_response = Mock()
        metrics_response.raise_for_status = Mock()
        metrics_response.content = b'{"status": "success"}'
        metrics_response.json.return_value = {"status": "success"}
        
        mock_session.get.return_value = heartbeat_response
        mock_session.request.return_value = metrics_response
        
        client = PicoClient(config=mock_config)
        result = client.log_metrics(sample_metrics, step=100)
        
        assert result["status"] == "success"
        
        # Verify the request was made
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[0][0] == "POST"
        assert "/metrics" in call_args[0][1]
        
        # Check payload
        payload = call_args[1]["json"]
        assert payload["metrics"] == sample_metrics
        assert payload["step"] == 100
        assert payload["lab_hash"] == mock_config.lab_hash
    
    @patch('pico_report.client.requests.Session')
    def test_log_metrics_with_timestamp(self, mock_session_class, mock_config, sample_metrics):
        """Test logging metrics with custom timestamp."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock responses
        heartbeat_response = Mock()
        heartbeat_response.raise_for_status = Mock()
        
        metrics_response = Mock()
        metrics_response.raise_for_status = Mock()
        metrics_response.content = b'{"status": "success"}'
        metrics_response.json.return_value = {"status": "success"}
        
        mock_session.get.return_value = heartbeat_response
        mock_session.request.return_value = metrics_response
        
        client = PicoClient(config=mock_config)
        custom_timestamp = 1234567890.0
        client.log_metrics(sample_metrics, step=100, timestamp=custom_timestamp)
        
        # Check timestamp in payload
        payload = mock_session.request.call_args[1]["json"]
        assert payload["timestamp"] == custom_timestamp
    
    @patch('pico_report.client.requests.Session')
    def test_create_experiment(self, mock_session_class, mock_config, sample_experiment_config):
        """Test creating an experiment."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock responses
        heartbeat_response = Mock()
        heartbeat_response.raise_for_status = Mock()
        
        experiment_response = Mock()
        experiment_response.raise_for_status = Mock()
        experiment_response.content = b'{"experiment_id": "exp_123"}'
        experiment_response.json.return_value = {"experiment_id": "exp_123"}
        
        mock_session.get.return_value = heartbeat_response
        mock_session.request.return_value = experiment_response
        
        client = PicoClient(config=mock_config)
        result = client.create_experiment(
            experiment_name="test-experiment",
            config_data=sample_experiment_config,
            description="Test experiment description"
        )
        
        assert result["experiment_id"] == "exp_123"
        assert client.config.experiment_name == "test-experiment"
        
        # Verify the request
        call_args = mock_session.request.call_args
        assert call_args[0][0] == "POST"
        assert "/experiments" in call_args[0][1]
        
        payload = call_args[1]["json"]
        assert payload["name"] == "test-experiment"
        assert payload["config"] == sample_experiment_config
        assert payload["description"] == "Test experiment description"
    
    @patch('pico_report.client.requests.Session')
    def test_list_experiments(self, mock_session_class, mock_config):
        """Test listing experiments."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock responses
        heartbeat_response = Mock()
        heartbeat_response.raise_for_status = Mock()
        
        experiments_response = Mock()
        experiments_response.raise_for_status = Mock()
        experiments_response.content = b'{"experiments": [{"id": "exp_1"}, {"id": "exp_2"}]}'
        experiments_response.json.return_value = {
            "experiments": [{"id": "exp_1"}, {"id": "exp_2"}]
        }
        
        mock_session.get.return_value = heartbeat_response
        mock_session.request.return_value = experiments_response
        
        client = PicoClient(config=mock_config)
        result = client.list_experiments(limit=10)
        
        assert len(result) == 2
        assert result[0]["id"] == "exp_1"
        assert result[1]["id"] == "exp_2"
    
    @patch('pico_report.client.requests.Session')
    def test_auth_error_401(self, mock_session_class, mock_config, sample_metrics):
        """Test that 401 response raises PicoAuthError."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock heartbeat success
        heartbeat_response = Mock()
        heartbeat_response.raise_for_status = Mock()
        mock_session.get.return_value = heartbeat_response
        
        # Mock 401 error
        from requests.exceptions import HTTPError
        metrics_response = Mock()
        metrics_response.status_code = 401
        metrics_response.raise_for_status.side_effect = HTTPError()
        mock_session.request.return_value = metrics_response
        
        client = PicoClient(config=mock_config)
        
        with pytest.raises(PicoAuthError, match="Invalid API key"):
            client.log_metrics(sample_metrics, step=100)
    
    @patch('pico_report.client.requests.Session')
    def test_rate_limit_error_429(self, mock_session_class, mock_config, sample_metrics):
        """Test that 429 response raises PicoUploadError about rate limiting."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock heartbeat success
        heartbeat_response = Mock()
        heartbeat_response.raise_for_status = Mock()
        mock_session.get.return_value = heartbeat_response
        
        # Mock 429 error
        from requests.exceptions import HTTPError
        metrics_response = Mock()
        metrics_response.status_code = 429
        metrics_response.raise_for_status.side_effect = HTTPError()
        mock_session.request.return_value = metrics_response
        
        client = PicoClient(config=mock_config)
        
        with pytest.raises(PicoUploadError, match="Rate limit exceeded"):
            client.log_metrics(sample_metrics, step=100)
    
    @patch('pico_report.client.requests.Session')
    def test_close(self, mock_session_class, mock_config):
        """Test closing the client session."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock heartbeat
        heartbeat_response = Mock()
        heartbeat_response.raise_for_status = Mock()
        mock_session.get.return_value = heartbeat_response
        
        client = PicoClient(config=mock_config)
        client.close()
        
        mock_session.close.assert_called_once()

