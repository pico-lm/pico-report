"""
Configuration management for pico-report package.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

from .exceptions import PicoConfigError

# Load environment variables from .env file
load_dotenv()


class PicoConfig(BaseModel):
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
    timeout: Optional[int] = Field(
        default=30,
        description="Request timeout in seconds"
    )
    max_retries: Optional[int] = Field(
        default=3,
        description="Maximum number of retry attempts for failed requests"
    )
    
    @validator('api_key')
    def validate_api_key(cls, v):
        if not v or len(v.strip()) == 0:
            raise PicoConfigError("API key cannot be empty")
        return v.strip()
    
    @validator('base_url')
    def validate_base_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise PicoConfigError("Base URL must start with http:// or https://")
        return v.rstrip('/')

    @validator('lab_hash')
    def validate_lab_hash(cls, v):
        if not v or len(v.strip()) == 0:
            raise PicoConfigError("Lab hash is required and cannot be empty")
        return v.strip()
    
    @classmethod
    def from_env(cls, **kwargs) -> 'PicoConfig':
        """
        Create config from environment variables with optional overrides.
        
        Note: PICO_API_KEY and PICO_LAB_HASH environment variables are required.
        """
        env_config = {
            'api_key': os.getenv('PICO_API_KEY', ''),
            'base_url': os.getenv('PICO_BASE_URL', 'https://picolabs.space/api'),
            'lab_hash': os.getenv('PICO_LAB_HASH', ''),
            'experiment_name': os.getenv('PICO_EXPERIMENT_NAME'),
            'timeout': int(os.getenv('PICO_TIMEOUT', '30')),
            'max_retries': int(os.getenv('PICO_MAX_RETRIES', '3')),
        }
        
        # Override with provided kwargs
        env_config.update(kwargs)
        
        return cls(**env_config)