import os
import json
from typing import TypedDict, Any
from pydantic import BaseModel, Field
import instructor
from openai import OpenAI
from ai_agent.tools import retrieve_similar_post_mortems, detect_visual_anomaly
from db.database import SessionLocal
from sqlalchemy import text

# Setup Instructor to use Ollama's OpenAI-compatible endpoint
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

# Ollama now supports OpenAI API format at /v1
client = instructor.from_openai(
    OpenAI(
        base_url=f"{OLLAMA_BASE_URL}/v1",
        api_key="ollama",  # required but ignored
    ),
    mode=instructor.Mode.JSON
)

# 1. State Definition
class AgentState(TypedDict):
    log_id: int
    raw_log: str
    structured_data: dict[str, Any]
    retrieved_context: str
    image_path: str
    visual_context: str
    final_analysis: dict[str, Any]

# 2. Pydantic Models for Instructor
class LogExtraction(BaseModel):
    service: str = Field(description="The service or module throwing the error")
    error_type: str = Field(description="The general category of the error")
    driver: str = Field(description="The specific driver or library causing the issue, if any")
    
class RootCauseAnalysis(BaseModel):
    root_cause: str = Field(description="Detailed explanation of what caused the issue")
    suggested_fix: str = Field(description="Step-by-step actionable fix")
    slack_alert: str = Field(description="A short, formatted message to send to the team in Slack")

# 3. Node Functions

def extract_and_format(state: AgentState) -> AgentState:
    """Node 1: Extract entities from raw log."""
    print("Node 1: Extract & Format")
    
    extraction = client.chat.completions.create(
        model=OLLAMA_MODEL,
        response_model=LogExtraction,
        messages=[
            {"role": "system", "content": "You are a senior SRE. Extract structured entities from the following raw log."},
            {"role": "user", "content": state["raw_log"]}
        ]
    )
    
    state["structured_data"] = extraction.model_dump()
    return state

def retrieve_context(state: AgentState) -> AgentState:
    """Node 2: Retrieve similar past incidents."""
    print("Node 2: Retrieve Context")
    
    # Construct a search query from extracted data
    data = state["structured_data"]
    query = f"{data.get('error_type', '')} in {data.get('service', '')} involving {data.get('driver', '')}"
    
    context = retrieve_similar_post_mortems(query)
    state["retrieved_context"] = context
    return state

def analyze_visuals(state: AgentState) -> AgentState:
    """Node 2.5: Analyze uploaded dashboard screenshots if available."""
    print("Node 2.5: Analyze Visuals")
    
    image_path = state.get("image_path")
    if image_path and os.path.exists(image_path):
        visual_analysis = detect_visual_anomaly(image_path)
        state["visual_context"] = visual_analysis
    else:
        state["visual_context"] = "No visual dashboard provided."
        
    return state

def synthesize_and_diagnose(state: AgentState) -> AgentState:
    """Node 3 & 4: Synthesize root cause and format output."""
    print("Node 3 & 4: Synthesize & Output")
    
    prompt = f"""
    Raw Log:
    {state['raw_log']}
    
    Extracted Entities:
    {json.dumps(state['structured_data'])}
    
    Historical Context (Past Post-Mortems):
    {state['retrieved_context']}
    
    Visual Dashboard Context (if any):
    {state.get('visual_context', 'None')}
    
    Based on the raw log, historical context, and any visual dashboard analysis, provide a root cause analysis, a suggested fix, and draft a Slack alert.
    """
    
    analysis = client.chat.completions.create(
        model=OLLAMA_MODEL,
        response_model=RootCauseAnalysis,
        messages=[
            {"role": "system", "content": "You are an expert SRE AI. Diagnose the issue and provide actionable solutions."},
            {"role": "user", "content": prompt}
        ]
    )
    
    state["final_analysis"] = analysis.model_dump()
    
    # Persist the result to the database
    db = SessionLocal()
    try:
        db.execute(
            text("""
            INSERT INTO agent_analyses (log_id, root_cause, suggested_fix, slack_alert) 
            VALUES (:log_id, :rc, :fix, :slack)
            """),
            {
                "log_id": state["log_id"],
                "rc": analysis.root_cause,
                "fix": analysis.suggested_fix,
                "slack": analysis.slack_alert
            }
        )
        db.commit()
    except Exception as e:
        print(f"DB Insert Error in Synthesis: {e}")
        db.rollback()
    finally:
        db.close()
        
    return state
