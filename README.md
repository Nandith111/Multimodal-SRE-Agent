# 🚀 Agentic SRE Log Triage Pipeline

An AI-powered Site Reliability Engineering (SRE) platform that automates log triage, anomaly detection, incident analysis, and root cause investigation using Machine Learning, Agentic AI, Hybrid RAG, and Computer Vision.

Instead of sending every log to an expensive LLM, the system first filters routine events using a lightweight machine learning classifier. Only novel or suspicious incidents are escalated to an AI agent that retrieves historical incidents, analyses dashboard screenshots, identifies probable root causes, and generates structured remediation reports.

---

## 📌 Overview

Modern distributed applications generate thousands of logs every minute. While most are routine operational messages, a small fraction indicate production failures requiring immediate attention.

This project automates that process by combining:

- Machine Learning-based log classification
- Agentic AI using LangGraph
- Local LLM inference using Ollama
- Hybrid Retrieval-Augmented Generation (Hybrid RAG)
- Computer Vision for dashboard screenshot analysis
- Asynchronous processing with Redis & Celery
- Real-time monitoring and observability

The entire system runs locally, avoiding cloud inference costs while maintaining data privacy.

---

# ✨ Features

- Automatic log ingestion
- FastAPI-based REST API
- Redis queue with Celery workers
- ML Gatekeeper model for routine log filtering
- LangGraph multi-agent workflow
- Local LLM inference using Ollama
- Hybrid RAG with PostgreSQL + pgvector
- Dashboard screenshot anomaly detection using ResNet18
- Structured JSON outputs using Pydantic
- Draft Slack alert generation
- MLflow experiment tracking
- Prometheus & Grafana monitoring
- Streamlit dashboard
- Dockerized microservices
- GitHub Actions CI/CD pipeline

---

# 🏗 System Architecture

```
                   Fake Log Generator
                          │
                          ▼
                      FastAPI API
                          │
                          ▼
                    Redis Message Queue
                          │
                          ▼
                     Celery Worker
                          │
                          ▼
              ML Gatekeeper (Logistic Regression)
                   │                     │
      Routine (>85%)              Novel (<85%)
            │                           │
            ▼                           ▼
      Drop Log                    LangGraph Agent
                                        │
                  ┌─────────────────────┼─────────────────────┐
                  ▼                     ▼                     ▼
           Hybrid RAG            Ollama Local LLM      Screenshot CNN
                  │                     │                     │
                  └───────────────Structured JSON─────────────┘
                                        │
                                        ▼
                                  PostgreSQL
                                        │
                                        ▼
                                 Streamlit UI
```

---

# 🧠 Technology Stack

| Layer | Technology |
|----------|------------|
| Backend | FastAPI |
| Queue | Redis |
| Workers | Celery |
| Machine Learning | Scikit-learn |
| Deep Learning | PyTorch |
| CNN | ResNet18 |
| Agent Framework | LangGraph |
| LLM | Ollama |
| Embeddings | nomic-embed-text |
| Database | PostgreSQL |
| Vector Database | pgvector |
| Validation | Pydantic |
| Dashboard | Streamlit |
| Monitoring | Prometheus + Grafana |
| Experiment Tracking | MLflow |
| Containerization | Docker |
| CI/CD | GitHub Actions |
| Cloud Deployment | Azure Web App |

---

# ⚙️ Project Workflow

## 1. Log Generation

A Python Faker script continuously generates synthetic production logs.

- Routine logs
- Warning logs
- Exception logs
- Rare production failures

---

## 2. API Ingestion

FastAPI receives logs through REST endpoints.

Incoming requests are immediately pushed into Redis to avoid blocking the API.

---

## 3. Asynchronous Processing

Celery workers consume logs from Redis and process them independently.

This architecture enables high-throughput log processing without overwhelming the API server.

---

## 4. Machine Learning Gatekeeper

A Logistic Regression classifier trained using TF-IDF features classifies incoming logs into:

- Routine
- Novel

If the prediction confidence exceeds 85%, the log is discarded.

Otherwise, it is escalated to the AI pipeline.

---

## 5. Agentic AI Investigation

LangGraph orchestrates the investigation workflow.

Typical agent steps include:

1. Extract information
2. Retrieve historical incidents
3. Analyse screenshots
4. Generate root cause
5. Recommend resolution

---

## 6. Hybrid RAG Pipeline

Historical incident reports are indexed using two retrieval methods.

### Dense Retrieval

- pgvector
- Semantic embeddings
- Cosine similarity

### Sparse Retrieval

- PostgreSQL Full Text Search
- Keyword matching

Both results are merged and re-ranked before being passed to the LLM.

---

## 7. Computer Vision Pipeline

SREs may upload Grafana dashboard screenshots.

The image pipeline:

- Resize to 224×224
- Normalize ImageNet statistics
- Infer using ResNet18

Output:

- Healthy
- Anomalous

The prediction becomes additional context for the AI agent.

---

## 8. Local LLM Analysis

Ollama performs:

- Root cause analysis
- Historical reasoning
- Incident summarization
- Resolution generation

Running locally ensures:

- Zero API costs
- Data privacy
- Offline capability

---

## 9. Structured Output

Pydantic enforces a strict JSON schema containing:

- Incident summary
- Root cause
- Confidence
- Suggested fix
- Draft Slack notification

---

## 10. Dashboard

A Streamlit dashboard provides:

- Live incidents
- Screenshot uploads
- AI analysis
- Historical incidents
- Cost savings
- Slack drafts

---

# 📂 Hybrid RAG Workflow

```
Historical Incidents
          │
          ▼
 Chunking & Embeddings
          │
          ▼
 PostgreSQL + pgvector
          │
          ▼
 Hybrid Retrieval
    ├── Dense Search
    └── Sparse Search
          │
          ▼
     Cross Encoder
       Re-ranking
          │
          ▼
     Top-K Context
          │
          ▼
      Ollama LLM
          │
          ▼
 Structured Root Cause
```

---

# 📊 Machine Learning Models

## 1. Text Log Classification (The Gatekeeper)

This model acts as the first line of defense, filtering out routine text logs so the LLM isn't overwhelmed.

- **Models Evaluated:** The training pipeline (`models/train.py`) evaluates three traditional machine learning models: **Logistic Regression**, **Random Forest**, and **Linear SVC**.
- **Preprocessing:** Before training, the raw text logs undergo preprocessing using a **TF-IDF Vectorizer** (`TfidfVectorizer`). This step removes common English "stop words" (like "the", "is", "and") and mathematically converts the remaining text into a matrix of term frequency-inverse document frequency features. This allows the models to understand which specific words are most important for classifying a log.
- **Evaluation Metrics:** The models are evaluated using four key metrics:
  - **Accuracy**
  - **Precision**
  - **Recall**
  - **F1-Score**
- **Identifying the Best Model:** The system automatically identifies the absolute best model by comparing their **F1-Scores**. F1-Score is chosen over simple accuracy because log datasets are often imbalanced (way more routine logs than errors). The model with the highest F1-Score is selected, saved as `classifier.pkl`, and used in production to classify logs into **Routine** or **Novel** classes.

---

## 2. Dashboard Image Classification (Computer Vision)

This model analyzes uploaded Grafana dashboard screenshots to provide visual context to the AI Agent.

- **Model Used:** We use **Transfer Learning** on a pretrained **ResNet18** Convolutional Neural Network (CNN). The early layers are frozen (keeping their general image recognition capabilities), and only the final fully connected layer is retrained to recognize our specific dashboard classes.
- **Preprocessing:** Images undergo several transformations before being fed to the CNN (`models/train_cnn.py`):
  - **Resizing:** Scaled to exactly `224x224` pixels.
  - **Data Augmentation:** During training, a `RandomHorizontalFlip` is applied to artificially increase dataset variety and prevent overfitting.
  - **Tensor Conversion:** Converted into a PyTorch Tensor format.
  - **Normalization:** The image color channels are normalized using standard ImageNet statistics (Mean: `[0.485, 0.456, 0.406]`, Std: `[0.229, 0.224, 0.225]`).
- **Evaluation Metrics:** The CNN is trained and evaluated using **Cross-Entropy Loss** and **Accuracy**.
- **Identifying the Best Model:** At the end of every training epoch, the model is tested on a separate validation dataset. The system tracks the **Validation Accuracy**. The weights from the epoch that achieved the absolute highest validation accuracy are saved as the final best model (`chart_anomaly_cnn.pth`). The model outputs a prediction of either **Healthy** or **Anomalous**.

## 3. Synthetic Training Data Generation

Because production logs are often proprietary and contain sensitive data, this project uses synthetic (fake) datasets specifically engineered to mimic real-world production environments to train both models.

### Text Log Generation (`models/generate_logs.py`)
The text dataset contains 25,000 synthetic log lines generated using the Python `Faker` library, simulating a busy backend service.
- **Routine Logs (15,000 samples):** These are normal operational logs. 
  - **Features:** They use log levels like `INFO`, `DEBUG`, and `WARNING`. 
  - **Content:** Messages include standard events like "User logged in successfully", "Payment processed", or "Health check passed". To simulate real unstructured data, random fake IPv4 addresses are appended to the end of these messages.
- **Anomalous Logs (10,000 samples):** These simulate critical system failures.
  - **Features:** They use severe log levels like `ERROR`, `CRITICAL`, and `FATAL`. 
  - **Content:** Messages include severe events like "Segmentation fault in core module", "Database connection failed", or "OutOfMemoryError: Java heap space". To make the dataset challenging and realistic, these logs contain fake usernames and, 50% of the time, append long fake UUID stack tracebacks.

### Dashboard Image Generation (`models/dataset_generator.py`)
The image dataset contains 400 synthetic Grafana-style charts (split evenly for training and validation), generated using `numpy` and `matplotlib`.
- **Visual Style:** The script intentionally generates images that look like modern observability dashboards—using a dark theme background (`#1e1e2e`), hidden axes, and a neon cyan line (`#00ffcc`) to represent a metric (like CPU usage over time).
- **Healthy Charts (200 samples):** These are generated as a flat baseline time series (hovering around 20-40% usage) with normal Gaussian noise added to simulate standard metric jitter.
- **Anomalous Charts (200 samples):** These start as healthy charts, but halfway through the time series, the script injects a sudden anomaly. The anomaly is randomly chosen to be either a massive **spike** (suddenly adding 40-60% usage) or a massive **drop** (dropping down near zero) lasting for 5 to 15 time units. 

These highly realistic synthetic datasets ensure the ML models are fully capable of recognizing patterns out-of-the-box before being fine-tuned on your project's actual data.

---

# 📈 Monitoring

The platform is continuously monitored using:

- Prometheus
- Grafana
- MLflow

Metrics include:

- Queue length
- Worker health
- API latency
- Model inference time
- Agent execution traces

---

# 🐳 Docker Services

The application is containerized using Docker Compose.

Services include:

- FastAPI
- Redis
- PostgreSQL
- pgvector
- Prometheus
- Grafana

---

# 🔄 CI/CD Pipeline

The project uses GitHub Actions to automate testing and deployment, ensuring that only high-quality, secure code reaches production. Here is how each step works in the automated pipeline:

- **Code Linting (Pylint):** As soon as a developer pushes code, Pylint scans the Python scripts to enforce coding standards (PEP 8). It catches syntax errors, unused variables, and messy formatting, ensuring the codebase remains clean and readable.
- **Static Analysis (SonarCloud):** SonarCloud performs a deep dive into the code's security and maintainability. It detects "code smells", hardcoded secrets, security vulnerabilities (like SQL injection risks), and tracks technical debt over time.
- **Unit Testing (Pytest):** Pytest automatically runs a suite of tests against the core logic (like checking if the ML Gatekeeper correctly classifies test logs or if the API returns the right status codes). If any test fails, the pipeline halts immediately, preventing broken code from deploying.
- **Docker Image Build:** Once the code passes linting, security checks, and testing, GitHub Actions uses the `Dockerfile` to build a fresh Docker image. This guarantees that the exact environment needed to run the app (including Python dependencies, Ollama, and system libraries) is perfectly packaged into a single container.
- **Push to GitHub Container Registry & Azure Deployment:** The freshly built Docker image is pushed to the registry, and a webhook tells the Azure Web App to pull the new container and seamlessly restart the service.

---

# 📁 Project Structure

```
.
├── app/
├── agent/
├── models/
├── rag/
├── workers/
├── database/
├── dashboard/
├── monitoring/
├── tests/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

# 🎯 Key Highlights

- Agentic AI-powered incident investigation
- Hybrid RAG using dense and sparse retrieval
- Local LLM inference with Ollama
- Computer Vision for dashboard analysis
- ML-based log triaging
- Fully asynchronous architecture
- Production-ready monitoring
- Dockerized microservices
- Automated CI/CD pipeline
- Cost-efficient on-premise deployment

---

# 🚀 Future Improvements

- Kubernetes deployment
- Multi-agent collaboration
- GraphRAG integration
- Automated remediation
- Live Slack webhook integration
- Multi-modal LLM support
- Advanced anomaly forecasting

---

---

# 🔄 How This Agent Can Analyze Logs From Any Project

This SRE Agent isn't just for a specific system—it acts as a universal, centralized brain. You can use its existing tools and technologies to analyze logs from a completely different project, like a **Travel Booking Platform** or an **AI Voicebot**, without changing the underlying architecture.

Here is a simple, easy-to-understand breakdown of exactly how it connects, reads, and analyzes logs from your separate project:

### 1. Connecting to Your Project
This agent acts as a listening server (a REST API built with **FastAPI**). To connect your separate project to this agent, you simply need to send your project's logs over the network to this listener. You don't need to rewrite your project's code to do this.

- For local testing, you can use the **Streamlit Dashboard**! It acts like a remote control for your logs. You simply type in the path to your log file, click a button, and the dashboard automatically connects your logs to the SRE agent.

#### Deep Dive: How Fluent Bit Works in Production
For a production server, the recommended approach is to install **Fluent Bit**. Fluent Bit is an industry-standard, incredibly fast log processor that runs as a background service on your server. This repository includes a pre-configured `fluent-bit.conf` file that handles the heavy lifting in three simple steps:
1. **The Input (Tailing):** It uses an `[INPUT]` block to constantly monitor (tail) your project's raw log files (e.g., `/path/to/your/travel_app.log`) exactly as they are written in real-time.
2. **The Filter (Structuring):** Because the SRE Agent's API expects data in a specific JSON format, Fluent Bit uses a `[FILTER]` block to instantly wrap your raw text log into a clean JSON object. 
   
   For example, if your raw log file outputs:
   `2026-08-04 10:00:00 ERROR [PaymentGateway] Connection timeout`
   
   Fluent Bit automatically converts it to:
   ```json
   {
     "message": "2026-08-04 10:00:00 ERROR [PaymentGateway] Connection timeout"
   }
   ```
3. **The Output (Shipping):** Finally, an `[OUTPUT]` block takes that nicely formatted JSON and fires it securely over the internet as an HTTP POST request straight into the SRE Agent's FastAPI listener (`/ingest` endpoint).

This means your actual project doesn't even know the SRE Agent exists—Fluent Bit acts as the invisible middleman doing all the parsing and shipping.

#### Deep Dive: The Streamlit Dashboard as a Remote Control
To make connecting external projects as simple as possible, the Streamlit dashboard acts as a remote control for the Fluent Bit engine. Instead of manually editing configuration files or using the command line, you simply paste the absolute path to your project's log file directly into the dashboard UI and click "Start Tailing".

Behind the scenes, the dashboard dynamically reads the `fluent-bit.conf` template, silently overwrites the `Path` variable with your input, and spawns the Fluent Bit background process. Fluent Bit then does all of its heavy lifting—reading the file, wrapping it in JSON, and securely POSTing it to the FastAPI endpoint for message queuing and SRE Agent analysis—exactly as it would in production. This fully automates the ingestion process, giving you an easy "plug-and-play" experience without sacrificing the robustness of the Fluent Bit architecture.

The file can be in any plain text format and the extension doesn't matter at all!

You can use .log, .txt, .out, .csv, or even a file with no extension.

Because Fluent Bit uses the standard tail plugin, all it cares about is that the file contains raw text with each log entry on a new line. When Fluent Bit reads a new line from the file, it simply takes that exact string of text, wraps it inside the {"message": "..."} JSON format required by the SRE Agent, and sends it on its way.

So whether your project spits out logs like app.log or just standard text files, it will work perfectly!

### 2. How the Agent Reads and Filters the Logs
When your project's logs arrive at the agent, they are placed into a high-speed waiting line (a queue powered by **Redis** and **Celery**). This ensures that if your project suddenly crashes and spits out thousands of logs at once, the agent won't get overwhelmed. 

#### Deep Dive: How Redis and Celery Work Together
To handle massive spikes in log volume without crashing, this project separates receiving logs from analyzing them:
- **Redis (The Queue):** Redis acts as an incredibly fast, in-memory message broker. When the FastAPI listener receives a new log from Fluent Bit, it instantly pushes a message containing the log into a Redis queue and immediately sends a "success" response back. This takes milliseconds, allowing the API to handle thousands of requests per second without blocking.
- **Celery (The Workers):** Celery is a distributed task queue system running in the background. It constantly watches Redis. Whenever a new log appears in the Redis queue, an available Celery "worker" picks it up and begins the heavy lifting—running it through the Scikit-learn ML Gatekeeper, and if it's an anomaly, triggering the full LangGraph AI pipeline. 

This asynchronous producer (FastAPI) and consumer (Celery) relationship via Redis guarantees that the system remains highly responsive and no logs are ever dropped during traffic spikes.

Once in the queue, a lightweight Machine Learning "Gatekeeper" (built with **Scikit-learn**) reads the log first. You can easily train this Gatekeeper to know what a "normal" log looks like for your specific project. If the Gatekeeper sees a normal log (like a routine voicebot greeting), it simply drops it to save processing power. If it sees something strange, novel, or broken, it rings the alarm and wakes up the AI Agent.

### 3. The Brains: Analysis, PSQL, and RAG
When the alarm rings, the AI Agent (powered by **LangGraph** and a local **Ollama** LLM) takes over. To figure out what went wrong, the AI needs context—it needs to know how *your specific team* fixes problems. 
This is the purpose of **PSQL (PostgreSQL)** and **RAG (Retrieval-Augmented Generation)**. The PSQL database acts as the agent's long-term memory. You can fill this database with your project's historical incident reports, architecture diagrams, and runbooks.
Instead of the AI just guessing how to fix the bug based on generic internet data, it uses RAG to search your PSQL database. It mathematically compares the current broken log to your past incidents, retrieves the exact document where your team solved a similar issue, and reads it. It then combines the raw log with your team's historical knowledge to deduce exactly what went wrong.

#### Deep Dive: How LangGraph Orchestrates the Workflow
To manage this complex investigation, the project uses **LangGraph** to build a reliable, multi-step pipeline. The graph consists of exactly **4 distinct nodes**, executed sequentially:

1. **`extract` (Node 1):** The LLM reads the messy, raw text log and extracts clean, structured entities (like exactly which service failed and what the specific error type is).
2. **`retrieve` (Node 2):** It takes those extracted entities and runs the RAG search against the PSQL database to find historical context.
3. **`analyze_visuals` (Node 3):** If a dashboard screenshot was uploaded alongside the log, a Computer Vision model (ResNet18) analyzes the image to see if there are visual anomalies (like a sudden drop in a graph).
4. **`synthesize` (Node 4):** The final step. The LLM is fed the raw log, the extracted data, the RAG context from PSQL, and the visual context. It synthesizes all of this to write the final Root Cause, Fix, and Slack Alert.

LangGraph orchestrates this by maintaining a central "Agent State" (a shared dictionary of data). It passes this state linearly from Node 1 → Node 2 → Node 3 → Node 4. Each node does its specific job, adds its findings to the state, and passes the increasingly enriched data to the next node until the investigation is complete.

#### Deep Dive: How the PSQL Database and pgvector Work
To make this RAG search incredibly fast and accurate, the project uses PSQL heavily enhanced by the **`pgvector`** extension. Here is exactly how data is stored and compared:

1. **How Data is Stored (Rows and Columns):** 
   Past incidents are stored in a PSQL table named `post_mortems`. Every single row in this table represents one past bug or incident. The table has exactly 8 columns, each serving a specific purpose: 
   - `id`: A unique auto-incrementing integer identifying the incident.
   - `incident_date`: A timestamp recording exactly when the past incident occurred.
   - `title`: A short, human-readable summary of the problem (e.g., "Database Outage").
   - `content`: The full textual description of the symptoms and logs seen during the incident.
   - `root_cause`: The detailed technical reason the incident happened.
   - `resolution`: The step-by-step actionable guide that was used to fix the incident.
   - `embedding`: A mathematical array (`vector(4096)`) representing the *semantic meaning* of the entire incident (used for similarity math).
   - `text_search`: A `tsvector` formatted column that indexes the text for extremely fast, traditional exact-keyword searches.

   Every single log that passes through the Celery worker (whether it is routine or novel) is immediately saved into the logs table in your PSQL database.
   1) The Gatekeeper (Scikit-learn) reads the log.
   2) It assigns a status ("routine" or "novel") and a confidence score. 
   3) It immediately inserts that log into the PSQL logs table along with its status and score. The table has exactly 7 columns: id (auto-generated), timestamp, log_content, status, confidence, agent_triggered (default: false), and created_at.
   4) If the log was marked as "novel", the system flips an agent_triggered flag to True in the database, and then wakes up the LangGraph AI Agent to figure out what went wrong.
   5) Once the AI finishes its investigation, its final root cause and suggested fix are saved in a separate PSQL table called agent_analyses, permanently linked to that original novel log.
2. **Converting Data into Vectors:**
   The `pgvector` extension doesn't convert the text itself. Instead, the agent sends your past documentation text to a specialized, open-source AI model (like `nomic-embed-text` running in Ollama). This AI reads the text and converts its *meaning* into a mathematical array of 4,096 numbers. 
3. **How Vectors are Stored:**
   Once the text is converted into that list of 4,096 numbers, it is saved back into PSQL inside the `embedding` column. Thanks to `pgvector`, this column uses a special data type literally called `vector(4096)`, allowing the database to understand advanced mathematics natively.
4. **How the Retriever Compares Them:**
   When a new, broken log arrives, the agent converts *that new log* into a 4,096-number vector too. It then asks PSQL to compare the new vector against all the stored past vectors. 
   - The comparison is done based on **Cosine Distance** (`1 - (embedding <=> :emb)` in SQL). If the numbers are mathematically similar, it means the *meaning* of the current error closely matches the *meaning* of a past error. 
   - The agent combines this math comparison with a traditional keyword search using the `text_search` column (looking for exact matching words). 
   - Finally, an advanced AI "CrossEncoder" looks at the top matches and reranks them to pick the absolute best, most relevant past incident to feed to the LLM for explanation.

### Automated Startup (Windows)
If you don't want to open three separate terminals every time, simply double-click the **`start_sre.bat`** file located in the root folder. It will automatically spawn all three required services (API, Celery, and Streamlit) in separate windows for you!

### Manual Startup (3 Terminals)

If you prefer to start them manually, open 3 separate terminals:

**Terminal 1: FastAPI Server**

### 4. Output and Display
You don't need to dig through messy terminal screens to see the results. The entire pipeline is connected to a sleek **Streamlit** dashboard. When you open the dashboard in your web browser, you will see a clean, live feed of all the critical incidents happening in your project.

When you click on an incident, you will see the final output generated by the AI. This output is a highly structured, easy-to-read report that contains three main things:
- **Root Cause Analysis:** A plain-English explanation of exactly what broke (e.g., "The payment gateway timed out because the Amadeus API rate limit was exceeded").
- **Suggested Fix:** A step-by-step, actionable guide on how to resolve the issue right now, based specifically on the runbooks it found in the PSQL database.
- **Draft Slack Alert:** A pre-written, nicely formatted message that you can instantly copy and paste into your team's Slack channel to let everyone know what's happening.

---

# 📄 License

This project is intended for educational and research purposes.