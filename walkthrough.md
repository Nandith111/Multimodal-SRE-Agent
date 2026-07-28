# Agentic SRE Tech Stack Implementation Walkthrough

I have fully implemented the requested log triage and automated incident response pipeline. The solution leverages multiple layers to efficiently process logs, intelligently identify anomalies, and autonomously research and formulate fixes.

## Architecture & Components

The implementation aligns exactly with your provided architecture, using the following components:

- **Ingestion & Generation**: [tests/faker_stream.py](file:///d:/SRE%20Agent/tests/faker_stream.py) streams synthetic log traffic to the FastAPI entry point.
- **Web API**: [api/main.py](file:///d:/SRE%20Agent/api/main.py) exposes the `/ingest` endpoint and handles requests quickly by delegating processing.
- **Task Broker**: [worker/celery_app.py](file:///d:/SRE%20Agent/worker/celery_app.py) configures Celery to use Redis for ultra-low-latency asynchronous message queuing.
- **Tier-1 Router (Gatekeeper)**: [models/train.py](file:///d:/SRE%20Agent/models/train.py) trains a TF-IDF + LogisticRegression model to predict whether a log is routine. In [worker/tasks.py](file:///d:/SRE%20Agent/worker/tasks.py), logs falling below an 85% confidence score trigger the LangGraph agent.
- **Agent Orchestrator (LangGraph)**: The graph and state are defined in [ai_agent/graph.py](file:///d:/SRE%20Agent/ai_agent/graph.py).
- **Agent Brain & Guardrails**: Nodes inside [ai_agent/nodes.py](file:///d:/SRE%20Agent/ai_agent/nodes.py) use Ollama connected via Instructor and Pydantic to ensure strict JSON structured output.
- **Knowledge Base**: Structured data and `pgvector` embeddings are saved to PostgreSQL via SQLAlchemy configurations in [db/database.py](file:///d:/SRE%20Agent/db/database.py) and schemas defined in [db/schemas.sql](file:///d:/SRE%20Agent/db/schemas.sql). Vector search logic lives in [ai_agent/tools.py](file:///d:/SRE%20Agent/ai_agent/tools.py).
- **Business Dashboard**: [dashboard/app.py](file:///d:/SRE%20Agent/dashboard/app.py) visualizes ingested logs, calculates cost avoidance, and lists new anomalies using Streamlit.
- **System Dashboard**: Prometheus configuration in `prometheus.yml` scrapes FastAPI metrics for Grafana visualization.
- **Computer Vision Pipeline**: [models/dataset_generator.py](file:///d:/SRE%20Agent/models/dataset_generator.py) synthetically generates chart data, [models/train_cnn.py](file:///d:/SRE%20Agent/models/train_cnn.py) trains a ResNet18 model, and [models/vision_inference.py](file:///d:/SRE%20Agent/models/vision_inference.py) provides inference for detecting dashboard anomalies uploaded via Streamlit.

---

## How to Run the Pipeline Locally

Follow these steps to bring up the system on your machine:

### 1. Start Infrastructure Dependencies
Ensure Docker Desktop is running, then run the infrastructure services (Redis, PostgreSQL with pgvector, Prometheus, Grafana) in the background:
```bash
docker-compose up -d
```

### 2. Initialize the Database
Execute the `schemas.sql` file to create tables and enable `pgvector`.
```bash
docker exec -i sre-agent-postgres-1 psql -U sre_user -d sre_kb < db/schemas.sql
```
*(Note: Replace `sre-agent-postgres-1` with your actual Postgres container name if different)*

### 3. Install Python Dependencies
Create a virtual environment and install the required packages:
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Train the ML Gatekeeper Model
Run the script to train the scikit-learn model and save it as a pickle file:
```bash
python models/train.py
```

### 4b. Prepare and Train the Computer Vision Model (Optional)
To enable the "Manual Visual Triage" feature on the dashboard, you must generate the synthetic dataset and train the CNN:
```bash
python models/dataset_generator.py
python models/train_cnn.py
```

### 5. Start the Microservices
You will need to open **four** separate terminal windows (with the `venv` activated in each) to run the services concurrently:

**Terminal 1: FastAPI**
```bash
uvicorn api.main:app --reload
```

**Terminal 2: Celery Worker**
```bash
# On Windows, you may need to use threads instead of prefork
celery -A worker.celery_app worker --loglevel=info --pool=threads
```

**Terminal 3: Streamlit Dashboard**
```bash
streamlit run dashboard/app.py
```

**Terminal 4: Log Simulator**
```bash
python tests/faker_stream.py
```

> [!NOTE]
> **Important:** To run the LangGraph agent properly, ensure Ollama is installed and running locally with the mistral model pulled (`ollama run mistral`).

## What to Expect
As you run the log simulator, watch the Streamlit dashboard (`http://localhost:8501`). You will see normal, high-confidence logs flowing in as "routine" (green). When the simulated `pg8000.exceptions.DatabaseError` log arrives, the Gatekeeper will flag it with a low confidence score, mark it "novel", and trigger the LangGraph Agent. The Agent will execute locally via Ollama, pulling relevant history from pgvector, and populate the dashboard with the detailed root cause, solution, and drafted Slack alert.

Additionally, you can now use the **Manual Incident Triage** section at the top of the dashboard. Upload any of the generated images from `models/dataset/val/anomalous/` to see the Computer Vision pipeline detect the visual spike and trigger the AI agent for a full root-cause synthesis!

---

## Recent Upgrades: Hybrid RAG, Multimodal API & CI/CD

The pipeline has been upgraded with the following production-ready features:

### 1. Hybrid RAG Pipeline
We upgraded the simple vector search to a **Hybrid RAG** system that combines Dense (Semantic) and Sparse (Keyword) search, along with a CrossEncoder for reranking.
- **Database Schema ([db/schemas.sql](file:///d:/SRE%20Agent/db/schemas.sql))**: Added a `tsvector` column (`text_search`) and a GIN index to the `post_mortems` table to enable fast PostgreSQL full-text search.
- **RAG Tool ([ai_agent/tools.py](file:///d:/SRE%20Agent/ai_agent/tools.py))**: Rewrote the retrieval function to fetch Dense results (pgvector) and Sparse results (Postgres `plainto_tsquery`), deduplicate them, and rerank the top candidates using `sentence-transformers`.

### 2. Multimodal API Integration
- **API and Worker ([api/main.py](file:///d:/SRE%20Agent/api/main.py), [worker/tasks.py](file:///d:/SRE%20Agent/worker/tasks.py))**: Updated the FastAPI `LogEntry` schema and Celery task signature to accept an `image_path`. This allows the agent to process both the textual error log and any uploaded visual dashboard screenshots seamlessly through the backend queue.

### 3. ML Observability & Monitoring
- **MLflow Tracking**: Integrated `mlflow` into the Celery worker. Every time the agent runs, it creates an MLflow run that tracks the inputs, whether an image was present, the structured entities extracted, and the final synthesis output.
- **Docker Compose ([docker-compose.yml](file:///d:/SRE%20Agent/docker-compose.yml))**: Added an `mlflow` service. The stack now includes Redis, Postgres, Prometheus, Grafana, MLflow, and the built `app` and `worker` images.

### 4. CI/CD Pipeline
- **GitHub Actions ([.github/workflows/ci-cd.yml](file:///d:/SRE%20Agent/.github/workflows/ci-cd.yml))**: Created a workflow that runs on push to `main` featuring code quality scans (`pylint`, SonarCloud), testing (`pytest`), Docker image building, and pushing to Azure Web App.
- **Dockerfile ([Dockerfile](file:///d:/SRE%20Agent/Dockerfile))**: Created a multi-stage Dockerfile containing all system dependencies necessary for the API and background workers.
