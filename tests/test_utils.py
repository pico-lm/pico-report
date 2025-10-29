"""
Unit tests for utility functions.
"""

import os
import json
import tempfile
import pytest
from pico_report.utils import (
    extract_checkpoint_metadata,
    format_metrics_for_logging,
    safe_json_serialize,
    validate_api_key,
    setup_logging
)


class TestExtractCheckpointMetadata:
    """Test checkpoint metadata extraction."""
    
    def test_nonexistent_path(self):
        """Test extracting metadata from nonexistent path."""
        metadata = extract_checkpoint_metadata("/path/that/does/not/exist")
        
        assert metadata["checkpoint_path"] == "/path/that/does/not/exist"
        assert metadata["exists"] is False
    
    def test_single_file_checkpoint(self):
        """Test extracting metadata from a single file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test checkpoint data")
            temp_path = f.name
        
        try:
            metadata = extract_checkpoint_metadata(temp_path)
            
            assert metadata["exists"] is True
            assert metadata["type"] == "file"
            assert metadata["size_bytes"] > 0
            assert "filename" in metadata
        finally:
            os.unlink(temp_path)
    
    def test_directory_checkpoint(self):
        """Test extracting metadata from a directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some files in the directory
            file1 = os.path.join(tmpdir, "model.bin")
            file2 = os.path.join(tmpdir, "config.json")
            
            with open(file1, "w") as f:
                f.write("model data" * 100)
            with open(file2, "w") as f:
                json.dump({"param": "value"}, f)
            
            metadata = extract_checkpoint_metadata(tmpdir)
            
            assert metadata["exists"] is True
            assert metadata["type"] == "directory"
            assert metadata["file_count"] == 2
            assert metadata["total_size_bytes"] > 0
            assert len(metadata["files"]) == 2


class TestFormatMetricsForLogging:
    """Test metrics formatting."""
    
    def test_basic_formatting(self):
        """Test basic metrics formatting."""
        metrics = {
            "loss": 0.5,
            "accuracy": 0.85,
            "epoch": 1
        }
        
        formatted = format_metrics_for_logging(metrics)
        
        assert formatted["loss"] == 0.5
        assert formatted["accuracy"] == 0.85
        assert formatted["epoch"] == 1.0  # Converted to float
    
    def test_with_prefix(self):
        """Test formatting with prefix."""
        metrics = {
            "loss": 0.5,
            "accuracy": 0.85
        }
        
        formatted = format_metrics_for_logging(metrics, prefix="train")
        
        assert "train/loss" in formatted
        assert "train/accuracy" in formatted
        assert formatted["train/loss"] == 0.5
    
    def test_skip_non_numeric(self):
        """Test that non-numeric values are skipped."""
        metrics = {
            "loss": 0.5,
            "name": "experiment",
            "status": "running",
            "count": 10
        }
        
        formatted = format_metrics_for_logging(metrics)
        
        assert "loss" in formatted
        assert "count" in formatted
        assert "name" not in formatted
        assert "status" not in formatted
    
    def test_empty_metrics(self):
        """Test formatting empty metrics."""
        formatted = format_metrics_for_logging({})
        
        assert formatted == {}


class TestSafeJsonSerialize:
    """Test safe JSON serialization."""
    
    def test_basic_dict(self):
        """Test serializing a basic dictionary."""
        obj = {"key": "value", "number": 42}
        result = safe_json_serialize(obj)
        
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["key"] == "value"
        assert parsed["number"] == 42
    
    def test_with_numpy_array(self):
        """Test serializing with numpy arrays."""
        try:
            import numpy as np
            obj = {"array": np.array([1, 2, 3])}
            result = safe_json_serialize(obj)
            
            parsed = json.loads(result)
            assert parsed["array"] == [1, 2, 3]
        except ImportError:
            pytest.skip("NumPy not installed")
    
    def test_custom_object(self):
        """Test serializing custom objects."""
        class CustomObj:
            def __init__(self):
                self.value = 42
        
        obj = {"custom": CustomObj()}
        result = safe_json_serialize(obj)
        
        # Should not raise, will convert to dict or string
        assert isinstance(result, str)
    
    def test_unserializable_fallback(self):
        """Test fallback for truly unserializable objects."""
        # Lambda functions are not JSON serializable
        obj = {"func": lambda x: x}
        result = safe_json_serialize(obj)
        
        # Should still produce a string (converted to string representation)
        assert isinstance(result, str)


class TestValidateApiKey:
    """Test API key validation."""
    
    def test_valid_key(self):
        """Test validating a valid API key."""
        assert validate_api_key("pk_Q69RoDCc4D9tJeATATGvBotCqUlt8IxJ") is True
    
    def test_another_valid_key(self):
        """Test another valid key format."""
        assert validate_api_key("test_api_key_12345678") is True
    
    def test_empty_key(self):
        """Test that empty key is invalid."""
        assert validate_api_key("") is False
    
    def test_none_key(self):
        """Test that None is invalid."""
        assert validate_api_key(None) is False
    
    def test_short_key(self):
        """Test that very short key is invalid."""
        assert validate_api_key("short") is False
    
    def test_whitespace_key(self):
        """Test that whitespace-only key is invalid."""
        assert validate_api_key("   ") is False
    
    def test_non_string_key(self):
        """Test that non-string key is invalid."""
        assert validate_api_key(12345) is False
        assert validate_api_key(["key"]) is False


class TestSetupLogging:
    """Test logging setup."""
    
    def test_setup_info_level(self):
        """Test setting up logging at INFO level."""
        setup_logging("INFO")
        
        import logging
        logger = logging.getLogger('pico_report')
        assert logger.level == logging.INFO
    
    def test_setup_debug_level(self):
        """Test setting up logging at DEBUG level."""
        setup_logging("DEBUG")
        
        import logging
        logger = logging.getLogger('pico_report')
        assert logger.level == logging.DEBUG
    
    def test_setup_warning_level(self):
        """Test setting up logging at WARNING level."""
        setup_logging("WARNING")
        
        import logging
        logger = logging.getLogger('pico_report')
        assert logger.level == logging.WARNING

