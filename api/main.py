import os
import time
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from worker.tasks import process_log_task
from prometheus_client import make_asgi_app, Counter, Histogram

app = FastAPI(title="SRE Agentic Pipeline API")

# Prometheus Metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

LOG_INGESTION_COUNT = Counter("log_ingestion_total", "Total logs ingested")
LOG_INGESTION_LATENCY = Histogram("log_ingestion_latency_seconds", "Latency of log ingestion")

from typing import Optional

class LogEntry(BaseModel):
    message: str
    image_path: Optional[str] = None

@app.post("/ingest")
async def ingest_log(log: LogEntry):
    start_time = time.time()
    
    LOG_INGESTION_COUNT.inc()
    
    # Send to Celery queue
    # We do this asynchronously so the API returns instantly
    process_log_task.delay(log.message, log.image_path)
    
    LOG_INGESTION_LATENCY.observe(time.time() - start_time)
    
    return {"status": "queued"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
