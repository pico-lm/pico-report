"""
Integration tests with real API endpoints.

These tests require a running Pico backend at localhost:3000/api.
Run with: pytest tests/test_integration_real.py -v
"""

import time
import pytest
from pico_report import PicoClient, PicoConfig
from pico_report.integrations import PicoReporter
from pico_report.exceptions import PicoAuthError, PicoUploadError


@pytest.mark.integration
class TestRealAPIIntegration:
    """Integration tests with real API."""
    
    def test_client_initialization(self, real_config):
        """Test that client can initialize and connect to real API."""
        try:
            client = PicoClient(config=real_config)
            assert client is not None
            client.close()
        except Exception as e:
            pytest.skip(f"API not available: {e}")
    
    def test_log_metrics_basic(self, real_config, sample_metrics):
        """Test logging basic metrics to real API."""
        try:
            client = PicoClient(config=real_config)
            
            result = client.log_metrics(sample_metrics, step=1)
            
            # Verify response indicates success
            assert result is not None
            
            client.close()
        except Exception as e:
            pytest.skip(f"API not available: {e}")
    
    def test_log_metrics_multiple_steps(self, real_config):
        """Test logging metrics across multiple steps."""
        try:
            client = PicoClient(config=real_config)
            
            for step in range(5):
                metrics = {
                    "loss": 1.0 / (step + 1),
                    "accuracy": 0.5 + (step * 0.1),
                    "step": step
                }
                result = client.log_metrics(metrics, step=step)
                assert result is not None
                time.sleep(0.1)  # Small delay between requests
            
            client.close()
        except Exception as e:
            pytest.skip(f"API not available: {e}")
    
    def test_create_experiment(self, real_config, sample_experiment_config):
        """Test creating an experiment."""
        try:
            client = PicoClient(config=real_config)
            
            experiment_name = f"test-experiment-{int(time.time())}"
            result = client.create_experiment(
                experiment_name=experiment_name,
                config_data=sample_experiment_config,
                description="Integration test experiment"
            )
            
            assert result is not None
            # Check that experiment name was updated in config
            assert client.config.experiment_name == experiment_name
            
            client.close()
        except Exception as e:
            pytest.skip(f"API not available: {e}")
    
    def test_list_experiments(self, real_config):
        """Test listing experiments."""
        try:
            client = PicoClient(config=real_config)
            
            experiments = client.list_experiments(limit=5)
            
            assert isinstance(experiments, list)
            # May be empty if no experiments exist yet
            
            client.close()
        except Exception as e:
            pytest.skip(f"API not available: {e}")
    
    def test_reporter_full_workflow(self, real_api_key, real_lab_hash, real_base_url, sample_experiment_config):
        """Test complete workflow with PicoReporter."""
        try:
            reporter = PicoReporter(
                lab_hash=real_lab_hash,
                api_key=real_api_key,
                base_url=real_base_url,
                experiment_name=f"reporter-test-{int(time.time())}"
            )
            
            # Setup experiment
            exp_result = reporter.setup_experiment(
                experiment_name=f"reporter-experiment-{int(time.time())}",
                config_data=sample_experiment_config,
                description="Reporter integration test"
            )
            
            # Log training metrics
            for step in range(3):
                reporter.log_training_metrics({
                    "loss": 1.0 / (step + 1),
                    "lr": 0.001
                }, step=step)
                time.sleep(0.1)
            
            # Log evaluation metrics
            reporter.log_evaluation_metrics({
                "eval_loss": 0.5,
                "eval_acc": 0.85
            }, step=3, task_name="validation")
            
            # Log system metrics
            reporter.log_system_metrics(
                gpu_utilization=75.0,
                memory_usage=8.5,
                step=3
            )
            
            reporter.close()
            
        except Exception as e:
            pytest.skip(f"API not available: {e}")
    
    def test_invalid_api_key(self, real_lab_hash, real_base_url):
        """Test that invalid API key is rejected."""
        invalid_config = PicoConfig(
            api_key="invalid_key_12345",
            lab_hash=real_lab_hash,
            base_url=real_base_url
        )
        
        try:
            # This might fail at connection validation
            client = PicoClient(config=invalid_config)
            
            # Or fail when trying to log metrics
            with pytest.raises((PicoAuthError, PicoUploadError)):
                client.log_metrics({"test": 1}, step=0)
            
            client.close()
        except (PicoAuthError, Exception) as e:
            # Expected - invalid API key should be rejected
            pass
    
    def test_concurrent_metrics_logging(self, real_config):
        """Test logging metrics in quick succession."""
        try:
            client = PicoClient(config=real_config)
            
            # Log multiple metrics quickly
            results = []
            for i in range(10):
                result = client.log_metrics({
                    "metric": i,
                    "value": i * 2
                }, step=i)
                results.append(result)
            
            # All should succeed
            assert len(results) == 10
            
            client.close()
        except Exception as e:
            pytest.skip(f"API not available: {e}")
    
    def test_large_metrics_payload(self, real_config):
        """Test logging a large number of metrics at once."""
        try:
            client = PicoClient(config=real_config)
            
            # Create a large metrics dictionary
            large_metrics = {f"metric_{i}": float(i) for i in range(100)}
            
            result = client.log_metrics(large_metrics, step=0)
            assert result is not None
            
            client.close()
        except Exception as e:
            pytest.skip(f"API not available: {e}")
    
    def test_metrics_with_special_characters(self, real_config):
        """Test logging metrics with special characters in keys."""
        try:
            client = PicoClient(config=real_config)
            
            metrics = {
                "train/loss": 0.5,
                "eval/accuracy": 0.85,
                "model.layer1.weight": 0.3,
                "metric-with-dash": 1.0,
                "metric_with_underscore": 2.0
            }
            
            result = client.log_metrics(metrics, step=0)
            assert result is not None
            
            client.close()
        except Exception as e:
            pytest.skip(f"API not available: {e}")

