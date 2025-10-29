"""
Unit tests for PicoReporter integration class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pico_report.integrations import PicoReporter, create_pico_reporter


class TestPicoReporter:
    """Test PicoReporter class."""
    
    @patch('pico_report.integrations.PicoClient')
    def test_reporter_initialization(self, mock_client_class, mock_api_key, mock_lab_hash):
        """Test reporter initialization."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        reporter = PicoReporter(
            lab_hash=mock_lab_hash,
            api_key=mock_api_key,
            experiment_name="test-exp"
        )
        
        assert reporter.client == mock_client
        assert reporter._experiment_created is False
    
    @patch('pico_report.integrations.PicoClient')
    def test_setup_experiment(self, mock_client_class, mock_api_key, mock_lab_hash, sample_experiment_config):
        """Test setting up an experiment."""
        mock_client = Mock()
        mock_client.create_experiment.return_value = {"experiment_id": "exp_123"}
        mock_client_class.return_value = mock_client
        
        reporter = PicoReporter(lab_hash=mock_lab_hash, api_key=mock_api_key)
        result = reporter.setup_experiment(
            experiment_name="test-exp",
            config_data=sample_experiment_config,
            description="Test description"
        )
        
        assert result["experiment_id"] == "exp_123"
        assert reporter._experiment_created is True
        
        mock_client.create_experiment.assert_called_once_with(
            experiment_name="test-exp",
            config_data=sample_experiment_config,
            description="Test description"
        )
    
    @patch('pico_report.integrations.PicoClient')
    def test_setup_experiment_failure(self, mock_client_class, mock_api_key, mock_lab_hash):
        """Test that experiment setup failure is handled gracefully."""
        mock_client = Mock()
        mock_client.create_experiment.side_effect = Exception("Network error")
        mock_client_class.return_value = mock_client
        
        reporter = PicoReporter(lab_hash=mock_lab_hash, api_key=mock_api_key)
        
        # Should not raise, just return empty dict
        result = reporter.setup_experiment(experiment_name="test-exp")
        
        assert result == {}
        assert reporter._experiment_created is False
    
    @patch('pico_report.integrations.PicoClient')
    def test_log_training_metrics(self, mock_client_class, mock_api_key, mock_lab_hash, sample_metrics):
        """Test logging training metrics."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        reporter = PicoReporter(lab_hash=mock_lab_hash, api_key=mock_api_key)
        reporter.log_training_metrics(sample_metrics, step=100)
        
        # Verify metrics were prefixed with "train/"
        mock_client.log_metrics.assert_called_once()
        logged_metrics = mock_client.log_metrics.call_args[0][0]
        
        for key in sample_metrics.keys():
            assert f"train/{key}" in logged_metrics
    
    @patch('pico_report.integrations.PicoClient')
    def test_log_training_metrics_custom_prefix(self, mock_client_class, mock_api_key, mock_lab_hash, sample_metrics):
        """Test logging training metrics with custom prefix."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        reporter = PicoReporter(lab_hash=mock_lab_hash, api_key=mock_api_key)
        reporter.log_training_metrics(sample_metrics, step=100, prefix="custom")
        
        logged_metrics = mock_client.log_metrics.call_args[0][0]
        
        for key in sample_metrics.keys():
            assert f"custom/{key}" in logged_metrics
    
    @patch('pico_report.integrations.PicoClient')
    def test_log_evaluation_metrics(self, mock_client_class, mock_api_key, mock_lab_hash, sample_metrics):
        """Test logging evaluation metrics."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        reporter = PicoReporter(lab_hash=mock_lab_hash, api_key=mock_api_key)
        reporter.log_evaluation_metrics(sample_metrics, step=100, task_name="test")
        
        # Should call both log_metrics and upload_evaluation_results
        assert mock_client.log_metrics.called
        
        logged_metrics = mock_client.log_metrics.call_args[0][0]
        for key in sample_metrics.keys():
            assert f"eval/test/{key}" in logged_metrics
    
    @patch('pico_report.integrations.PicoClient')
    def test_log_system_metrics(self, mock_client_class, mock_api_key, mock_lab_hash):
        """Test logging system metrics."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        reporter = PicoReporter(lab_hash=mock_lab_hash, api_key=mock_api_key)
        reporter.log_system_metrics(
            gpu_utilization=75.5,
            memory_usage=8.2,
            step=100,
            cpu_usage=45.0
        )
        
        mock_client.log_metrics.assert_called_once()
        logged_metrics = mock_client.log_metrics.call_args[0][0]
        
        assert "system/gpu_utilization" in logged_metrics
        assert logged_metrics["system/gpu_utilization"] == 75.5
        assert "system/memory_usage_gb" in logged_metrics
        assert logged_metrics["system/memory_usage_gb"] == 8.2
        assert "system/cpu_usage" in logged_metrics
        assert logged_metrics["system/cpu_usage"] == 45.0
    
    @patch('pico_report.integrations.PicoClient')
    def test_log_system_metrics_partial(self, mock_client_class, mock_api_key, mock_lab_hash):
        """Test logging partial system metrics."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        reporter = PicoReporter(lab_hash=mock_lab_hash, api_key=mock_api_key)
        reporter.log_system_metrics(gpu_utilization=75.5, step=100)
        
        logged_metrics = mock_client.log_metrics.call_args[0][0]
        
        assert "system/gpu_utilization" in logged_metrics
        assert "system/memory_usage_gb" not in logged_metrics
    
    @patch('pico_report.integrations.PicoClient')
    def test_close(self, mock_client_class, mock_api_key, mock_lab_hash):
        """Test closing the reporter."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        reporter = PicoReporter(lab_hash=mock_lab_hash, api_key=mock_api_key)
        reporter.close()
        
        mock_client.close.assert_called_once()
    
    @patch('pico_report.integrations.PicoClient')
    def test_create_pico_reporter_function(self, mock_client_class, mock_api_key, mock_lab_hash):
        """Test the convenience function for creating a reporter."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        reporter = create_pico_reporter(
            lab_hash=mock_lab_hash,
            api_key=mock_api_key,
            experiment_name="test-exp"
        )
        
        assert isinstance(reporter, PicoReporter)
        assert reporter.client == mock_client
    
    @patch('pico_report.integrations.PicoClient')
    def test_error_handling_log_training_metrics(self, mock_client_class, mock_api_key, mock_lab_hash, sample_metrics):
        """Test that errors in log_training_metrics are caught and logged."""
        mock_client = Mock()
        mock_client.log_metrics.side_effect = Exception("Network error")
        mock_client_class.return_value = mock_client
        
        reporter = PicoReporter(lab_hash=mock_lab_hash, api_key=mock_api_key)
        
        # Should not raise, error should be caught
        reporter.log_training_metrics(sample_metrics, step=100)
    
    @patch('pico_report.integrations.PicoClient')
    def test_error_handling_log_system_metrics(self, mock_client_class, mock_api_key, mock_lab_hash):
        """Test that errors in log_system_metrics are caught and logged."""
        mock_client = Mock()
        mock_client.log_metrics.side_effect = Exception("Network error")
        mock_client_class.return_value = mock_client
        
        reporter = PicoReporter(lab_hash=mock_lab_hash, api_key=mock_api_key)
        
        # Should not raise, error should be caught
        reporter.log_system_metrics(gpu_utilization=75.5, step=100)

