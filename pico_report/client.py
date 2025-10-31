"""
Main client for interacting with Pico backend API.
"""

import json
import os
import subprocess
import time
from typing import Any, Dict, List, Optional, Union, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import ReporterConfig
from .exceptions import PicoAuthError, PicoUploadError, PicoReportError, PicoGitError


class PicoClient:
    """Client for uploading data to Pico backend databases."""
    
    def __init__(self, config: Optional[ReporterConfig] = None, **kwargs):
        """
        Initialize PicoClient.
        
        Args:
            config: ReporterConfig instance. If None, will create from environment.
            **kwargs: Additional config parameters to override defaults.
            
        Note:
            Requires api_key and lab_hash to be provided either via config object,
            kwargs, or environment variables (PICO_API_KEY, PICO_LAB_HASH).
        """
        if config is None:
            config = ReporterConfig.from_env(**kwargs)
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
                f"{self.config.base_url}/heartbeat",
                timeout=self.config.timeout
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise PicoAuthError(f"Failed to connect to Pico backend: {e}")
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository."""
        try:
            subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise PicoGitError("Current directory is not a git repository")
    
    def _get_git_info(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Get current git commit SHA, branch, and status.
        
        Returns:
            Tuple of (commit_sha, branch, has_changes)
        """
        if not self._is_git_repo():
            return None, None, None
        
        try:
            # Get current commit SHA
            commit_sha = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                check=True,
                capture_output=True,
                text=True
            ).stdout.strip()
            
            # Get current branch
            branch = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                check=True,
                capture_output=True,
                text=True
            ).stdout.strip()
            
            # Check for uncommitted changes
            status = subprocess.run(
                ['git', 'status', '--porcelain'],
                check=True,
                capture_output=True,
                text=True
            ).stdout.strip()
            
            has_changes = bool(status)
            
            return commit_sha, branch, has_changes
            
        except subprocess.CalledProcessError:
            return None, None, None
    
    def _create_git_commit(self, experiment_name: str, config_data: Optional[Dict[str, Any]] = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Create a git commit for the experiment.
        
        Args:
            experiment_name: Name of the experiment
            config_data: Configuration data to save
            
        Returns:
            Tuple of (commit_sha, commit_message) or (None, None) if git operations fail
        """
        if not self._is_git_repo():
            return None, None
        
        try:
            # Check if there are changes to commit
            _, _, has_changes = self._get_git_info()
            
            if has_changes:
                # Stage all changes
                subprocess.run(
                    ['git', 'add', '-A'],
                    check=True,
                    capture_output=True
                )
                
                # Create commit message
                commit_message = f"Experiment: {experiment_name}"
                
                # Commit changes
                subprocess.run(
                    ['git', 'commit', '-m', commit_message],
                    check=True,
                    capture_output=True,
                    text=True
                )
                
                # Get the new commit SHA
                commit_sha = subprocess.run(
                    ['git', 'rev-parse', 'HEAD'],
                    check=True,
                    capture_output=True,
                    text=True
                ).stdout.strip()
                
                # Try to push the commit to remote
                try:
                    subprocess.run(
                        ['git', 'push'],
                        check=True,
                        capture_output=True,
                        timeout=30  # 30 second timeout for push
                    )
                    print(f"✓ Pushed commit {commit_sha[:7]} to remote repository")
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as push_error:
                    # Push failed, but commit was created locally
                    print(f"Warning: Failed to push commit to remote: {push_error}")
                    print("Commit created locally. You may need to push manually.")
                
                return commit_sha, commit_message
            else:
                # No changes, use current commit
                commit_sha, _, _ = self._get_git_info()
                return commit_sha, None
                
        except subprocess.CalledProcessError as e:
            # Git operations failed, but don't fail the experiment creation
            print(f"Warning: Git commit failed: {e}")
            return None, None
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Pico backend."""
        url = f"{self.config.base_url}{endpoint}"
        
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
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new experiment in Pico backend with automatic git tracking.
        
        This method will:
        1. Create a local git commit if there are changes (when auto_commit=True)
        2. Create the experiment in the Pico backend with git metadata
        3. The git commit SHA will be tracked with the experiment
        
        Args:
            experiment_name: Name of the experiment
            config_data: Training configuration data
            description: Optional experiment description
            
        Returns:
            Response from backend API containing experiment details
        """
        git_commit_sha = None
        git_commit_message = None
        git_branch = None
        
        # Create git commit if enabled and in a git repo
        if self.config.auto_commit:
            commit_sha, commit_msg = self._create_git_commit(experiment_name, config_data)
            if commit_sha:
                git_commit_sha = commit_sha
                git_commit_message = commit_msg or f"Experiment: {experiment_name}"
                # Get branch info
                _, branch, _ = self._get_git_info()
                git_branch = branch
        
        payload = {
            'name': experiment_name,
            'lab_hash': self.config.lab_hash,
            'config': config_data,
            'description': description,
            'timestamp': time.time(),
            'git_commit_sha': git_commit_sha,
            'git_commit_message': git_commit_message,
            'git_branch': git_branch
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