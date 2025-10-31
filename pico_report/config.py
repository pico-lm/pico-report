"""
Configuration management for pico-report package.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

from .exceptions import PicoConfigError

# Load environment variables from .env file
load_dotenv()


class ReporterConfig(BaseModel):
    """Configuration for Pico backend integration."""
    
    api_key: str = Field(..., description="API key for Pico backend authentication")
    base_url: str = Field(
        default="https://api.picolm.io",
        description="Base URL for Pico backend API"
    )
    lab_hash: str = Field(
        description="Lab hash for organizing experiments"
    )
    experiment_name: Optional[str] = Field(
        default=None,
        description="Name of the current experiment"
    )
    auto_commit: bool = Field(
        default=False,
        description="Automatically create git commits when creating experiments"
    )
    timeout: Optional[int] = Field(
        default=30,
        description="Request timeout in seconds"
    )
    max_retries: Optional[int] = Field(
        default=3,
        description="Maximum number of retry attempts for failed requests"
    )
    
    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v):
        if not v or len(v.strip()) == 0:
            raise PicoConfigError("API key cannot be empty")
        return v.strip()
    
    @field_validator('base_url')
    @classmethod
    def validate_base_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise PicoConfigError("Base URL must start with http:// or https://")
        return v.rstrip('/')

    @field_validator('lab_hash')
    @classmethod
    def validate_lab_hash(cls, v):
        if not v or len(v.strip()) == 0:
            raise PicoConfigError("Lab hash is required and cannot be empty")
        return v.strip()
    
    @classmethod
    def from_env(cls, **kwargs) -> 'ReporterConfig':
        """
        Create config from environment variables with optional overrides.
        
        Environment variables:
        - PICO_API_KEY (required): API key for authentication
        - PICO_LAB_HASH (required): Lab hash for organizing experiments
        - PICO_BASE_URL (optional): Base URL for Pico backend API
        - PICO_EXPERIMENT_NAME (optional): Default experiment name
        - PICO_AUTO_COMMIT (optional): Enable automatic git commits (true/false)
        - PICO_TIMEOUT (optional): Request timeout in seconds
        - PICO_MAX_RETRIES (optional): Maximum retry attempts
        """
        env_config = {
            'api_key': os.getenv('PICO_API_KEY', ''),
            'base_url': os.getenv('PICO_BASE_URL', 'https://picolabs.space/api/report'),
            'lab_hash': os.getenv('PICO_LAB_HASH', ''),
            'experiment_name': os.getenv('PICO_EXPERIMENT_NAME'),
            'auto_commit': os.getenv('PICO_AUTO_COMMIT', 'false').lower() in ('true', '1', 'yes'),
            'timeout': int(os.getenv('PICO_TIMEOUT', '30')),
            'max_retries': int(os.getenv('PICO_MAX_RETRIES', '3')),
        }
        
        # Override with provided kwargs
        env_config.update(kwargs)
        
        return cls(**env_config)