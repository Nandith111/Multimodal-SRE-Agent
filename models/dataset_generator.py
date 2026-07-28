import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def generate_time_series(length=100, anomaly=False, anomaly_type='spike'):
    # Base normal metric (e.g., CPU hovering around 20-40%)
    base_level = np.random.uniform(20, 40)
    noise = np.random.normal(0, 2, length)
    ts = base_level + noise
    
    if anomaly:
        start_idx = np.random.randint(10, length - 20)
        duration = np.random.randint(5, 15)
        if anomaly_type == 'spike':
            # Sudden spike
            ts[start_idx:start_idx+duration] += np.random.uniform(40, 60)
        elif anomaly_type == 'drop':
            # Sudden drop to near zero
            ts[start_idx:start_idx+duration] -= np.random.uniform(15, base_level)
            
    # Ensure no negative values for things like CPU
    ts = np.clip(ts, 0, 100)
    return ts

def plot_and_save(ts, label, save_dir, index):
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Simulating a Grafana-like dark theme
    fig.patch.set_facecolor('#1e1e2e')
    ax.set_facecolor('#1e1e2e')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#555555')
        
    ax.plot(ts, color='#00ffcc', linewidth=2)
    ax.set_ylim(0, 105)
    ax.set_xticks([]) # Hide X axis ticks for cleaner look
    
    # Save tightly to focus on the chart
    filename = os.path.join(save_dir, f"{label}_{index}.png")
    plt.savefig(filename, facecolor=fig.get_facecolor(), bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)

def create_dataset(base_dir, num_samples_per_class=100, val_split=0.2):
    train_dir = os.path.join(base_dir, 'train')
    val_dir = os.path.join(base_dir, 'val')
    
    for split_dir in [train_dir, val_dir]:
        os.makedirs(os.path.join(split_dir, 'healthy'), exist_ok=True)
        os.makedirs(os.path.join(split_dir, 'anomalous'), exist_ok=True)
        
    num_train = int(num_samples_per_class * (1 - val_split))
    num_val = num_samples_per_class - num_train
    
    # Generate Healthy
    for i in range(num_samples_per_class):
        ts = generate_time_series(anomaly=False)
        split = 'train' if i < num_train else 'val'
        save_dir = os.path.join(base_dir, split, 'healthy')
        plot_and_save(ts, 'healthy', save_dir, i)
        
    # Generate Anomalous
    for i in range(num_samples_per_class):
        anomaly_type = np.random.choice(['spike', 'drop'])
        ts = generate_time_series(anomaly=True, anomaly_type=anomaly_type)
        split = 'train' if i < num_train else 'val'
        save_dir = os.path.join(base_dir, split, 'anomalous')
        plot_and_save(ts, 'anomalous', save_dir, i)

if __name__ == "__main__":
    print("Generating synthetic dataset...")
    base_dir = os.path.join(os.path.dirname(__file__), 'dataset')
    create_dataset(base_dir, num_samples_per_class=100) # Quick small dataset
    print(f"Dataset generated at {base_dir}")
