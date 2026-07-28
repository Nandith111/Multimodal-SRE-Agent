import os
import pickle
from worker.celery_app import celery_app
from db.database import SessionLocal
from sqlalchemy import text
import sys

# Load Scikit-Learn Model
MODEL_PATH = "models/classifier.pkl"
try:
    with open(MODEL_PATH, "rb") as f:
        classifier = pickle.load(f)
except FileNotFoundError:
    print(f"Warning: Model not found at {MODEL_PATH}. Run models/train.py first.")
    classifier = None

import mlflow

@celery_app.task(name="worker.tasks.process_log_task")
def process_log_task(log_message: str, image_path: str = None):
    # Step 1: The Gatekeeper (scikit-learn)
    confidence = 1.0
    status = "routine"
    agent_triggered = False

    if classifier:
        # Predict probability of being "routine" (class 1)
        prob = classifier.predict_proba([log_message])[0]
        # prob[1] is confidence it is routine, prob[0] is confidence it is novel
        confidence = prob[1]
        
        # If confidence it's routine is < 85%, it's novel
        if confidence < 0.85:
            status = "novel"
            agent_triggered = True

    # Save initial log to DB
    db = SessionLocal()
    try:
        result = db.execute(
            text("INSERT INTO logs (message, status, confidence, agent_triggered) VALUES (:msg, :status, :conf, :agent) RETURNING id"),
            {"msg": log_message, "status": status, "conf": confidence, "agent": agent_triggered}
        )
        log_id = result.scalar()
        db.commit()
    except Exception as e:
        print(f"DB Error: {e}")
        db.rollback()
        return
    finally:
        db.close()

    # Step 2: Trigger LangGraph Agent if novel
    if agent_triggered:
        # We invoke the agent workflow here
        print(f"Novel log detected (confidence {confidence:.2f}). Triggering Agent for log ID {log_id}...")
        
        # Avoid circular imports by importing graph here
        try:
            from ai_agent.graph import run_agent
            
            # Setup MLflow Tracking
            mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000"))
            mlflow.set_experiment("sre-agent-pipeline")
            
            with mlflow.start_run(run_name=f"agent-run-log-{log_id}"):
                mlflow.log_param("log_id", log_id)
                mlflow.log_param("log_message", log_message)
                mlflow.log_param("has_image", bool(image_path))
                
                # Run the agent
                result_state = run_agent(log_id, log_message, image_path)
                
                # Log metrics/results
                if "structured_data" in result_state:
                    mlflow.log_dict(result_state["structured_data"], "structured_data.json")
                if "final_analysis" in result_state:
                    mlflow.log_dict(result_state["final_analysis"], "final_analysis.json")
                
                print("Agent execution completed and logged to MLflow.")
        except Exception as e:
            print(f"Agent Execution Error: {e}")

    return {"log_id": log_id, "status": status, "agent_triggered": agent_triggered}
