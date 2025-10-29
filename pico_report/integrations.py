"""
Integration utilities for pico-report with existing training frameworks.
"""

from typing import Any, Dict, Optional, Union
import logging

from .client import PicoClient
from .config import PicoConfig
from .exceptions import PicoReportError

logger = logging.getLogger(__name__)


class PicoReporter:
    """High-level interface for reporting training data to Pico backend."""
    
    def __init__(
        self, 
        config: Optional[PicoConfig] = None,
        lab_hash: Optional[str] = None,
        experiment_name: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize PicoReporter.
        
        Args:
            config: PicoConfig instance
            lab_hash: Lab hash (required - provide here or via PICO_LAB_HASH env var)
            experiment_name: Experiment name (optional)
            **kwargs: Additional config parameters (e.g., api_key, base_url)
            
        Note:
            If config is not provided, lab_hash and api_key must be provided either
            through arguments or environment variables (PICO_LAB_HASH, PICO_API_KEY).
        """
        config_kwargs = kwargs.copy()
        if lab_hash:
            config_kwargs['lab_hash'] = lab_hash
        if experiment_name:
            config_kwargs['experiment_name'] = experiment_name
            
        self.client = PicoClient(config=config, **config_kwargs)
        self._experiment_created = False
    
    def setup_experiment(
        self,
        experiment_name: str,
        config_data: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Setup a new experiment or connect to existing one.
        
        Args:
            experiment_name: Name of the experiment
            config_data: Training configuration data
            description: Optional experiment description
            
        Returns:
            Experiment details from backend
        """
        try:
            response = self.client.create_experiment(
                experiment_name=experiment_name,
                config_data=config_data,
                description=description
            )
            self._experiment_created = True
            logger.info(f"Created experiment: {experiment_name}")
            return response
        except Exception as e:
            logger.warning(f"Failed to create experiment: {e}")
            # Continue without failing - experiment might already exist
            return {}
    
    def _log_metrics(
        self,
        metrics: Dict[str, Union[int, float]],
        step: int,
        metric_type: str
    ) -> None:
        """
        Internal helper to log metrics with error handling.
        
        Args:
            metrics: Dictionary of formatted metric names and values
            step: Training step number
            metric_type: Type of metrics for logging purposes (e.g., "training", "evaluation", "analysis")
        """
        try:
            self.client.log_metrics(metrics, step=step)
            logger.debug(f"Logged {len(metrics)} {metric_type} metrics at step {step}")
        except Exception as e:
            logger.error(f"Failed to log {metric_type} metrics: {e}")
    
    def log_training_metrics(
        self,
        metrics: Dict[str, Union[int, float]],
        step: int,
        prefix: str = "train"
    ) -> None:
        """
        Log training metrics with optional prefix.
        
        Args:
            metrics: Dictionary of metric names and values
            step: Training step number
            prefix: Prefix to add to metric names (default: "train")
        """
        prefixed_metrics = {f"{prefix}/{k}": v for k, v in metrics.items()}
        self._log_metrics(prefixed_metrics, step, "training")
    
    def log_evaluation_metrics(
        self,
        metrics: Dict[str, Union[int, float]],
        step: int,
        prefix: str = "eval"
    ) -> None:
        """
        Log evaluation metrics with optional prefix. 
        NOTE: We could add some fancy handling if we want to store the evaluation results 
        in a separate table in the database.
        
        Args:
            metrics: Dictionary of metric names and values
            step: Training step number
            prefix: Prefix to add to metric names (default: "validation")
        """
        prefixed_metrics = {f"{prefix}/{k}": v for k, v in metrics.items()}
        self._log_metrics(prefixed_metrics, step, "evaluation")
    
    def log_analysis_metrics(
        self,
        metric_name: str,
        metric_data: Dict[str, float],
        step: int,
        data_split: str,
        prefix: str = "analysis"
    ) -> None:
        """
        Log learning dynamics analysis metrics.
        
        This method is specifically designed for logging metrics from pico-analyze,
        which often have per-layer values. The metrics are formatted to match the
        structure used in wandb logging.
        
        Args:
            metric_name: Name of the metric (e.g., "cka", "per", "gini")
            metric_data: Dictionary mapping layer names to metric values
                Example: {"model.0.attention.o_proj.weights": 0.85, ...}
            step: Training step number at which analysis was performed
            data_split: Data split used for analysis (e.g., "train", "val")
            prefix: Prefix to add to metric names (default: "analysis")
        
        Example:
            >>> reporter.log_analysis_metrics(
            ...     metric_name="cka",
            ...     metric_data={
            ...         "model.0.attention.o_proj.weights": 0.85,
            ...         "model.1.attention.o_proj.weights": 0.92
            ...     },
            ...     step=5000,
            ...     data_split="val"
            ... )
        """
        # Format metrics to match wandb structure: {prefix}/{metric_name}_{data_split}/{layer}
        formatted_metrics = {
            f"{prefix}/{metric_name}_{data_split}/{layer}": value
            for layer, value in metric_data.items()
        }
        self._log_metrics(formatted_metrics, step, "analysis")

    def log_system_metrics(
        self,
        gpu_utilization: Optional[float] = None,
        memory_usage: Optional[float] = None,
        step: Optional[int] = None,
        **additional_metrics
    ) -> None:
        """
        Log system performance metrics.
        
        Args:
            gpu_utilization: GPU utilization percentage
            memory_usage: Memory usage in GB
            step: Training step number
            **additional_metrics: Additional system metrics
        """
        try:
            system_metrics = {}
            if gpu_utilization is not None:
                system_metrics['system/gpu_utilization'] = gpu_utilization
            if memory_usage is not None:
                system_metrics['system/memory_usage_gb'] = memory_usage
            
            # Add any additional metrics with system prefix
            for key, value in additional_metrics.items():
                system_metrics[f'system/{key}'] = value
            
            if system_metrics:
                self.client.log_metrics(system_metrics, step=step)
                logger.debug(f"Logged system metrics at step {step}")
        except Exception as e:
            logger.error(f"Failed to log system metrics: {e}")
    
    def close(self) -> None:
        """Close the client connection."""
        if hasattr(self, 'client'):
            self.client.close()


def create_pico_reporter(**kwargs) -> PicoReporter:
    """
    Convenience function to create a PicoReporter instance.
    
    Args:
        **kwargs: Configuration parameters (must include lab_hash or set PICO_LAB_HASH env var)
        
    Returns:
        PicoReporter instance
        
    Note:
        Requires lab_hash and api_key to be provided either as arguments or 
        via environment variables (PICO_LAB_HASH, PICO_API_KEY).
    """
    return PicoReporter(**kwargs)