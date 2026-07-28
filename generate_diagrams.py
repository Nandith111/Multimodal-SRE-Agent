import base64
import requests
import os

def generate_mermaid_image(mermaid_code, output_filename):
    # Encode the mermaid code to base64
    graphbytes = mermaid_code.encode("utf8")
    # mermaid.ink requires standard base64 or base64url.
    # standard base64 is usually fine, but let's use urlsafe
    base64_bytes = base64.urlsafe_b64encode(graphbytes)
    base64_string = base64_bytes.decode("ascii")
    
    url = f"https://mermaid.ink/img/{base64_string}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(output_filename, 'wb') as f:
            f.write(response.content)
        print(f"Successfully generated {output_filename}")
    except Exception as e:
        print(f"Failed to generate {output_filename}: {e}")

arch_graph = """
graph TD
    A[Fake Logs/Faker] -->|HTTP POST| B(FastAPI)
    B -->|Async| C[Redis Queue]
    C -->|Pulls| D[Celery Worker]
    D --> E{Gatekeeper Model<br>scikit-learn}
    E -->|> 85% Confidence| F[Log is Routine<br>Dropped]
    E -->|< 85% Confidence| G[LangGraph Agent]
    
    L[SRE Uploads Screenshot] -->|Manual Triage| K[Streamlit Dashboard]
    K -->|Inference| M(ResNet18 CNN Model)
    M -->|Visual Context| G
    
    G <-->|RAG Query| H[(PostgreSQL + pgvector)]
    G <-->|Prompt| I(Ollama Local LLM)
    G -->|JSON Output| J[(PostgreSQL DB)]
    J --> K
"""

rag_graph = """
sequenceDiagram
    participant Agent as LangGraph Agent
    participant DB as pgvector DB
    participant LLM as Ollama LLM
    Agent->>Agent: 1. Extract error details
    Agent->>DB: 2. Search embeddings (Cosine Distance)
    DB-->>Agent: 3. Return relevant historical chunk
    Agent->>LLM: 4. Send new error + historical chunk
    LLM-->>Agent: 5. Synthesize Root Cause & Fix
"""

if __name__ == "__main__":
    generate_mermaid_image(arch_graph, "arch_diagram.png")
    generate_mermaid_image(rag_graph, "rag_diagram.png")
