# Pico Report

A Python package for uploading training metrics and checkpointing data to Pico backend databases. This package allows you to seamlessly integrate with your existing training pipelines while sending data to your private Pico dashboard.

## Installation

```bash
pip install pico-report
```

## Quick Start

```python
from pico_report import PicoClient, PicoConfig

# Method 1: Using environment variables
client = PicoClient()

# Method 2: Direct configuration
config = PicoConfig(
    api_key="your-api-key",
    project_id="your-project-id",
    experiment_name="experiment-1"
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

Set the following environment variables:

```bash
export PICO_API_KEY="your-api-key"
```

### Configuration File

Create a `.env` file in your project root:

```env
PICO_API_KEY=your-api-key
PICO_PROJECT_ID=your-project-id
PICO_EXPERIMENT_NAME=my-experiment
```

## High-Level Interface

For easier integration, use the `PicoReporter` class:

```python
from pico_report.integrations import PicoReporter

reporter = PicoReporter(
    project_id="my-project",
    experiment_name="transformer-training"
)

# Setup experiment
reporter.setup_experiment(
    experiment_name="transformer-training",
    config_data={"lr": 0.001, "batch_size": 32},
    description="Training transformer model"
)

# Log training metrics
reporter.log_training_metrics({
    "loss": 0.5,
    "perplexity": 2.1
}, step=100)

# Log evaluation metrics
reporter.log_evaluation_metrics({
    "eval_loss": 0.45,
    "eval_accuracy": 0.87
}, step=100, task_name="validation")

# Save checkpoint information
reporter.save_checkpoint_data({
    "checkpoint_path": "/path/to/checkpoint",
    "model_size_mb": 450,
    "training_time_hours": 2.5
}, step=100)
```

## Integration with Existing Training Code

### PyTorch Lightning Integration

```python
import lightning as L
from pico_report.integrations import PicoReporter

class MyLightningModule(L.LightningModule):
    def __init__(self):
        super().__init__()
        self.pico_reporter = PicoReporter(
            experiment_name="lightning-training"
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
    project_id=monitoring_config.pico.project_id,
    experiment_name=checkpointing_config.run_name
)

# In your training loop
for step, batch in enumerate(dataloader):
    # ... training logic ...
    
    # Log to both wandb and pico
    metrics = {"loss": loss.item(), "lr": lr}
    wandb_logger.log(metrics, step=step)
    pico_reporter.log_training_metrics(metrics, step=step)
    
    # Save checkpoint data to pico
    if step % save_every == 0:
        checkpoint_info = extract_checkpoint_metadata(checkpoint_path)
        pico_reporter.save_checkpoint_data(checkpoint_info, step=step)
```

## API Reference

### PicoClient

Main client for direct API interaction.

#### Methods

- `log_metrics(metrics, step, timestamp)`: Log training metrics
- `upload_checkpoint_data(checkpoint_data, step, checkpoint_type)`: Upload checkpoint information  
- `upload_learning_dynamics(dynamics_data, step)`: Upload learning dynamics data
- `upload_evaluation_results(evaluation_data, step, task_name)`: Upload evaluation results
- `create_experiment(name, config_data, description)`: Create new experiment
- `list_experiments(limit, offset)`: List existing experiments

### PicoReporter

High-level interface for easier integration.

#### Methods

- `setup_experiment(name, config_data, description)`: Setup experiment
- `log_training_metrics(metrics, step, prefix)`: Log training metrics with prefix
- `log_evaluation_metrics(metrics, step, task_name)`: Log evaluation metrics
- `save_checkpoint_data(checkpoint_info, step, checkpoint_type)`: Save checkpoint data
- `save_learning_dynamics(dynamics_data, step)`: Save learning dynamics
- `log_system_metrics(**metrics)`: Log system performance metrics

## Error Handling

The package includes custom exceptions:

- `PicoReportError`: Base exception
- `PicoAuthError`: Authentication related errors
- `PicoUploadError`: Data upload errors
- `PicoConfigError`: Configuration errors

```python
from pico_report.exceptions import PicoAuthError, PicoUploadError

try:
    client.log_metrics(metrics, step=100)
except PicoAuthError:
    print("Authentication failed - check your API key")
except PicoUploadError as e:
    print(f"Upload failed: {e}")
```

## Development

### Setup Development Environment

```bash
git clone <repository>
cd pico-report
poetry install
poetry run pytest
```

## License

Apache 2.0