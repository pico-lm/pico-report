"""
Main client for interacting with Pico backend API.
"""

import json
import time
from typing import Any, Dict, List, Optional, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import PicoConfig
from .exceptions import PicoAuthError, PicoUploadError, PicoReportError


class PicoClient:
    """Client for uploading data to Pico backend databases."""
    
    def __init__(self, config: Optional[PicoConfig] = None, **kwargs):
        """
        Initialize PicoClient.
        
        Args:
            config: PicoConfig instance. If None, will create from environment.
            **kwargs: Additional config parameters to override defaults.
        """
        if config is None:
            config = PicoConfig.from_env(**kwargs)
        self.config = config
        
        self.session = requests.Session()
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.session.headers.update({
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'pico-report/1.0.0'
        })
        
        self._validate_connection()
    
    def _validate_connection(self) -> None:
        """Validate API key and connection to backend."""
        try:
            response = self.session.get(
                f"{self.config.base_url}/v1/heartbeat",
                timeout=self.config.timeout
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise PicoAuthError(f"Failed to connect to Pico backend: {e}")
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Pico backend."""
        url = f"{self.config.base_url}/report{endpoint}"
        
        try:
            if files:
                # Remove Content-Type header for file uploads
                headers = {k: v for k, v in self.session.headers.items() 
                          if k.lower() != 'content-type'}
                response = self.session.request(
                    method, url, json=data, files=files, 
                    timeout=self.config.timeout, headers=headers
                )
            else:
                response = self.session.request(
                    method, url, json=data, timeout=self.config.timeout
                )
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise PicoAuthError("Invalid API key or authentication failed")
            elif response.status_code == 429:
                raise PicoUploadError("Rate limit exceeded. Please retry later.")
            else:
                raise PicoUploadError(f"HTTP {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            raise PicoUploadError(f"Request failed: {e}")
    
    def log_metrics(
        self, 
        metrics: Dict[str, Union[int, float]], 
        step: Optional[int] = None,
        timestamp: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Log training metrics to Pico backend.
        
        Args:
            metrics: Dictionary of metric names and values
            step: Training step number
            timestamp: Unix timestamp (defaults to current time)
            
        Returns:
            Response from backend API
        """
        if timestamp is None:
            timestamp = time.time()
            
        payload = {
            'metrics': metrics,
            'step': step,
            'timestamp': timestamp,
            'lab_hash': self.config.lab_hash,
            'experiment_name': self.config.experiment_name
        }
        
        return self._make_request('POST', '/metrics', data=payload)
    
    
    def create_experiment(
        self,
        experiment_name: str,
        config_data: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new experiment in Pico backend.
        
        Args:
            experiment_name: Name of the experiment
            config_data: Training configuration data
            description: Optional experiment description
            
        Returns:
            Response from backend API containing experiment details
        """
        payload = {
            'name': experiment_name,
            'lab_hash': self.config.lab_hash,
            'config': config_data,
            'description': description,
            'timestamp': time.time()
        }
        
        response = self._make_request('POST', '/experiments', data=payload)
        
        # Update config with new experiment name
        self.config.experiment_name = experiment_name
        
        return response
    
    def list_experiments(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List experiments in the current lab.
        
        Args:
            limit: Maximum number of experiments to return
            offset: Number of experiments to skip
            
        Returns:
            List of experiment dictionaries
        """
        params = {
            'lab_hash': self.config.lab_hash,
            'limit': limit,
            'offset': offset
        }
        
        response = self._make_request('GET', '/experiments', data=params)
        return response.get('experiments', [])
    
    def close(self) -> None:
        """Close the HTTP session."""
        if hasattr(self, 'session'):
            self.session.close()