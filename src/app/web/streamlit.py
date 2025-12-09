import streamlit as st
import pandas as pd
import requests
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==============================================================================
# CONFIG
# ==============================================================================
API_URL = "http://localhost:8000"
HISTORY_ENDPOINT = f"{API_URL}/history"
HEALTH_ENDPOINT = f"{API_URL}/health"
REFRESH_RATE = 2  # Seconds

st.set_page_config(
    page_title="IDS Dashboard - XGBoost",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# STYLE & CSS
# ==============================================================================
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .metric-card {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #41444d;
    }
    .stDataFrame {
        border: 1px solid #41444d;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def check_api_health():
    try:
        r = requests.get(HEALTH_ENDPOINT, timeout=1)
        if r.status_code == 200:
            return True, r.json()
    except:
        pass
    return False, {}

def get_history_data():
    try:
        r = requests.get(HISTORY_ENDPOINT, timeout=1)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

# ==============================================================================
# MAIN LAYOUT
# ==============================================================================
st.title("🛡️ Network Intrusion Detection System")
st.markdown("### XGBoost Model Monitor | Real-time Threat Analysis")

# --- SIDEBAR ---
st.sidebar.header("System Status")
is_healthy, health_data = check_api_health()

if is_healthy:
    st.sidebar.success("API CONNECTED")
    st.sidebar.json(health_data)
else:
    st.sidebar.error("API DISCONNECTED")
    st.sidebar.warning("Please ensure main.py is running.")

st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)

# --- DATA FETCHING ---
history_data = get_history_data()

if not history_data:
    st.info("No traffic data received yet. Waiting for data stream...")
else:
    df = pd.DataFrame(history_data)
    # Convert timestamp if exists
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values(by='timestamp', ascending=False)
    
    # --- METRICS ROW ---
    col1, col2, col3, col4 = st.columns(4)
    
    total_pkts = len(df)
    benign_count = len(df[df['prediction_class'] == 'Benign'])
    threat_count = total_pkts - benign_count
    
    # Calculate percentage
    if total_pkts > 0:
        threat_rate = (threat_count / total_pkts) * 100
    else:
        threat_rate = 0
    
    latest_event = df.iloc[0]
    last_threat = df[df['prediction_class'] != 'Benign'].iloc[0] if threat_count > 0 else None
    
    with col1:
        st.metric(label="Total Analyzed Packets", value=total_pkts)
    with col2:
        st.metric(label="Benign Traffic", value=benign_count)
    with col3:
        st.metric(label="Threat Detected", value=threat_count, delta=f"{threat_rate:.1f}% Rate", delta_color="inverse")
    with col4:
        status_label = "SAFE" if latest_event['prediction_class'] == 'Benign' else "ALERT"
        st.metric(label="Current Status", value=status_label)

    # --- CHARTS ---
    st.markdown("---")
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("Traffic Classification Distribution")
        # Pie Chart
        counts = df['prediction_class'].value_counts().reset_index()
        counts.columns = ['Category', 'Count']
        
        fig_pie = px.pie(counts, values='Count', names='Category', hole=0.4, 
                         color='Category',
                         color_discrete_map={
                             'Benign': '#00CC96', 
                             'DDoS': '#EF553B', 
                             'Brute Force': '#FFA15A', 
                             'Other': '#AB63FA'
                         })
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.subheader("Confidence Levels")
        # Histogram of confidence
        fig_hist = px.histogram(df, x="confidence", nbins=20, title="Model Confidence Distribution",
                                color_discrete_sequence=['#636EFA'])
        st.plotly_chart(fig_hist, use_container_width=True)

    # --- LATEST ALERT & MITIGATION ---
    st.markdown("### 🚨 Latest Threat Mitigation")
    
    if last_threat is not None:
        alert_col1, alert_col2 = st.columns(2)
        
        with alert_col1:
            st.error(f"Detected: {last_threat['prediction_class']}")
            st.markdown(f"**Threat Type:** {last_threat['threat_type']}")
            st.markdown(f"**Response Mode:** {last_threat['response_mode']}")
            st.markdown(f"**Confidence:** {last_threat['confidence']:.4f}")
            st.markdown(f"**Timestamp:** {last_threat['timestamp']}")
            
        with alert_col2:
            st.write("**Recommended Mitigation Actions:**")
            actions = last_threat.get('mitigation_actions', [])
            for action in actions:
                st.info(action)
    else:
        st.success("No threats detected in the recent history.")

    # --- RAW DATA TABLE ---
    st.markdown("### 📋 Recent Traffic Log")
    st.dataframe(
        df[['timestamp', 'prediction_class', 'confidence', 'threat_type', 'response_mode', 'input_summary']],
        use_container_width=True
    )

# --- AUTO REFRESH LOGIC (MUST BE AT THE END) ---
if auto_refresh:
    time.sleep(REFRESH_RATE)
    st.rerun()
