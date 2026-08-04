import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
import time
import subprocess
import sys

POSTGRES_USER = os.getenv("POSTGRES_USER", "sre_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "sre_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "sre_kb")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

st.set_page_config(page_title="SRE Agent Dashboard", layout="wide", page_icon="🤖")

st.title("🤖 Agentic SRE Dashboard")

# Function to load data
def load_data():
    try:
        logs_df = pd.read_sql("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 100", engine)
        analyses_df = pd.read_sql("SELECT * FROM agent_analyses ORDER BY analysis_time DESC LIMIT 10", engine)
        return logs_df, analyses_df
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return pd.DataFrame(), pd.DataFrame()

logs_df, analyses_df = load_data()

# Business Metrics
st.header("Business Metrics")
col1, col2, col3 = st.columns(3)

total_logs = len(logs_df) if not logs_df.empty else 0
anomalies = len(logs_df[logs_df['agent_triggered'] == True]) if not logs_df.empty else 0

# Assume every API call we didn't send to a paid cloud LLM saved $0.05
cost_avoided = anomalies * 0.05 

col1.metric("Total Logs Analyzed (Recent)", total_logs)
col2.metric("Novel Anomalies Triaged", anomalies)
col3.metric("Cost Avoidance (Ollama)", f"${cost_avoided:.2f}")

st.markdown("---")

# Live Log Tailing Section
st.header("🔌 Live Log Tailing")
st.write("Automatically read a log file from another project and send it to the SRE Agent.")

# Initialize session state for tailing process
if 'tail_process' not in st.session_state:
    st.session_state.tail_process = None

tail_col1, tail_col2, tail_col3 = st.columns([3, 1, 1])
log_file_path = tail_col1.text_input("Absolute Path to Log File", placeholder="/var/log/my_project/app.log")

def stop_tailing():
    if st.session_state.tail_process is not None:
        try:
            st.session_state.tail_process.terminate()
            st.session_state.tail_process = None
        except Exception as e:
            st.error(f"Failed to stop process: {e}")

if tail_col2.button("▶️ Start Tailing", use_container_width=True):
    if not log_file_path:
        st.warning("Please enter a valid file path.")
    elif not os.path.exists(log_file_path):
        st.error(f"File not found: {log_file_path}")
    else:
        # Stop existing if running
        stop_tailing()
        
        # Start new process
        try:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            template_path = os.path.join(root_dir, "fluent-bit.conf")
            temp_conf_path = os.path.join(root_dir, "temp_fluent_bit.conf")
            
            with open(template_path, 'r') as f:
                lines = f.readlines()
                
            with open(temp_conf_path, 'w') as f:
                for line in lines:
                    if line.strip().startswith("Path"):
                        f.write(f"    Path         {log_file_path}\n")
                    else:
                        f.write(line)
            
            process = subprocess.Popen(["fluent-bit", "-c", temp_conf_path])
            st.session_state.tail_process = process
            st.success(f"Started tailing {log_file_path} via Fluent Bit")
        except FileNotFoundError:
            st.error("Failed to start Fluent Bit. Ensure it is installed and added to your system PATH.")
        except Exception as e:
            st.error(f"Failed to start tailing: {e}")

if tail_col3.button("⏹️ Stop Tailing", use_container_width=True):
    stop_tailing()
    st.info("Stopped tailing.")

if st.session_state.tail_process is not None:
    st.success(f"✅ Currently tailing a log file in the background. (PID: {st.session_state.tail_process.pid})")
else:
    st.info("No active log tailing.")

st.markdown("---")

# Manual Triage Section
st.header("Manual Incident Triage (with Vision)")
uploaded_file = st.file_uploader("Upload a Dashboard Screenshot (Grafana, etc.)", type=['png', 'jpg', 'jpeg'])
user_log_input = st.text_area("Optional Log Context or Description", value="Manual triage triggered from dashboard.")

if st.button("Analyze with SRE Agent"):
    if uploaded_file is not None:
        import uuid
        from ai_agent.graph import run_agent
        
        # Save image to a temp location
        os.makedirs("temp_uploads", exist_ok=True)
        img_path = f"temp_uploads/{uuid.uuid4()}.png"
        with open(img_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        with st.spinner("Analyzing image and synthesizing root cause..."):
            # Dummy log_id for manual triage
            log_id = int(time.time())
            try:
                result = run_agent(log_id=log_id, raw_log=user_log_input, image_path=img_path)
                
                st.success("Analysis Complete!")
                st.subheader("Visual Context")
                st.write(result.get("visual_context", "None"))
                
                st.subheader("Root Cause Analysis")
                final = result.get("final_analysis", {})
                st.write(final.get("root_cause", "N/A"))
                
                st.subheader("Suggested Fix")
                st.write(final.get("suggested_fix", "N/A"))
                
                st.subheader("Slack Draft")
                st.code(final.get("slack_alert", "N/A"))
            except Exception as e:
                st.error(f"Error during analysis: {e}")
    else:
        st.warning("Please upload an image first.")

st.markdown("---")

# Active Incidents
st.header("Active AI Investigations")

if not analyses_df.empty:
    for _, row in analyses_df.iterrows():
        with st.expander(f"Incident Analysis: Log ID {row['log_id']} - {row['analysis_time']}"):
            st.markdown(f"**Root Cause:**\n{row['root_cause']}")
            st.markdown(f"**Suggested Fix:**\n{row['suggested_fix']}")
            st.markdown(f"**Slack Alert Draft:**\n```\n{row['slack_alert']}\n```")
else:
    st.info("No active investigations. System is healthy.")

st.markdown("---")

# Recent Logs Feed
st.header("Recent Logs Feed")
if not logs_df.empty:
    # Highlight anomalies in red
    def color_status(val):
        color = 'red' if val == 'novel' else 'green'
        return f'color: {color}'
    
    st.dataframe(logs_df[['timestamp', 'message', 'confidence', 'status']].style.applymap(color_status, subset=['status']), use_container_width=True)
else:
    st.write("No logs recorded yet.")

# Auto-refresh
time.sleep(5)
st.rerun()
