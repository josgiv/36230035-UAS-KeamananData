import streamlit as st
import pandas as pd
import requests
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import uuid
import random

# ==============================================================================
# CONFIG & PAGE SETUP
# ==============================================================================
st.set_page_config(
    page_title="ShieldGuard SOC - Advanced IDS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Constants from React App
API_URL = "http://localhost:8000"
REFRESH_RATE = 2  # Seconds (matches Recharts 2000ms)

COLORS = {
    "Benign": "#10B981",       # Emerald
    "DDoS": "#EF4444",         # Red
    "Brute Force": "#F59E0B",  # Amber
    "Other": "#8B5CF6",        # Violet
}

# Mock Data for Simulation (Ported from page.tsx)
MOCK_IPS = ["192.168.1.105", "10.0.5.22", "203.114.12.5", "172.16.0.44", "45.33.22.11", "88.99.100.50", "12.34.56.78", "77.88.99.10"]
MOCK_HASHES = ["e5d3...8a2f", "99a1...b2c3", "malware_win32.exe", "trojan_dropper.bat", "ransomware.dll", "keylogger_v2.exe", "backdoor.sh"]
MOCK_USERS = ["admin_sys", "root", "user_service", "database_admin", "guest_wifi", "backup_operator", "web_service", "ftp_admin"]

ACTIONS_TEMPLATE = {
    "NETWORK": [
        {"type": "BLOCK", "template": "Blocking source IP {target} via firewall rule #442"},
        {"type": "THROTTLE", "template": "Applying QoS limit (10kbps) on flow from {target}"},
        {"type": "BLOCK", "template": "Adding {target} to IP blacklist (24h TTL)"},
        {"type": "THROTTLE", "template": "Rate limiting connections from {target} to 5/min"},
        {"type": "BLOCK", "template": "Dropping all packets from {target} on port 443"},
        {"type": "TRACE", "template": "Capturing packet dump for traffic from {target}"},
    ],
    "ENDPOINT": [
        {"type": "QUARANTINE", "template": "Isolating file hash {target} to Sandbox"},
        {"type": "TRACE", "template": "Tracing process origin for {target}"},
        {"type": "QUARANTINE", "template": "Moving {target} to quarantine zone"},
        {"type": "BLOCK", "template": "Killing process associated with {target}"},
        {"type": "TRACE", "template": "Analyzing memory dump for {target}"},
        {"type": "QUARANTINE", "template": "Preventing execution of {target} system-wide"},
    ],
    "IDENTITY": [
        {"type": "LOCK", "template": "Locking account {target} due to repeated failures"},
        {"type": "ISOLATE", "template": "Terminating active sessions for {target}"},
    ]
}

# ==============================================================================
# CSS STYLING (Theming to match page.tsx)
# ==============================================================================
st.markdown("""
<style>
    /* Global Background */
    .stApp {
        background-color: #020617; /* slate-950 */
        color: #f8fafc; /* slate-50 */
    }
    
    /* Metrics Cards */
    div[data-testid="metric-container"] {
        background-color: rgba(15, 23, 42, 0.5); /* slate-900/50 */
        border: 1px solid #1e293b; /* slate-800 */
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #f8fafc !important;
    }
    
    /* Tables */
    .stDataFrame {
         border: 1px solid #1e293b;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(30, 41, 59, 0.5);
        padding: 10px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 5px;
        color: #94a3b8;
        font-size: 14px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: rgba(59, 130, 246, 0.2);
        color: #60a5fa;
        font-weight: bold;
    }

    /* Custom Identity Header */
    .identity-header {
        display: flex;
        justify-content: space-between;
        background-color: #0f172a; /* slate-900 */
        border-bottom: 1px solid #1e293b;
        padding: 8px 15px;
        font-family: monospace;
        font-size: 11px;
        color: #94a3b8;
        margin-bottom: 20px;
        border-radius: 5px;
    }
    .id-section { display: flex; gap: 15px; }
    .text-cyan { color: #22d3ee; font-weight: bold; }
    .text-emerald { color: #34d399; font-weight: bold; }

    /* Custom Badge */
    .badge {
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: bold;
        text-transform: uppercase;
        display: inline-block;
    }
    .badge-benign { background-color: rgba(16, 185, 129, 0.2); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-ddos { background-color: rgba(239, 68, 68, 0.2); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-brute { background-color: rgba(245, 158, 11, 0.2); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-other { background-color: rgba(139, 92, 246, 0.2); color: #8B5CF6; border: 1px solid rgba(139, 92, 246, 0.3); }

    /* Mitigation Card */
    .mitigation-card {
        border: 1px solid #1e293b;
        background-color: rgba(15, 23, 42, 0.5);
        border-radius: 10px;
        padding: 15px;
        margin-top: 10px;
    }
    .mitigation-danger {
        background-color: rgba(69, 10, 10, 0.2);
        border: 1px solid rgba(239, 68, 68, 0.5);
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.1);
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# STATE & LOGIC
# ==============================================================================
# Initialize Session State
if 'history' not in st.session_state:
    st.session_state.history = []     # List of predictions
if 'action_log' not in st.session_state:
    st.session_state.action_log = []  # List of simulated actions
if 'seen_prediction_ids' not in st.session_state:
    st.session_state.seen_prediction_ids = set()

def fetch_data():
    """Fetch history from API and handle action simulation."""
    try:
        r = requests.get(f"{API_URL}/history", timeout=1)
        if r.status_code == 200:
            data = r.json()
            
            # Process new predictions for Action Simulation
            for prediction in data:
                pid = prediction.get('prediction_id')
                pclass = prediction.get('prediction_class')
                
                # If new and NOT Benign, trigger random actions
                if pid not in st.session_state.seen_prediction_ids:
                    st.session_state.seen_prediction_ids.add(pid)
                    if pclass != 'Benign':
                        trigger_random_action(pclass)
            
            # Sync history
            st.session_state.history = data
            return data
    except Exception as e:
        # st.error(f"Connection Error: {e}")
        return []
    return []

def trigger_random_action(threat_type):
    """Simulate SOC mitigation actions based on threat type."""
    num_actions = random.randint(2, 4)
    categories = ["NETWORK", "ENDPOINT", "IDENTITY"]
    
    new_logs = []
    
    for i in range(num_actions):
        # 1. Determine Category & Target
        category = "NETWORK" # Default
        target = "Unknown"
        
        # Rule: First action matches threat type strongly
        if i == 0:
            if threat_type == "DDoS":
                category = "NETWORK"
                target = random.choice(MOCK_IPS)
            elif threat_type == "Brute Force":
                category = "IDENTITY"
                target = random.choice(MOCK_USERS)
            else:
                category = "ENDPOINT"
                target = random.choice(MOCK_HASHES)
        else:
            # Randomize subsequent actions
            category = random.choice(categories)
            if category == "NETWORK": target = random.choice(MOCK_IPS)
            elif category == "IDENTITY": target = random.choice(MOCK_USERS)
            else: target = random.choice(MOCK_HASHES)
            
        # 2. Select Template
        template_obj = random.choice(ACTIONS_TEMPLATE[category])
        details = template_obj["template"].replace("{target}", target)
        
        # 3. Create Log Entry
        log_entry = {
            "id": str(uuid.uuid4()),
            "time": datetime.now() + timedelta(milliseconds=i*100),
            "category": category,
            "type": template_obj["type"],
            "target": target,
            "details": details,
            "status": "EXECUTED"
        }
        new_logs.append(log_entry)
        
    # Prepend to log (newest first)
    st.session_state.action_log = new_logs + st.session_state.action_log
    # Keep only last 100
    st.session_state.action_log = st.session_state.action_log[:100]

# ==============================================================================
# LAYOUT RENDERING
# ==============================================================================

# 1. Identity Header
st.markdown("""
<div class="identity-header">
    <div class="id-section">
        <span>NAMA: <span class="text-cyan">JOSIA GIVEN SANTOSO</span></span>
        <span>|</span>
        <span>NIM: <span class="text-emerald">36230035</span></span>
    </div>
    <div class="id-section">
        <span>DOSEN: ALANIAH NISRINA, B.ENG., M.ENG.</span>
        <span>|</span>
        <span>MK: KEAMANAN DATA</span>
    </div>
</div>
""", unsafe_allow_html=True)

# 2. Main Title & Status
history = fetch_data()
df = pd.DataFrame(history)

# Derived Metrics
total_pkts = len(df)
if total_pkts > 0:
    benign_count = len(df[df['prediction_class'] == 'Benign'])
    ddos_count = len(df[df['prediction_class'] == 'DDoS'])
    brute_count = len(df[df['prediction_class'] == 'Brute Force'])
    other_count = len(df[df['prediction_class'] == 'Other'])
    threat_count = total_pkts - benign_count
    threat_rate = (threat_count / total_pkts) * 100
    
    # Sort by time desc
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp', ascending=False)
    
    newest_item = df.iloc[0] if not df.empty else None
    system_status = "SECURE"
    if newest_item is not None and newest_item['prediction_class'] != 'Benign':
        system_status = "CRITICAL"
else:
    benign_count, ddos_count, brute_count, other_count, threat_count, threat_rate = 0, 0, 0, 0, 0, 0.0
    newest_item = None
    system_status = "SECURE"

# Header Row
col_header_1, col_header_2 = st.columns([3, 1])
with col_header_1:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 15px;">
        <div style="background: rgba(16, 185, 129, 0.1); padding: 10px; border-radius: 50%;">
            <span style="font-size: 30px;">🛡️</span>
        </div>
        <div>
            <h1 style="margin: 0; background: linear-gradient(to right, #22d3ee, #3b82f6, #a855f7); -webkit-background-clip: text; color: transparent;">SHIELDGUARD SOC</h1>
            <p style="margin: 0; color: #94a3b8; font-size: 14px;">Advanced Network Intrusion Detection System</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_header_2:
    status_color = "#34d399" if system_status == "SECURE" else "#f43f5e"
    status_icon = "🔒" if system_status == "SECURE" else "🚨"
    st.markdown(f"""
    <div style="text-align: right;">
        <div style="text-transform: uppercase; letter-spacing: 1px; font-size: 10px; color: #64748b; font-weight: bold;">System Status</div>
        <div style="font-size: 24px; font-weight: bold; color: {status_color};">
            {status_icon} {system_status}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 3. Metric Cards (Grid)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Analyzed", total_pkts)
m2.metric("Benign Traffic", benign_count)
m3.metric("Threat Detected", threat_count, delta=f"{threat_count} Events", delta_color="inverse")
m4.metric("Threat Rate", f"{threat_rate:.1f}%")

st.markdown("<br>", unsafe_allow_html=True)

# 4. Main Charts (Left: Confidence, Right: Pie & Mitigation)
row_charts = st.columns([2, 1])

with row_charts[0]:
    # --- Confidence Area Chart ---
    st.markdown("### 📈 Confidence Trend")
    if not df.empty:
        # Take last 50 points, reverse for chart (old -> new)
        chart_df = df.head(50).iloc[::-1].copy()
        
        fig = px.area(chart_df, x="timestamp", y="confidence", 
                      template="plotly_dark",
                      color_discrete_sequence=['#3b82f6'])
        
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            height=250,
            xaxis=dict(showgrid=False, title=None),
            yaxis=dict(showgrid=True, gridcolor="#1e293b", range=[0, 1.1])
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available")
        
    # --- Live Traffic Table ---
    st.markdown("### 🖥️ Live Traffic Log")
    if not df.empty:
        # Build a nice table dataframe
        display_df = df.head(10).copy()
        
        # Display
        # Using HTML table for full control over badges
        table_html = '<table style="width:100%; border-collapse: collapse; color: #cbd5e1; font-size: 12px;">'
        table_html += '<thead style="background: #0f172a; border-bottom: 1px solid #334155;">'
        table_html += '<tr>'
        table_html += '<th style="text-align: left; padding: 8px;">TIMESTAMP</th>'
        table_html += '<th style="text-align: left; padding: 8px;">CLASS</th>'
        table_html += '<th style="text-align: left; padding: 8px;">CONFIDENCE</th>'
        table_html += '<th style="text-align: left; padding: 8px;">SUMMARY</th>'
        table_html += '</tr></thead><tbody>'
        
        for index, row in display_df.iterrows():
            ts = row['timestamp'].strftime('%H:%M:%S')
            cls = row['prediction_class']
            conf = row['confidence'] * 100
            summ = row['input_summary']
            
            # Badge Class
            badge_class = "badge-benign"
            if cls == "DDoS": badge_class = "badge-ddos"
            elif cls == "Brute Force": badge_class = "badge-brute"
            elif cls == "Other": badge_class = "badge-other"
            
            table_html += '<tr style="border-bottom: 1px solid #1e293b;">'
            table_html += f'<td style="padding: 8px; font-family: monospace;">{ts}</td>'
            table_html += f'<td style="padding: 8px;"><span class="badge {badge_class}">{cls}</span></td>'
            table_html += '<td style="padding: 8px;">'
            table_html += '<div style="display: flex; align-items: center; gap: 8px;">'
            table_html += '<div style="width: 50px; height: 6px; background: #334155; border-radius: 3px; overflow: hidden;">'
            table_html += f'<div style="width: {conf}%; height: 100%; background: #3b82f6;"></div>'
            table_html += '</div>'
            table_html += f'<span>{conf:.0f}%</span>'
            table_html += '</div></td>'
            table_html += f'<td style="padding: 8px; color: #94a3b8;">{summ}</td>'
            table_html += '</tr>'
            
        table_html += "</tbody></table>"
        st.markdown(table_html, unsafe_allow_html=True)

with row_charts[1]:
    # --- Pie Chart ---
    st.markdown("### Traffic Distribution")
    if total_pkts > 0:
        counts = df['prediction_class'].value_counts()
        pie_data = pd.DataFrame({'Class': counts.index, 'Count': counts.values})
        
        fig_pie = px.pie(pie_data, names='Class', values='Count', hole=0.6,
                         color='Class',
                         color_discrete_map=COLORS)
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=0, b=0),
            height=200,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- Active Mitigation Card ---
    is_critical = system_status == "CRITICAL"
    card_class = "mitigation-card mitigation-danger" if is_critical else "mitigation-card"
    
    mitigation_html = f'<div class="{card_class}">'
    mitigation_html += '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">'
    
    color_class = '#f87171' if is_critical else '#94a3b8'
    mitigation_html += f'<h3 style="margin: 0; font-size: 16px; display: flex; align-items: center; gap: 8px; color: {color_class}">'
    mitigation_html += '<span>⚡</span> Active Mitigation</h3>'
    
    if is_critical:
        mitigation_html += '<span class="badge badge-ddos">ACTIVE</span>'
    mitigation_html += '</div>'
    
    if is_critical and newest_item is not None:
        mitigation_html += '<div style="background: rgba(239, 68, 68, 0.1); padding: 10px; border-radius: 6px; border: 1px solid rgba(239, 68, 68, 0.2);">'
        mitigation_html += f'<h4 style="margin: 0 0 5px 0; color: #f87171;">{newest_item["threat_type"]}</h4>'
        mitigation_html += f'<p style="margin: 0 0 10px 0; font-size: 12px; color: #fecaca;">Confidence: {newest_item["confidence"]*100:.1f}%</p>'
        mitigation_html += '<hr style="border-color: rgba(239, 68, 68, 0.2); margin: 5px 0;">'
        mitigation_html += '<div style="display: grid; gap: 5px;">'
        
        for action in newest_item.get('mitigation_actions', [])[:3]:
            mitigation_html += f'<div style="display: flex; gap: 8px; font-size: 12px; color: #fee2e2;"><span>✔</span> {action}</div>'
            
        mitigation_html += '</div></div>'
    else:
        mitigation_html += '<div style="display: flex; flex-direction: column; align-items: center; padding: 20px; color: #64748b;">'
        mitigation_html += '<div style="font-size: 30px; opacity: 0.3;">🛡️</div>'
        mitigation_html += '<div style="font-weight: bold; margin-top: 5px;">System Secure</div>'
        mitigation_html += '<div style="font-size: 11px;">Monitoring active traffic</div>'
        mitigation_html += '</div>'
        
    mitigation_html += "</div>"
    st.markdown(mitigation_html, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. SOC Operations Center (Table with Tabs)
st.markdown("### 📟 Security Operations Center")

# Filter Log Data
logs = st.session_state.action_log
logs_df = pd.DataFrame(logs)
# Convert Time
if not logs_df.empty and 'time' in logs_df.columns:
    logs_df['time'] = pd.to_datetime(logs_df['time'])
    logs_df = logs_df.sort_values('time', ascending=False)

tab_all, tab_net, tab_end, tab_id = st.tabs(["All Events", "Network", "Endpoint", "Identity"])

def render_log_table(df_subset, category_color="slate"):
    if df_subset.empty:
        st.info("No events in this category.")
        return

    # Use a similar styling approach
    # Use a similar styling approach
    t_html = '<table style="width:100%; border-collapse: collapse; font-size: 12px; color: #cbd5e1;">'
    t_html += '<thead style="background: #1e293b; color: #94a3b8;">'
    t_html += '<tr>'
    t_html += '<th style="padding: 8px; text-align: left;">TIME</th>'
    t_html += '<th style="padding: 8px; text-align: left;">CATEGORY</th>'
    t_html += '<th style="padding: 8px; text-align: left;">TYPE</th>'
    t_html += '<th style="padding: 8px; text-align: left;">TARGET</th>'
    t_html += '<th style="padding: 8px; text-align: left;">DETAILS</th>'
    t_html += '<th style="padding: 8px; text-align: right;">STATUS</th>'
    t_html += '</tr></thead><tbody>'
    
    for idx, row in df_subset.iterrows():
        ts = row['time'].strftime('%H:%M:%S')
        cat = row['category']
        type_ = row['type']
        target = row['target']
        details = row['details']
        status = row['status']
        
        # Color Logic
        cat_style = "color: #94a3b8;"
        if cat == "NETWORK": cat_style = "color: #22d3ee; background: rgba(34, 211, 238, 0.1); padding: 2px 6px; border-radius: 4px; font-weight: bold;"
        elif cat == "ENDPOINT": cat_style = "color: #c084fc; background: rgba(192, 132, 252, 0.1); padding: 2px 6px; border-radius: 4px; font-weight: bold;"
        elif cat == "IDENTITY": cat_style = "color: #fbbf24; background: rgba(251, 191, 36, 0.1); padding: 2px 6px; border-radius: 4px; font-weight: bold;"
        
        t_html += '<tr style="border-bottom: 1px solid #334155;">'
        t_html += f'<td style="padding: 8px; font-family: monospace; color: #64748b;">{ts}</td>'
        t_html += f'<td style="padding: 8px;"><span style="{cat_style}">{cat}</span></td>'
        t_html += f'<td style="padding: 8px;"><span style="border: 1px solid #475569; padding: 2px 6px; border-radius: 4px; font-size: 10px;">{type_}</span></td>'
        t_html += f'<td style="padding: 8px;"><code style="background: #0f172a; padding: 2px 4px; border-radius: 3px; color: #f1f5f9;">{target}</code></td>'
        t_html += f'<td style="padding: 8px; color: #cbd5e1;">{details}</td>'
        t_html += f'<td style="padding: 8px; text-align: right; color: #34d399; font-weight: bold;">✔ {status}</td>'
        t_html += '</tr>'
        
    t_html += "</tbody></table>"
    st.markdown(t_html, unsafe_allow_html=True)

with tab_all:
    render_log_table(logs_df)
with tab_net:
    if not logs_df.empty:
        render_log_table(logs_df[logs_df['category'] == 'NETWORK'])
    else: st.info("No Data")
with tab_end:
    if not logs_df.empty:
        render_log_table(logs_df[logs_df['category'] == 'ENDPOINT'])
    else: st.info("No Data")
with tab_id:
    if not logs_df.empty:
        render_log_table(logs_df[logs_df['category'] == 'IDENTITY'])
    else: st.info("No Data")

# Auto-Refresh (Bottom)
time.sleep(REFRESH_RATE)
st.rerun()
