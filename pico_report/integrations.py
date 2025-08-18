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
        project_id: Optional[str] = None,
        experiment_name: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize PicoReporter.
        
        Args:
            config: PicoConfig instance
            project_id: Project ID override
            experiment_name: Experiment name override
            **kwargs: Additional config parameters
        """
        config_kwargs = kwargs.copy()
        if project_id:
            config_kwargs['project_id'] = project_id
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
            prefix: Prefix to add to metric names
        """
        try:
            prefixed_metrics = {f"{prefix}/{k}": v for k, v in metrics.items()}
            self.client.log_metrics(prefixed_metrics, step=step)
            logger.debug(f"Logged {len(metrics)} training metrics at step {step}")
        except Exception as e:
            logger.error(f"Failed to log training metrics: {e}")
    
    def log_evaluation_metrics(
        self,
        metrics: Dict[str, Union[int, float]],
        step: int,
        task_name: str = "validation"
    ) -> None:
        """
        Log evaluation metrics.
        
        Args:
            metrics: Dictionary of metric names and values
            step: Training step number
            task_name: Name of the evaluation task
        """
        try:
            # Log as regular metrics with eval prefix
            prefixed_metrics = {f"eval/{task_name}/{k}": v for k, v in metrics.items()}
            self.client.log_metrics(prefixed_metrics, step=step)
            
            # Also upload as evaluation results for specialized handling
            self.client.upload_evaluation_results(
                evaluation_data=metrics,
                step=step,
                task_name=task_name
            )
            logger.debug(f"Logged evaluation metrics for {task_name} at step {step}")
        except Exception as e:
            logger.error(f"Failed to log evaluation metrics: {e}")
    
    def save_checkpoint_data(
        self,
        checkpoint_info: Dict[str, Any],
        step: int,
        checkpoint_type: str = "training"
    ) -> None:
        """
        Save checkpoint metadata and information.
        
        Args:
            checkpoint_info: Dictionary containing checkpoint information
            step: Training step number  
            checkpoint_type: Type of checkpoint
        """
        try:
            self.client.upload_checkpoint_data(
                checkpoint_data=checkpoint_info,
                step=step,
                checkpoint_type=checkpoint_type
            )
            logger.debug(f"Saved checkpoint data at step {step}")
        except Exception as e:
            logger.error(f"Failed to save checkpoint data: {e}")
    
    def save_learning_dynamics(
        self,
        dynamics_data: Dict[str, Any],
        step: int
    ) -> None:
        """
        Save learning dynamics data.
        
        Args:
            dynamics_data: Learning dynamics information
            step: Training step number
        """
        try:
            self.client.upload_learning_dynamics(
                dynamics_data=dynamics_data,
                step=step
            )
            logger.debug(f"Saved learning dynamics at step {step}")
        except Exception as e:
            logger.error(f"Failed to save learning dynamics: {e}")
    
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
        **kwargs: Configuration parameters
        
    Returns:
        PicoReporter instance
    """
    return PicoReporter(**kwargs)