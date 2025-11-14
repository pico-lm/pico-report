"""
Command-line interface for pico-report package.
"""

import json
import sys
from typing import Optional

import click
from .client import PicoClient
from .config import ReporterConfig
from .exceptions import PicoReportError
from .utils import setup_logging, validate_api_key


@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging')
def main(debug: bool):
    """Pico Report CLI - Upload training data to Pico backend."""
    setup_logging("DEBUG" if debug else "INFO")


@main.command()
@click.option('--api-key', required=True, help='Pico API key')
@click.option('--lab-hash', required=True, help='Lab hash')
@click.option('--base-url', default='https://api.picolm.io', help='Pico backend URL')
def validate(api_key: str, lab_hash: str, base_url: str):
    """Validate API key and connection to Pico backend."""
    if not validate_api_key(api_key):
        click.echo("❌ Invalid API key format", err=True)
        sys.exit(1)
    
    try:
        config = ReporterConfig(api_key=api_key, lab_hash=lab_hash, base_url=base_url)
        client = PicoClient(config=config)
        click.echo("✅ API key valid and connection successful")
    except PicoReportError as e:
        click.echo(f"❌ Validation failed: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--api-key', help='Pico API key (or use PICO_API_KEY env var)')
@click.option('--lab-hash', help='Lab hash (required - or use PICO_LAB_HASH env var)')
@click.option('--experiment-name', required=True, help='Experiment name')
@click.option('--description', help='Experiment description')
@click.option('--config-file', type=click.Path(exists=True), help='JSON config file')
def create_experiment(
    api_key: Optional[str],
    lab_hash: Optional[str], 
    experiment_name: str,
    description: Optional[str],
    config_file: Optional[str]
):
    """
    Create a new experiment in Pico backend.
    
    Requires PICO_API_KEY and PICO_LAB_HASH environment variables or --api-key and --lab-hash options.
    """
    try:
        config_kwargs = {}
        if api_key:
            config_kwargs['api_key'] = api_key
        if lab_hash:
            config_kwargs['lab_hash'] = lab_hash
            
        client = PicoClient(**config_kwargs)
        
        config_data = None
        if config_file:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
        
        response = client.create_experiment(
            experiment_name=experiment_name,
            config_data=config_data,
            description=description
        )
        
        click.echo(f"✅ Created experiment: {experiment_name}")
        click.echo(f"Experiment ID: {response.get('experiment_id', 'N/A')}")
        
    except PicoReportError as e:
        click.echo(f"❌ Failed to create experiment: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--api-key', help='Pico API key (or use PICO_API_KEY env var)')
@click.option('--lab-hash', help='Lab hash (required - or use PICO_LAB_HASH env var)')
@click.option('--limit', default=10, help='Number of experiments to list')
def list_experiments(api_key: Optional[str], lab_hash: Optional[str], limit: int):
    """
    List experiments in the current lab.
    
    Requires PICO_API_KEY and PICO_LAB_HASH environment variables or --api-key and --lab-hash options.
    """
    try:
        config_kwargs = {}
        if api_key:
            config_kwargs['api_key'] = api_key
        if lab_hash:
            config_kwargs['lab_hash'] = lab_hash
            
        client = PicoClient(**config_kwargs)
        experiments = client.list_experiments(limit=limit)
        
        if not experiments:
            click.echo("No experiments found")
            return
        
        click.echo(f"Found {len(experiments)} experiments:")
        for exp in experiments:
            click.echo(f"  - {exp.get('name', 'Unknown')} (ID: {exp.get('id', 'N/A')})")
            
    except PicoReportError as e:
        click.echo(f"❌ Failed to list experiments: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--api-key', help='Pico API key (or use PICO_API_KEY env var)')
@click.option('--lab-hash', help='Lab hash (required - or use PICO_LAB_HASH env var)')
@click.option('--experiment-name', help='Experiment name')
@click.option('--metrics-file', type=click.Path(exists=True), required=True, 
              help='JSON file containing metrics data')
@click.option('--step', type=int, help='Training step number')
def upload_metrics(
    api_key: Optional[str],
    lab_hash: Optional[str],
    experiment_name: Optional[str],
    metrics_file: str,
    step: Optional[int]
):
    """
    Upload metrics from JSON file.
    
    Requires PICO_API_KEY and PICO_LAB_HASH environment variables or --api-key and --lab-hash options.
    """
    try:
        config_kwargs = {}
        if api_key:
            config_kwargs['api_key'] = api_key
        if lab_hash:
            config_kwargs['lab_hash'] = lab_hash
        if experiment_name:
            config_kwargs['experiment_name'] = experiment_name
            
        client = PicoClient(**config_kwargs)
        
        with open(metrics_file, 'r') as f:
            data = json.load(f)
        
        metrics = data.get('metrics', data) 
        file_step = data.get('step') if 'step' in data else step
        file_experiment = data.get('experiment_name') if 'experiment_name' in data else experiment_name
        
        response = client.log_metrics(metrics, step=file_step)
        click.echo(f"✅ Uploaded {len(metrics)} metrics")
        
    except (PicoReportError, json.JSONDecodeError, FileNotFoundError) as e:
        click.echo(f"❌ Failed to upload metrics: {e}", err=True)
        sys.exit(1)


@main.command()
def version():
    """Show version information."""
    from . import __version__
    click.echo(f"pico-report version {__version__}")


if __name__ == '__main__':
    main()