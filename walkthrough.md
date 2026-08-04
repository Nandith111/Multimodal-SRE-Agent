# Agentic SRE Tech Stack Implementation Walkthrough

I have fully implemented the requested log triage and automated incident response pipeline. The solution leverages multiple layers to efficiently process logs, intelligently identify anomalies, and autonomously research and formulate fixes.

## Architecture & Components

The implementation aligns exactly with your provided architecture, using the following components:

- **Ingestion & Generation**: [models/generate_logs.py](file:///d:/SRE%20Agent/models/generate_logs.py) generates a dataset using Faker. [live_feed.py](file:///d:/SRE%20Agent/live_feed.py) and [fluent-bit.conf](file:///d:/SRE%20Agent/fluent-bit.conf) provide mechanisms to stream local and remote log traffic to the FastAPI entry point.
- **Web API**: [api/main.py](file:///d:/SRE%20Agent/api/main.py) exposes the `/ingest` endpoint and handles requests quickly by delegating processing.
- **Task Broker**: [worker/celery_app.py](file:///d:/SRE%20Agent/worker/celery_app.py) configures Celery to use Redis for ultra-low-latency asynchronous message queuing.
- **Tier-1 Router (Gatekeeper)**: [models/train.py](file:///d:/SRE%20Agent/models/train.py) trains and evaluates 3 models, selecting the best (Logistic Regression) based on F1-Score to predict whether a log is routine. In [worker/tasks.py](file:///d:/SRE%20Agent/worker/tasks.py), logs falling below an 85% confidence score trigger the LangGraph agent.
- **Agent Orchestrator (LangGraph)**: The graph and state are defined in [ai_agent/graph.py](file:///d:/SRE%20Agent/ai_agent/graph.py).
- **Agent Brain & Guardrails**: Nodes inside [ai_agent/nodes.py](file:///d:/SRE%20Agent/ai_agent/nodes.py) use Ollama (or a cloud provider) connected via Instructor and Pydantic to ensure strict JSON structured output.
- **Knowledge Base**: Structured data and `pgvector` embeddings are saved to PostgreSQL via SQLAlchemy configurations in [db/database.py](file:///d:/SRE%20Agent/db/database.py) and schemas defined in [db/schemas.sql](file:///d:/SRE%20Agent/db/schemas.sql). Vector search logic lives in [ai_agent/tools.py](file:///d:/SRE%20Agent/ai_agent/tools.py).
- **Business Dashboard**: [dashboard/app.py](file:///d:/SRE%20Agent/dashboard/app.py) visualizes ingested logs, calculates cost avoidance, and lists new anomalies using Streamlit.
- **System Dashboard**: Prometheus configuration in `prometheus.yml` scrapes FastAPI metrics for Grafana visualization.
- **Computer Vision Pipeline**: [models/dataset_generator.py](file:///d:/SRE%20Agent/models/dataset_generator.py) synthetically generates chart data, [models/train_cnn.py](file:///d:/SRE%20Agent/models/train_cnn.py) trains a ResNet18 model, and [models/vision_inference.py](file:///d:/SRE%20Agent/models/vision_inference.py) provides inference for detecting dashboard anomalies uploaded via Streamlit.

---

## Prerequisites & Setup

Before running the application, ensure the following software is installed on your Windows machine:

1.  **Docker Desktop**: Required to spin up PostgreSQL (with pgvector), Redis, Prometheus, Grafana, and MLflow. Ensure the Docker engine is running.
2.  **Ollama**: Required to run local AI models. 
    *   Download from [ollama.com](https://ollama.com).
    *   Open a command prompt (`cmd`) and pull the required model:
        ```cmd
        ollama pull mistral
        ```
    *   Ensure Ollama is running in the background.
3.  **Python 3.10+**: Make sure Python and `pip` are installed and added to your System PATH.

### Optional: Using a Cloud Model (e.g., Groq) Instead of Local Ollama
If you do not want to run Ollama locally and prefer a lightning-fast cloud model like Groq, you can modify the environment variables. Because `instructor` uses an OpenAI-compatible client, Groq drops in perfectly.

1.  Open your `.env` file (or set these variables in your terminal):
    ```env
    OLLAMA_BASE_URL=https://api.groq.com/openai
    OLLAMA_MODEL=llama3-70b-8192
    ```
2.  Open `ai_agent/nodes.py` and modify the `api_key` line in the `instructor.from_openai()` initialization to use your actual Groq API key:
    ```python
    api_key=os.getenv("GROQ_API_KEY", "your-groq-key-here")
    ```

---

## How to Run the Pipeline Locally

Follow these steps in your Windows Command Prompt (`cmd`) to bring up the system:

### 1. Start Infrastructure Dependencies
Run the infrastructure services in the background using Docker:
```cmd
docker-compose up -d
```

### 2. Initialize the Database
Execute the `schemas.sql` file to create tables and enable `pgvector`.
```cmd
docker exec -i sre-agent-postgres-1 psql -U sre_user -d sre_kb < db\schemas.sql
```
*(Note: Replace `sre-agent-postgres-1` with your actual Postgres container name if different)*

### 3. Install Python Dependencies
Create a virtual environment and install the required packages:
```cmd
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Train the ML Gatekeeper Model
Run the script to generate the synthetic log dataset using Faker, and then train the scikit-learn models. The training script will evaluate 3 different models and save the best one:
```cmd
python models\generate_logs.py
python models\train.py
```

### 4b. Prepare and Train the Computer Vision Model (Optional)
To enable the "Manual Visual Triage" feature on the dashboard, generate the synthetic dataset and train the CNN:
```cmd
python models\dataset_generator.py
python models\train_cnn.py
```

### 5. Start the Microservices
You no longer need to open multiple terminals! Simply double-click or run the provided automated batch script from your root directory:

```cmd
start_sre.bat
```

This will automatically spawn the FastAPI server, the Celery Worker, and the Streamlit Dashboard in their own separate windows.

---

## Live Log Streaming (No Code Required)

You can now feed live logs directly from any external project without touching the terminal or manually editing config files.

1. Open the Streamlit Dashboard (which opens automatically via `start_sre.bat`).
2. Navigate to the **🔌 Live Log Tailing** section.
3. Paste the absolute path to your project's log file (e.g., `C:\logs\my_app.log`).
4. Click **▶️ Start Tailing**.

The dashboard will silently configure and launch Fluent Bit in the background. Fluent Bit will instantly begin streaming your logs to the SRE Agent's API endpoint, and you will see the results appear live on your dashboard!

Alternatively, you can test it directly using `curl`:
```cmd
curl -X POST http://localhost:8000/ingest -H "Content-Type: application/json" -d "{\"message\": \"ERROR: Connection timeout in database cluster\"}"
```

---

## Production Log Shipping & Cloud Tunneling

To monitor deployed applications (like a remote travel booking app), you need a production-grade log shipper and a way to expose your local agent securely.

### 1. Configure Fluent Bit (Log Shipper)
We use **Fluent Bit** to read your application's logs and forward them to the SRE Agent. 
1. Install Fluent Bit on the machine where your application is running.
2. We have provided a `fluent-bit.conf` file in the root of this project.
3. Edit `fluent-bit.conf` and replace `/path/to/your/travel_app.log` with the actual path to your application's logs.
4. If your SRE Agent is running on a different machine, update the `Host` and `Port` fields under `[OUTPUT]` to point to the agent.
5. Run Fluent Bit:
   ```cmd
   fluent-bit -c fluent-bit.conf
   ```

### 2. Expose Local Agent with Ngrok (Tunneling)
If your application is in the cloud but your SRE Agent is running locally on your laptop, you can use Ngrok to expose the Agent's API to the internet.
1. Download and install [ngrok](https://ngrok.com/).
2. Start a tunnel to your FastAPI application (running on port 8000):
   ```cmd
   ngrok http 8000
   ```
3. Ngrok will give you a public URL (e.g., `https://abcdef123.ngrok-free.app`). 
4. Update the `Host` in your `fluent-bit.conf` to use this new Ngrok URL.

---

## Observability & Visualization Step-by-Step

The system is equipped with robust monitoring to track both system performance and machine learning operations.

### 1. MLflow (Model Metrics & Run Tracking)
Whenever the Agent is triggered (for a novel/anomalous log), the entire interaction is logged to MLflow.
1. Open your browser and navigate to `http://localhost:5000` (assuming MLflow was spun up via docker-compose).
2. On the left sidebar, click on the **sre-agent-pipeline** experiment.
3. You will see a list of runs, named by `log_id` (e.g., `agent-run-log-1`).
4. Click on a specific run to view its details.
5. Under **Parameters**, you can view the `log_message` and `has_image` flag.
6. Under **Artifacts**, you can download or view the `structured_data.json` and `final_analysis.json` produced by the Ollama agent.

### 2. Prometheus (System Metrics)
Prometheus scrapes the FastAPI server for metrics defined via the `prometheus-client` in `api/main.py`.
1. Open your browser and navigate to `http://localhost:9090`.
2. In the expression browser (Search bar), type `log_ingestion_total` and click **Execute**. You will see the total count of logs ingested.
3. Switch to the **Graph** tab to see the ingestion rate over time.
4. Try searching for `log_ingestion_latency_seconds_bucket` to observe the histogram of API latency distribution.

### 3. Grafana (Dashboard Visualizations)
Grafana connects to Prometheus to provide beautiful, persistent dashboards.
1. Open your browser and navigate to `http://localhost:3000`.
2. Log in (default credentials are usually `admin` / `admin`).
3. If not already configured, go to **Connections > Data Sources**, add **Prometheus**, and set the URL to `http://prometheus:9090`.
4. Go to **Dashboards > New Dashboard**.
5. Click **Add Visualization** and select your Prometheus data source.
6. In the query field, enter `rate(log_ingestion_total[1m])` to create a chart showing logs ingested per minute.
7. Click **Apply** to save the panel to your new System Dashboard.
