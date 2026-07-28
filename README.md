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

## Log Classification

- TF-IDF Vectorizer
- Logistic Regression
- Binary Classification

Classes:

- Routine
- Novel

---

## Dashboard Classification

Transfer Learning using:

- ResNet18

Output:

- Healthy
- Anomalous

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

GitHub Actions automatically performs:

- Code linting (Pylint)
- Static analysis (SonarCloud)
- Unit testing (Pytest)
- Docker image build
- Push to GitHub Container Registry
- Azure Web App deployment

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

# 📄 License

This project is intended for educational and research purposes.