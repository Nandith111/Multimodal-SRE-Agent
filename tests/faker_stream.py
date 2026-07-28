import time
import random
import requests
from faker import Faker

fake = Faker()
API_URL = "http://localhost:8000/ingest"

ROUTINE_LOGS = [
    "INFO User logged in successfully",
    "INFO Payment processed for order {order_id}",
    "WARNING API rate limit approaching for endpoint {endpoint}",
    "ERROR Invalid password attempt from IP {ip}",
    "INFO Background sync completed in {ms}ms",
    "ERROR Cache miss for key {key}"
]

NOVEL_LOG = "ERROR [2026-07-19 08:57:22] - Thread-14: Unhandled pg8000.exceptions.DatabaseError: FATAL: remaining connection slots are reserved for non-replication superuser connections. Traceback: ..."

def generate_log():
    # 95% routine, 5% novel
    if random.random() < 0.95:
        log_template = random.choice(ROUTINE_LOGS)
        msg = log_template.format(
            order_id=fake.uuid4()[:8],
            endpoint=fake.uri_path(),
            ip=fake.ipv4(),
            ms=random.randint(10, 500),
            key=fake.word()
        )
        return f"{msg}"
    else:
        return NOVEL_LOG

def stream_logs():
    print(f"Streaming logs to {API_URL}...")
    while True:
        log_msg = generate_log()
        try:
            response = requests.post(API_URL, json={"message": log_msg})
            print(f"Sent: {log_msg[:60]}... | Status: {response.status_code}")
        except Exception as e:
            print(f"Error sending log: {e}")
            
        time.sleep(random.uniform(0.5, 2.0))

if __name__ == "__main__":
    stream_logs()
