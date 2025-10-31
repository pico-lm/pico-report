# Pico Report

A Python package for uploading training metrics and checkpointing data to Pico backend databases. This package allows you to seamlessly integrate with your existing training pipelines while sending data to your private Pico dashboard.

## Installation

```bash
pip install pico-report
```

## Quick Start

First, set up your environment variables (recommended) or use direct configuration.

### Setup Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your actual credentials (NEVER commit this file!)
# PICO_API_KEY=your_actual_api_key
# PICO_LAB_HASH=your_actual_lab_hash
```

### Using the Client

```python
from pico_report import PicoClient, ReporterConfig

# Method 1: Using environment variables (recommended - secure)
client = PicoClient()

# Method 2: Direct configuration (not recommended for production)
config = ReporterConfig(
    api_key="your-api-key",  # Required
    lab_hash="your-lab-hash",  # Required
    experiment_name="experiment-1"  # Optional
)
client = PicoClient(config=config)

# Log training metrics
client.log_metrics({
    "loss": 0.5,
    "accuracy": 0.85,
    "learning_rate": 0.001
}, step=100)

# Upload checkpoint data
client.upload_checkpoint_data({
    "model_state": "path/to/checkpoint",
    "optimizer_state": "path/to/optimizer",
    "epoch": 5
}, step=100)
```

## Configuration

### Environment Variables

Set the following **required** environment variables:

```bash
export PICO_API_KEY="your-api-key"
export PICO_LAB_HASH="your-lab-hash"
```

Optional configuration:

```bash
# Automatically create git commits for each experiment (default: false)
export PICO_AUTO_COMMIT="true"

# Experiment name (if not provided programmatically)
export PICO_EXPERIMENT_NAME="my-experiment"
```

### Configuration File

Create a `.env` file in your project root:

```env
# Required
PICO_API_KEY=your-api-key
PICO_LAB_HASH=your-lab-hash

# Optional
PICO_EXPERIMENT_NAME=my-experiment
PICO_AUTO_COMMIT=true
```

### Git Integration & Auto-Commit

Pico Report can automatically create Git commits when you create experiments, allowing you to track the exact code state used for each run.

#### Enabling Auto-Commit

```python
from pico_report.integrations import PicoReporter

# Method 1: Via environment variable
# Set PICO_AUTO_COMMIT=true in your .env file

# Method 2: Via configuration
reporter = PicoReporter(
    lab_hash="my-lab-hash",
    auto_commit=True  # Enable automatic git commits
)

# Setup experiment - will auto-commit if enabled
reporter.setup_experiment(
    experiment_name="my-experiment",
    config_data={"lr": 0.001}
)
# Git commit created automatically with message: "Experiment: my-experiment"
# Commit is pushed to your remote repository (if configured)
```

#### Requirements for Auto-Commit

- Your code must be in a Git repository
- Git must be installed and available in PATH
- For automatic push: Git remote must be configured with authentication

#### What Gets Committed

When auto-commit is enabled:
1. All modified and new files are staged (`git add -A`)
2. A commit is created with message: `"Experiment: {experiment_name}"`
3. The commit SHA is linked to your experiment in the dashboard
4. The commit is automatically pushed to your remote repository
5. You can view code diffs between experiments in the Pico Labs UI

#### Disabling Auto-Commit

```python
# Disable for specific reporter
reporter = PicoReporter(
    lab_hash="my-lab-hash",
    auto_commit=False  # Disable automatic commits
)

# Or set environment variable
# PICO_AUTO_COMMIT=false
```

## High-Level Interface

For easier integration, use the `PicoReporter` class:

```python
from pico_report.integrations import PicoReporter

# lab_hash is required - provide it explicitly or via PICO_LAB_HASH environment variable
reporter = PicoReporter(
    lab_hash="my-lab-hash",  # Required
    experiment_name="transformer-training",  # Optional
    auto_commit=True  # Optional: enable automatic git commits (default: False)
)

# Setup experiment (auto-commits if enabled)
reporter.setup_experiment(
    experiment_name="transformer-training",
    config_data={"lr": 0.001, "batch_size": 32},
    description="Training transformer model"
)
# If auto_commit=True, a git commit is automatically created and pushed

# Log training metrics
reporter.log_training_metrics({
    "loss": 0.5,
    "perplexity": 2.1
}, step=100)

# Log evaluation metrics
reporter.log_evaluation_metrics({
    "eval_loss": 0.45,
    "eval_accuracy": 0.87
}, step=100, prefix="validation")
```

## Integration with Existing Training Code

### PyTorch Lightning Integration

```python
import lightning as L
from pico_report.integrations import PicoReporter

class MyLightningModule(L.LightningModule):
    def __init__(self):
        super().__init__()
        # Requires PICO_API_KEY and PICO_LAB_HASH environment variables to be set
        self.pico_reporter = PicoReporter(
            experiment_name="lightning-training",
            auto_commit=True  # Track code changes automatically
        )
    
    def training_step(self, batch, batch_idx):
        # Your training logic
        loss = self.compute_loss(batch)
        
        # Log to Pico
        if self.global_step % 10 == 0:
            self.pico_reporter.log_training_metrics({
                "train_loss": loss.item()
            }, step=self.global_step)
        
        return loss
    
    def validation_step(self, batch, batch_idx):
        # Your validation logic
        val_loss = self.compute_loss(batch)
        return {"val_loss": val_loss}
    
    def validation_epoch_end(self, outputs):
        avg_loss = torch.stack([x["val_loss"] for x in outputs]).mean()
        
        self.pico_reporter.log_evaluation_metrics({
            "val_loss": avg_loss.item()
        }, step=self.global_step)
```

### Direct Integration with Pico-Train

You can modify your existing pico-train setup to also send data to Pico backend:

```python
# In your training script
from pico_report.integrations import PicoReporter

# Initialize both wandb and pico reporter
wandb_logger = initialize_wandb(monitoring_config, checkpointing_config)
pico_reporter = PicoReporter(
    lab_hash=monitoring_config.pico.lab_hash,
    experiment_name=checkpointing_config.run_name,
    auto_commit=True  # Automatically commit experiment code
)

# In your training loop
for step, batch in enumerate(dataloader):
    # ... training logic ...
    
    # Log to both wandb and pico
    metrics = {"loss": loss.item(), "lr": lr}
    wandb_logger.log(metrics, step=step)
    pico_reporter.log_training_metrics(metrics, step=step)
```

## Configuration

The base URL should point to the report API endpoint. For local development:
```bash
export PICO_BASE_URL="http://localhost:3000/api/report"
```

For production:
```bash
export PICO_BASE_URL="https://picolabs.space/api/report"
```

## API Reference

### PicoClient

Main client for direct API interaction.

#### Methods

- `log_metrics(metrics, step, timestamp)`: Log training metrics
- `create_experiment(name, config_data, description)`: Create new experiment
- `list_experiments(limit, offset)`: List existing experiments

### PicoReporter

High-level interface for easier integration.

#### Methods

- `setup_experiment(name, config_data, description)`: Setup experiment
- `log_training_metrics(metrics, step, prefix)`: Log training metrics with prefix
- `log_evaluation_metrics(metrics, step, prefix)`: Log evaluation metrics with prefix
- `log_analysis_metrics(metric_name, metric_data, step, data_split, prefix)`: Log learning dynamics analysis metrics
- `log_system_metrics(**metrics)`: Log system performance metrics

## Error Handling

The package includes custom exceptions:

- `PicoReportError`: Base exception
- `PicoAuthError`: Authentication related errors
- `PicoUploadError`: Data upload errors
- `PicoConfigError`: Configuration errors
- `PicoGitError`: Git operations errors (when using auto-commit)

```python
from pico_report.exceptions import PicoAuthError, PicoUploadError, PicoGitError

try:
    client.log_metrics(metrics, step=100)
except PicoAuthError:
    print("Authentication failed - check your API key")
except PicoUploadError as e:
    print(f"Upload failed: {e}")
except PicoGitError as e:
    print(f"Git operation failed: {e}")
    print("Note: Experiment was created, but git commit failed")
```