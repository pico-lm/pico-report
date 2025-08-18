import os
import time
import random
import numpy as np
from pico_report.integrations import PicoReporter

os.environ['PICO_API_KEY'] = 'pk_jGdg3EKlwBRkqQ4Vsn3I8MpY6KnSbZem'
os.environ['PICO_BASE_URL'] = 'http://localhost:3000/api'

def test_basic_metrics():
    print("🧪 Testing basic metrics upload...")
    
    try:
        reporter = PicoReporter(experiment_name='python-test-experiment')
        
        reporter.log_training_metrics({
            'loss': 0.45,
            'accuracy': 0.87,
            'learning_rate': 0.001,
            'batch_size': 32
        }, step=150)
        
        print("✅ Basic metrics uploaded successfully!")
        
    except Exception as e:
        print(f"❌ Basic metrics test failed: {e}")

def test_evaluation_metrics():
    print("\n🧪 Testing evaluation metrics upload...")
    
    try:
        reporter = PicoReporter(experiment_name='python-test-experiment')
        
        reporter.log_evaluation_metrics({
            'val_loss': 0.42,
            'val_accuracy': 0.89,
            'f1_score': 0.86,
            'precision': 0.88,
            'recall': 0.84
        }, step=150, task_name='validation')
        
        print("✅ Evaluation metrics uploaded successfully!")
        
    except Exception as e:
        print(f"❌ Evaluation metrics test failed: {e}")

def test_system_metrics():
    print("\n🧪 Testing system metrics upload...")
    
    try:
        reporter = PicoReporter(experiment_name='python-test-experiment')
        
        # Upload system metrics
        reporter.log_system_metrics(
            gpu_utilization=85.5,
            memory_usage=12.3,
            cpu_usage=45.2,
            temperature=72.5,
            step=150
        )
        
        print("✅ System metrics uploaded successfully!")
        
    except Exception as e:
        print(f"❌ System metrics test failed: {e}")

def test_checkpoint_data():
    print("\n🧪 Testing checkpoint data upload...")
    
    try:
        reporter = PicoReporter(experiment_name='python-test-experiment')
        
        reporter.save_checkpoint_data({
            'checkpoint_path': '/path/to/model/checkpoint_150.pt',
            'model_size_mb': 235.7,
            'optimizer_state': 'saved',
            'epoch': 5,
            'best_val_loss': 0.42,
            'training_time_hours': 3.2
        }, step=150)
        
        print("✅ Checkpoint data uploaded successfully!")
        
    except Exception as e:
        print(f"❌ Checkpoint data test failed: {e}")

def test_learning_dynamics():
    print("\n🧪 Testing learning dynamics upload...")
    
    try:
        reporter = PicoReporter(experiment_name='python-test-experiment')
        
        reporter.save_learning_dynamics({
            'gradient_norm': 2.34,
            'weight_norm': 15.67,
            'layer_activations': {
                'layer_1': 0.85,
                'layer_2': 0.92,
                'layer_3': 0.78
            },
            'loss_landscape': {
                'sharpness': 0.023,
                'flatness': 0.87
            }
        }, step=150)
        
        print("✅ Learning dynamics uploaded successfully!")
        
    except Exception as e:
        print(f"❌ Learning dynamics test failed: {e}")

def test_multiple_steps():
    print("\n🧪 Testing multiple training steps...")
    
    try:
        reporter = PicoReporter(experiment_name='multi-step-test')
        

        for step in range(200, 205):
            loss = 1.0 - (step - 200) * 0.1 + random.uniform(-0.05, 0.05)
            accuracy = 0.7 + (step - 200) * 0.02 + random.uniform(-0.01, 0.01)
            
            reporter.log_training_metrics({
                'loss': round(loss, 4),
                'accuracy': round(accuracy, 4),
                'learning_rate': 0.001 * (0.95 ** ((step - 200) // 2)),
                'epoch': (step - 200) + 1
            }, step=step)
            
            time.sleep(0.1)  # Small delay to avoid overwhelming the API
        
        print("✅ Multiple steps uploaded successfully!")
        
    except Exception as e:
        print(f"❌ Multiple steps test failed: {e}")

def test_experiment_setup():
    print("\n🧪 Testing experiment setup...")
    
    try:
        reporter = PicoReporter()
        
        response = reporter.setup_experiment(
            experiment_name='configured-experiment',
            config_data={
                'model_type': 'transformer',
                'learning_rate': 0.001,
                'batch_size': 32,
                'num_epochs': 10,
                'dataset': 'custom_dataset_v1'
            },
            description='Test experiment with full configuration'
        )
        
        print("✅ Experiment setup completed successfully!")
        print(f"   Response: {response}")
        
    except Exception as e:
        print(f"❌ Experiment setup test failed: {e}")

def test_realistic_training_run():
    """Test a realistic training run with 50 steps and realistic progression"""
    print("\n🧪 Testing realistic training run...")
    
    try:
        reporter = PicoReporter(experiment_name='realistic-training-run')
        
        # Simulate realistic training progression
        base_loss = 2.5
        base_accuracy = 0.15
        
        for step in range(1, 51):
            # Realistic loss decay with noise
            epoch = (step - 1) // 10 + 1
            progress = (step - 1) % 10 / 10.0
            
            # Loss decreases exponentially with some plateaus
            loss = base_loss * np.exp(-epoch * 0.3) * (1 - progress * 0.2)
            loss += random.uniform(-0.1, 0.1)  # Add noise
            
            # Accuracy increases with diminishing returns
            accuracy = base_accuracy + (1 - base_accuracy) * (1 - np.exp(-epoch * 0.4))
            accuracy += random.uniform(-0.02, 0.02)  # Add noise
            
            # Learning rate scheduling
            lr = 0.001 * (0.95 ** (epoch - 1))
            
            # Log training metrics
            reporter.log_training_metrics({
                'loss': round(max(0.01, loss), 4),
                'accuracy': round(min(0.99, accuracy), 4),
                'learning_rate': round(lr, 6),
                'epoch': epoch,
                'step': step
            }, step=step)
            
            # Log validation metrics every 5 steps
            if step % 5 == 0:
                val_loss = loss * (1 + random.uniform(0.1, 0.3))  # Validation loss is typically higher
                val_accuracy = accuracy * (1 - random.uniform(0.05, 0.15))  # Validation accuracy is typically lower
                
                reporter.log_evaluation_metrics({
                    'val_loss': round(max(0.01, val_loss), 4),
                    'val_accuracy': round(min(0.99, val_accuracy), 4),
                    'f1_score': round(accuracy * 0.95 + random.uniform(-0.02, 0.02), 4),
                    'precision': round(accuracy * 0.97 + random.uniform(-0.02, 0.02), 4),
                    'recall': round(accuracy * 0.93 + random.uniform(-0.02, 0.02), 4)
                }, step=step, task_name='validation')
            
            # Log system metrics every 10 steps
            if step % 10 == 0:
                reporter.log_system_metrics(
                    gpu_utilization=random.uniform(70, 95),
                    memory_usage=random.uniform(8, 16),
                    cpu_usage=random.uniform(30, 60),
                    temperature=random.uniform(65, 80),
                    step=step
                )
            
            time.sleep(0.05)  # Small delay
        
        print("✅ Realistic training run completed successfully!")
        
    except Exception as e:
        print(f"❌ Realistic training run failed: {e}")

def test_multiple_experiments():
    """Test multiple experiments with different configurations for comparison"""
    print("\n🧪 Testing multiple experiments for comparison...")
    
    experiments = [
        {
            'name': 'transformer-large-lr001',
            'config': {
                'model_type': 'transformer',
                'model_size': 'large',
                'learning_rate': 0.001,
                'batch_size': 32,
                'num_epochs': 20,
                'dataset': 'imagenet-1k',
                'optimizer': 'adam',
                'weight_decay': 0.01
            },
            'description': 'Large transformer with learning rate 0.001'
        },
        {
            'name': 'transformer-large-lr0001',
            'config': {
                'model_type': 'transformer',
                'model_size': 'large',
                'learning_rate': 0.0001,
                'batch_size': 32,
                'num_epochs': 20,
                'dataset': 'imagenet-1k',
                'optimizer': 'adam',
                'weight_decay': 0.01
            },
            'description': 'Large transformer with learning rate 0.0001'
        },
        {
            'name': 'resnet-50-lr001',
            'config': {
                'model_type': 'resnet',
                'model_size': '50',
                'learning_rate': 0.001,
                'batch_size': 64,
                'num_epochs': 15,
                'dataset': 'cifar-100',
                'optimizer': 'sgd',
                'weight_decay': 0.0001
            },
            'description': 'ResNet-50 with learning rate 0.001'
        },
        {
            'name': 'vit-base-lr0005',
            'config': {
                'model_type': 'vision_transformer',
                'model_size': 'base',
                'learning_rate': 0.0005,
                'batch_size': 128,
                'num_epochs': 25,
                'dataset': 'imagenet-21k',
                'optimizer': 'adamw',
                'weight_decay': 0.05
            },
            'description': 'Vision Transformer base with learning rate 0.0005'
        }
    ]
    
    try:
        for exp in experiments:
            print(f"   Setting up experiment: {exp['name']}")
            reporter = PicoReporter()
            
            response = reporter.setup_experiment(
                experiment_name=exp['name'],
                config_data=exp['config'],
                description=exp['description']
            )
            
            # Run a short training simulation for each experiment
            run_short_training_simulation(exp['name'], exp['config'])
            
            time.sleep(0.1)  # Small delay between experiments
        
        print("✅ Multiple experiments setup and training completed successfully!")
        
    except Exception as e:
        print(f"❌ Multiple experiments test failed: {e}")

def run_short_training_simulation(exp_name, config):
    """Run a short training simulation for an experiment"""
    try:
        reporter = PicoReporter(experiment_name=exp_name)
        
        # Simulate different training characteristics based on config
        if config['model_type'] == 'transformer':
            base_loss = 3.0
            convergence_rate = 0.25
        elif config['model_type'] == 'resnet':
            base_loss = 2.0
            convergence_rate = 0.35
        elif config['model_type'] == 'vision_transformer':
            base_loss = 2.5
            convergence_rate = 0.3
        
        # Adjust based on learning rate
        if config['learning_rate'] <= 0.0001:
            convergence_rate *= 0.7  # Slower convergence with very low LR
        elif config['learning_rate'] >= 0.01:
            convergence_rate *= 1.3  # Faster convergence with high LR
        
        for step in range(1, 21):  # 20 steps
            epoch = (step - 1) // 5 + 1
            progress = (step - 1) % 5 / 5.0
            
            # Loss progression
            loss = base_loss * np.exp(-epoch * convergence_rate) * (1 - progress * 0.1)
            loss += random.uniform(-0.05, 0.05)
            
            # Accuracy progression
            accuracy = 0.1 + 0.8 * (1 - np.exp(-epoch * convergence_rate * 0.8))
            accuracy += random.uniform(-0.01, 0.01)
            
            reporter.log_training_metrics({
                'loss': round(max(0.01, loss), 4),
                'accuracy': round(min(0.99, accuracy), 4),
                'learning_rate': config['learning_rate'],
                'epoch': epoch,
                'step': step
            }, step=step)
            
            # Log validation metrics every 5 steps
            if step % 5 == 0:
                val_loss = loss * (1 + random.uniform(0.1, 0.2))
                val_accuracy = accuracy * (1 - random.uniform(0.05, 0.1))
                
                reporter.log_evaluation_metrics({
                    'val_loss': round(max(0.01, val_loss), 4),
                    'val_accuracy': round(min(0.99, val_accuracy), 4)
                }, step=step, task_name='validation')
            
            time.sleep(0.02)  # Very small delay for simulation
        
    except Exception as e:
        print(f"   ⚠️ Training simulation failed for {exp_name}: {e}")

def test_hyperparameter_ablation():
    """Test hyperparameter ablation study for systematic comparison"""
    print("\n🧪 Testing hyperparameter ablation study...")
    
    try:
        base_config = {
            'model_type': 'transformer',
            'model_size': 'base',
            'dataset': 'cifar-10',
            'num_epochs': 10,
            'optimizer': 'adam'
        }
        
        # Test different learning rates
        learning_rates = [0.0001, 0.0005, 0.001, 0.005, 0.01]
        
        for lr in learning_rates:
            exp_name = f"ablation-lr-{lr}"
            config = {**base_config, 'learning_rate': lr}
            
            print(f"   Testing learning rate: {lr}")
            reporter = PicoReporter()
            
            reporter.setup_experiment(
                experiment_name=exp_name,
                config_data=config,
                description=f'Ablation study: learning rate {lr}'
            )
            
            # Run training simulation
            run_ablation_training(exp_name, config)
            time.sleep(0.1)
        
        print("✅ Hyperparameter ablation study completed successfully!")
        
    except Exception as e:
        print(f"❌ Hyperparameter ablation test failed: {e}")

def run_ablation_training(exp_name, config):
    """Run training for ablation study"""
    try:
        reporter = PicoReporter(experiment_name=exp_name)
        
        for step in range(1, 16):  # 15 steps
            epoch = (step - 1) // 5 + 1
            progress = (step - 1) % 5 / 5.0
            
            # Different convergence patterns based on learning rate
            lr = config['learning_rate']
            if lr <= 0.0001:
                convergence_rate = 0.2
            elif lr <= 0.001:
                convergence_rate = 0.3
            elif lr <= 0.005:
                convergence_rate = 0.4
            else:
                convergence_rate = 0.5
            
            # Loss progression
            loss = 2.0 * np.exp(-epoch * convergence_rate) * (1 - progress * 0.1)
            loss += random.uniform(-0.03, 0.03)
            
            # Accuracy progression
            accuracy = 0.1 + 0.8 * (1 - np.exp(-epoch * convergence_rate * 0.8))
            accuracy += random.uniform(-0.01, 0.01)
            
            reporter.log_training_metrics({
                'loss': round(max(0.01, loss), 4),
                'accuracy': round(min(0.99, accuracy), 4),
                'learning_rate': lr,
                'epoch': epoch,
                'step': step
            }, step=step)
            
            time.sleep(0.01)
        
    except Exception as e:
        print(f"   ⚠️ Ablation training failed for {exp_name}: {e}")

def test_dataset_comparison():
    """Test training on different datasets for comparison"""
    print("\n🧪 Testing dataset comparison...")
    
    datasets = [
        {
            'name': 'cifar-10',
            'num_classes': 10,
            'image_size': 32,
            'num_samples': 50000
        },
        {
            'name': 'cifar-100',
            'num_classes': 100,
            'image_size': 32,
            'num_samples': 50000
        },
        {
            'name': 'imagenet-1k',
            'num_classes': 1000,
            'image_size': 224,
            'num_samples': 1281167
        }
    ]
    
    try:
        for dataset in datasets:
            exp_name = f"dataset-{dataset['name']}"
            config = {
                'model_type': 'resnet',
                'model_size': '18',
                'dataset': dataset['name'],
                'learning_rate': 0.001,
                'batch_size': 32,
                'num_epochs': 8
            }
            
            print(f"   Testing dataset: {dataset['name']}")
            reporter = PicoReporter()
            
            reporter.setup_experiment(
                experiment_name=exp_name,
                config_data=config,
                description=f'Dataset comparison: {dataset["name"]}'
            )
            
            # Run training simulation
            run_dataset_training(exp_name, config, dataset)
            time.sleep(0.1)
        
        print("✅ Dataset comparison completed successfully!")
        
    except Exception as e:
        print(f"❌ Dataset comparison test failed: {e}")

def run_dataset_training(exp_name, config, dataset):
    """Run training for dataset comparison"""
    try:
        reporter = PicoReporter(experiment_name=exp_name)
        
        for step in range(1, 21):  # 20 steps
            epoch = (step - 1) // 5 + 1
            progress = (step - 1) % 5 / 5.0
            
            # Adjust difficulty based on dataset complexity
            if dataset['name'] == 'cifar-10':
                base_loss = 1.5
                convergence_rate = 0.4
            elif dataset['name'] == 'cifar-100':
                base_loss = 2.0
                convergence_rate = 0.3
            else:  # imagenet-1k
                base_loss = 3.0
                convergence_rate = 0.25
            
            # Loss progression
            loss = base_loss * np.exp(-epoch * convergence_rate) * (1 - progress * 0.1)
            loss += random.uniform(-0.05, 0.05)
            
            # Accuracy progression
            accuracy = 0.05 + 0.9 * (1 - np.exp(-epoch * convergence_rate * 0.8))
            accuracy += random.uniform(-0.02, 0.02)
            
            reporter.log_training_metrics({
                'loss': round(max(0.01, loss), 4),
                'accuracy': round(min(0.99, accuracy), 4),
                'learning_rate': config['learning_rate'],
                'epoch': epoch,
                'step': step,
                'dataset_complexity': dataset['num_classes']
            }, step=step)
            
            time.sleep(0.01)
        
    except Exception as e:
        print(f"   ⚠️ Dataset training failed for {exp_name}: {e}")

if __name__ == '__main__':
    print("🚀 Starting pico-report package tests...")
    print(f"   API Key: {os.environ.get('PICO_API_KEY', 'Not set')}")
    print(f"   Base URL: {os.environ.get('PICO_BASE_URL', 'Not set')}")
    print("=" * 50)
    
    # Run basic tests
    test_basic_metrics()
    test_evaluation_metrics()
    test_system_metrics()
    test_checkpoint_data()
    test_learning_dynamics()
    test_multiple_steps()
    test_experiment_setup()
    
    # Run enhanced tests with realistic data
    test_realistic_training_run()
    test_multiple_experiments()
    test_hyperparameter_ablation()
    test_dataset_comparison()
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")
    print("\n💡 Check your Supabase database to see the uploaded data:")
    print("   - experiments table: for experiment records")
    print("   - metrics table: for training/evaluation/system metrics")
    print("   - checkpoints table: for checkpoint information")
    print("   - learning_dynamics table: for learning dynamics data")
    print("\n🔍 Now you can test comparison functionality with:")
    print("   - Multiple experiments with different configurations")
    print("   - Hyperparameter ablation studies")
    print("   - Dataset comparisons")
    print("   - Learning rate comparisons")
    print("   - Model architecture comparisons")