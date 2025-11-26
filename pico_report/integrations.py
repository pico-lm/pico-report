"""
Integration utilities for pico-report with existing training frameworks.
"""

from typing import Any, Dict, Optional, Union
import logging

from .client import PicoClient
from .config import ReporterConfig
from .exceptions import PicoReportError

logger = logging.getLogger(__name__)


class PicoReporter:
    """High-level interface for reporting training data to Pico backend."""
    
    def __init__(self, config: Optional[ReporterConfig] = None, **kwargs):
        """
        Initialize PicoReporter.
        
        Args:
            config: ReporterConfig instance (optional)
            **kwargs: Configuration parameters passed to PicoClient
                     Common parameters:
                     - api_key: API key (or use PICO_API_KEY env var)
                     - lab_hash: Lab hash (required, or use PICO_LAB_HASH env var)
                     - experiment_name: Experiment name (optional)
                     - base_url: Base URL (optional)
                     - auto_commit: Enable git commits (default: False)
            
        Note:
            If config is not provided, a new ReporterConfig will be created from
            kwargs and environment variables (PICO_API_KEY, PICO_LAB_HASH, etc.).
            
            Auto-commit can be controlled via the auto_commit kwarg or
            PICO_AUTO_COMMIT environment variable. When enabled, a git commit is
            created whenever setup_experiment is called, capturing the exact code
            state for each experiment.
        
        Examples:
            >>> reporter = PicoReporter(lab_hash="my_lab", auto_commit=True)
            >>> reporter = PicoReporter(config=my_config)
        """
        # Pass everything to PicoClient - it handles config creation
        self.client = PicoClient(config=config, **kwargs)
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
            
        Note:
            Auto-commit behavior is controlled by the config.auto_commit setting.
            When enabled, this will create a git commit before creating the experiment,
            capturing the exact code state. The commit SHA will be tracked with the
            experiment.
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
            error_str = str(e)
            # Check if this is a 409 "experiment already exists" error
            if "409" in error_str and "already exists" in error_str:
                logger.info(f"Experiment '{experiment_name}' already exists - continuing to log metrics to existing experiment")
                self._experiment_created = True
                return {}
            else:
                logger.warning(f"Failed to create experiment: {e}")
                # Continue without failing
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