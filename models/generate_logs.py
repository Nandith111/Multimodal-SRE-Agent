import os
import csv
import random
from faker import Faker

def generate_logs(num_routine=15000, num_anomaly=10000, output_file='synthetic_logs.csv'):
    fake = Faker()
    logs = []
    
    # Generate Routine Logs (Class 1)
    routine_levels = ['INFO', 'DEBUG', 'WARNING']
    routine_messages = [
        "User logged in successfully",
        "Payment processed",
        "Service started",
        "API rate limit approaching",
        "Cache refreshed",
        "Health check passed",
        "Session timeout",
        "Data synchronized",
        "Request completed",
        "Connection established"
    ]
    
    for _ in range(num_routine):
        level = random.choice(routine_levels)
        timestamp = fake.date_time_between(start_date='-30d', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
        base_msg = random.choice(routine_messages)
        # Adding some randomness
        ip = fake.ipv4()
        log_msg = f"{level} [{timestamp}] {base_msg} - IP: {ip}"
        logs.append({'message': log_msg, 'label': 1})
        
    # Generate Anomaly/Error Logs (Class 0)
    anomaly_levels = ['ERROR', 'CRITICAL', 'FATAL']
    anomaly_messages = [
        "Invalid password attempt",
        "Cache miss",
        "Segmentation fault in core module",
        "OutOfMemoryError: Java heap space",
        "Database connection failed",
        "Unhandled pg8000.exceptions.DatabaseError: FATAL: remaining connection slots are reserved",
        "Timeout waiting for response from microservice",
        "Disk space critically low",
        "Unauthorized access attempt detected",
        "Failed to load module"
    ]
    
    for _ in range(num_anomaly):
        level = random.choice(anomaly_levels)
        timestamp = fake.date_time_between(start_date='-30d', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
        base_msg = random.choice(anomaly_messages)
        # Adding some stack traces or extra info for anomalies
        user = fake.user_name()
        if random.random() > 0.5:
            log_msg = f"{level} [{timestamp}] {base_msg} - User: {user} - Traceback: {fake.uuid4()}"
        else:
            log_msg = f"{level} [{timestamp}] {base_msg} - User: {user}"
        logs.append({'message': log_msg, 'label': 0})
        
    # Shuffle the logs to mix routine and anomalies
    random.shuffle(logs)
    
    # Save to CSV
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, output_file)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['message', 'label'])
        writer.writeheader()
        writer.writerows(logs)
        
    print(f"Successfully generated {len(logs)} logs at {output_path}")

if __name__ == "__main__":
    print("Generating synthetic logs using Faker...")
    generate_logs(num_routine=15000, num_anomaly=10000)
