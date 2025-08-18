"""
Utility functions for pico-report package.
"""

import json
import os
import sys
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


def extract_checkpoint_metadata(checkpoint_path: str) -> Dict[str, Any]:
    """
    Extract metadata from a checkpoint directory or file.
    
    Args:
        checkpoint_path: Path to checkpoint directory or file
        
    Returns:
        Dictionary containing checkpoint metadata
    """
    metadata = {
        'checkpoint_path': checkpoint_path,
        'exists': os.path.exists(checkpoint_path)
    }
    
    if not metadata['exists']:
        return metadata
    
    try:
        if os.path.isdir(checkpoint_path):
            # Directory checkpoint - get file list and sizes
            files = []
            total_size = 0
            
            for root, dirs, filenames in os.walk(checkpoint_path):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    try:
                        file_size = os.path.getsize(file_path)
                        rel_path = os.path.relpath(file_path, checkpoint_path)
                        files.append({
                            'name': rel_path,
                            'size_bytes': file_size
                        })
                        total_size += file_size
                    except OSError:
                        continue
            
            metadata.update({
                'type': 'directory',
                'files': files,
                'total_size_bytes': total_size,
                'file_count': len(files)
            })
        else:
            # Single file checkpoint
            file_size = os.path.getsize(checkpoint_path)
            metadata.update({
                'type': 'file',
                'size_bytes': file_size,
                'filename': os.path.basename(checkpoint_path)
            })
            
    except Exception as e:
        logger.warning(f"Failed to extract checkpoint metadata: {e}")
        metadata['error'] = str(e)
    
    return metadata


def get_system_info() -> Dict[str, Any]:
    """
    Get system information for logging.
    
    Returns:
        Dictionary containing system information
    """
    import platform
    import psutil
    
    info = {
        'platform': platform.platform(),
        'python_version': sys.version,
        'cpu_count': psutil.cpu_count(),
        'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2)
    }
    
    try:
        import torch
        info['torch_version'] = torch.__version__
        info['cuda_available'] = torch.cuda.is_available()
        if torch.cuda.is_available():
            info['cuda_version'] = torch.version.cuda
            info['gpu_count'] = torch.cuda.device_count()
            if torch.cuda.device_count() > 0:
                info['gpu_name'] = torch.cuda.get_device_name(0)
    except ImportError:
        pass
    
    return info


def format_metrics_for_logging(
    metrics: Dict[str, Any],
    step: Optional[int] = None,
    prefix: Optional[str] = None
) -> Dict[str, Any]:
    """
    Format metrics dictionary for consistent logging.
    
    Args:
        metrics: Raw metrics dictionary
        step: Optional step number
        prefix: Optional prefix for metric names
        
    Returns:
        Formatted metrics dictionary
    """
    formatted = {}
    
    for key, value in metrics.items():
        # Skip non-numeric values
        if not isinstance(value, (int, float)):
            continue
            
        # Apply prefix if provided
        formatted_key = f"{prefix}/{key}" if prefix else key
        formatted[formatted_key] = float(value)
    
    return formatted


def safe_json_serialize(obj: Any) -> str:
    """
    Safely serialize object to JSON, handling numpy arrays and other types.
    
    Args:
        obj: Object to serialize
        
    Returns:
        JSON string
    """
    def default_serializer(o):
        if hasattr(o, 'tolist'):  # numpy arrays
            return o.tolist()
        elif hasattr(o, '__dict__'):  # custom objects
            return o.__dict__
        else:
            return str(o)
    
    try:
        return json.dumps(obj, default=default_serializer, indent=2)
    except Exception as e:
        logger.warning(f"Failed to serialize object: {e}")
        return json.dumps({'error': f'Serialization failed: {str(e)}'})


def validate_api_key(api_key: str) -> bool:
    """
    Validate API key format.
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Basic validation - adjust based on your API key format
    api_key = api_key.strip()
    if len(api_key) < 10:  # Minimum length check
        return False
    
    # Add more specific validation based on your API key format
    # e.g., starts with specific prefix, contains only certain characters, etc.
    
    return True


def setup_logging(level: str = "INFO") -> None:
    """
    Setup logging for pico-report package.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set pico-report logger level
    logger = logging.getLogger('pico_report')
    logger.setLevel(getattr(logging, level.upper()))