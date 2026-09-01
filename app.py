"""
CinePulse AI - Web Application
Agentic Cinema: The Blockbuster Hackathon
Google Cloud (Gemini) + ClickHouse Multi-Agent Intelligence Platform
"""

import os
import time
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

from database.clickhouse_manager import db_manager
from agents.director_agent import cinepulse_agent

# Configure Streamlit Page
st.set_page_config(
    page_title="CinePulse AI | Agentic Cinema Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Cinematic Dark Theme Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&family=Inter:wght@300;400;600;700&display=swap');
    
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
        font-family: 'Inter', sans-serif;
    }
    
    .cinema-header {
        background: linear-gradient(135deg, #1f2937 0%, #111827 50%, #0f172a 100%);
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    
    .cinema-title {
        font-family: 'Cinzel', serif;
        font-size: 2.3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #F59E0B, #FBBF24, #FDE68A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .cinema-subtitle {
        color: #9CA3AF;
        font-size: 1.05rem;
        margin-top: 6px;
    }
    
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 8px;
    }
    
    .badge-google {
        background-color: rgba(59, 130, 246, 0.2);
        color: #60A5FA;
        border: 1px solid #3B82F6;
    }
    
    .badge-clickhouse {
        background-color: rgba(245, 158, 11, 0.2);
        color: #FBBF24;
        border: 1px solid #F59E0B;
    }
    
    .badge-speed {
        background-color: rgba(16, 185, 129, 0.2);
        color: #34D399;
        border: 1px solid #10B981;
    }
    
    .agent-card {
        background-color: #161b22;
        border-left: 4px solid #F59E0B;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
    }
    
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    
    .sql-container {
        background-color: #0a0c10;
        border: 1px solid #2d333b;
        border-radius: 8px;
        padding: 12px;
        font-family: 'Courier New', monospace;
        color: #58a6ff;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/movie-projector.png", width=64)
    st.markdown("### 🎬 **CinePulse Control Room**")
    st.caption("Agentic Cinema Studio Orchestration Platform")
    
    st.markdown("---")
    st.markdown("#### 🤖 **Active Agent Crew**")
    st.markdown("""
    - 🎬 **The Director:** *Gemini 2.5 Flash Orchestrator*
    - 📊 **Technical Producer:** *ClickHouse SQL Engine*
    - 🏛️ **The Studio Head:** *Strategic ROI Synthesizer*
    """)
    
    st.markdown("---")
    st.markdown("#### ⚙️ **Connection Settings**")
    
    api_key_input = st.text_input(
        "Google Gemini API Key", 
        value=os.getenv("GEMINI_API_KEY", ""), 
        type="password",
        help="Free key from Google AI Studio (aistudio.google.com)"
    )
    if api_key_input:
        cinepulse_agent.api_key = api_key_input
        cinepulse_agent._init_client()
        
    db_mode = "ClickHouse Cloud (Connected)" if db_manager.mode == "clickhouse" else "ClickHouse Engine (In-Memory Fast Mode)"
    st.info(f"💾 **Storage:** {db_mode}")
    
    with st.expander("🔌 ClickHouse Cloud Config"):
        ch_host = st.text_input("ClickHouse Host", value=os.getenv("CLICKHOUSE_HOST", "localhost"))
        ch_pw = st.text_input("ClickHouse Password", value=os.getenv("CLICKHOUSE_PASSWORD", ""), type="password")
        if st.button("Reconnect to ClickHouse"):
            os.environ["CLICKHOUSE_HOST"] = ch_host
            os.environ["CLICKHOUSE_PASSWORD"] = ch_pw
            db_manager._init_connection()
            st.rerun()

    st.markdown("---")
    if st.button("🔄 Refresh / Re-Seed Cinema Data"):
        db_manager._seed_local_engine()
        st.success("Successfully refreshed 4 cinematic datasets!")

# ----------------- HEADER -----------------
st.markdown("""
<div class="cinema-header">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 class="cinema-title">🎬 CinePulse AI</h1>
            <p class="cinema-subtitle">Autonomous Box Office, Streaming Telemetry & Multi-Agent Intelligence Engine</p>
        </div>
        <div style="text-align: right;">
            <span class="badge-pill badge-google">⚡ Google Gemini 2.5</span>
            <span class="badge-pill badge-clickhouse">⚡ ClickHouse Track</span>
            <span class="badge-pill badge-speed">🚀 Sub-10ms SQL</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- QUICK SCENARIO SELECTOR -----------------
st.markdown("##### 🎭 **Quick Studio Executive Scenarios**")
col1, col2, col3, col4 = st.columns(4)

scenario_prompt = ""
with col1:
    if st.button("📉 Scene Churn & Drop-offs", use_container_width=True):
        scenario_prompt = "Identify which scenes have the highest viewer drop-off counts and analyze pacing vs churn risk."

with col2:
    if st.button("💰 Box Office vs Marketing ROI", use_container_width=True):
        scenario_prompt = "Analyze global box office grosses and marketing spend efficiency across North America, Europe, and Asia."

with col3:
    if st.button("💬 Audience Sentiment Polarity", use_container_width=True):
        scenario_prompt = "What is the audience sentiment across X (Twitter), Reddit, and Letterboxd, and what are top viewer complaints?"

with col4:
    if st.button("🌐 Regional Streaming Health", use_container_width=True):
        scenario_prompt = "Compare streaming completion rates and buffering events across different device types and geographical territories."

# ----------------- QUERY INPUT BOX -----------------
default_val = scenario_prompt if scenario_prompt else "Why are viewers dropping off in early scenes, and what operational adjustments should the studio make?"
user_query = st.text_area("💬 **Ask the CinePulse Multi-Agent Studio Crew:**", value=default_val, height=80)

btn_col1, btn_col2 = st.columns([1, 5])
with btn_col1:
    run_clicked = st.button("🚀 **Direct AI Agents**", type="primary", use_container_width=True)

# ----------------- AGENT EXECUTION & RESULTS -----------------
if run_clicked or scenario_prompt:
    with st.spinner("🎬 The Director Agent is formulating the analytical plan and querying ClickHouse..."):
        start_time = time.perf_counter()
        trace = cinepulse_agent.run_workflow(user_query)
        total_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        
    st.markdown("---")
    st.markdown("### 🎥 **Multi-Agent Cinematic Execution Trace**")
    
    # Trace Metrics Bar
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"<div class='metric-card'><div style='color:#9CA3AF;font-size:0.85rem;'>Director Orchestrator</div><div style='color:#60A5FA;font-size:1.4rem;font-weight:700;'>Gemini 2.5 Flash</div></div>", unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"<div class='metric-card'><div style='color:#9CA3AF;font-size:0.85rem;'>Database Engine</div><div style='color:#FBBF24;font-size:1.4rem;font-weight:700;'>ClickHouse SQL</div></div>", unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"<div class='metric-card'><div style='color:#9CA3AF;font-size:0.85rem;'>ClickHouse Query Time</div><div style='color:#34D399;font-size:1.4rem;font-weight:700;'>{trace['total_sql_time_ms']} ms</div></div>", unsafe_allow_html=True)
    with m_col4:
        st.markdown(f"<div class='metric-card'><div style='color:#9CA3AF;font-size:0.85rem;'>Total Agent Latency</div><div style='color:#E6EDF3;font-size:1.4rem;font-weight:700;'>{total_time_ms} ms</div></div>", unsafe_allow_html=True)
        
    st.write("")
    
    # Step 1: Director Thought
    with st.expander("🎬 **Step 1: The Director's Investigation Strategy**", expanded=True):
        st.markdown(f"> *{trace['director_thought']}*")
        
    # Step 2: Technical Producer (ClickHouse SQL Execution)
    with st.expander("📊 **Step 2: The Technical Producer (ClickHouse SQL Execution & Telemetry)**", expanded=True):
        for i, q in enumerate(trace["query_results"]):
            st.markdown(f"**Query #{i+1} Executed in `{q['time_ms']} ms` on `{q['engine']}` ({q['rows']} rows returned):**")
            st.code(q["sql"], language="sql")
            
        if trace["dataframes"]:
            st.markdown("##### 📋 **Live Query Result Data Snapshot**")
            st.dataframe(trace["dataframes"][0].head(15), use_container_width=True)
            
    # Dynamic Plotly Visualizations based on Data
    if trace["dataframes"] and not trace["dataframes"][0].empty:
        df_plot = trace["dataframes"][0]
        st.markdown("### 📈 **Cinematic Telemetry Visualizations**")
        v_col1, v_col2 = st.columns(2)
        
        with v_col1:
            if "minute_mark" in df_plot.columns and "viewer_drop_count" in df_plot.columns:
                fig1 = px.bar(
                    df_plot, 
                    x="minute_mark", 
                    y="viewer_drop_count", 
                    color="scene_type",
                    title="Viewer Churn Spikes by Scene Timeline (Minute Mark)",
                    labels={"minute_mark": "Timeline Minute", "viewer_drop_count": "Viewer Drop Count"},
                    template="plotly_dark"
                )
                st.plotly_chart(fig1, use_container_width=True)
            elif "total_gross_usd" in df_plot.columns and "region" in df_plot.columns:
                fig1 = px.pie(
                    df_plot, 
                    names="region", 
                    values="total_gross_usd", 
                    title="Global Box Office Gross Distribution by Region",
                    template="plotly_dark",
                    hole=0.4
                )
                st.plotly_chart(fig1, use_container_width=True)
            elif "platform" in df_plot.columns and "review_count" in df_plot.columns:
                fig1 = px.bar(
                    df_plot,
                    x="platform",
                    y="review_count",
                    color="sentiment_label",
                    title="Social Platform Audience Review Distribution",
                    template="plotly_dark"
                )
                st.plotly_chart(fig1, use_container_width=True)
            else:
                num_cols = df_plot.select_dtypes(include=['float64', 'int64', 'int32']).columns
                if len(num_cols) >= 1:
                    fig1 = px.bar(df_plot.head(10), x=df_plot.columns[0], y=num_cols[0], template="plotly_dark", title=f"{num_cols[0]} by {df_plot.columns[0]}")
                    st.plotly_chart(fig1, use_container_width=True)
                    
        with v_col2:
            if "pacing_score" in df_plot.columns and "churn_risk_score" in df_plot.columns:
                fig2 = px.scatter(
                    df_plot,
                    x="pacing_score",
                    y="churn_risk_score",
                    color="emotional_tone",
                    size="viewer_drop_count",
                    title="Scene Pacing Intensity vs Churn Risk Score",
                    template="plotly_dark"
                )
                st.plotly_chart(fig2, use_container_width=True)
            elif "marketing_roi" in df_plot.columns:
                fig2 = px.bar(
                    df_plot,
                    x="region",
                    y="marketing_roi",
                    color="title",
                    title="Marketing Spend ROI Multiplier by Market",
                    template="plotly_dark"
                )
                st.plotly_chart(fig2, use_container_width=True)
            elif "avg_sentiment" in df_plot.columns:
                fig2 = px.line(
                    df_plot,
                    x="platform",
                    y="avg_sentiment",
                    markers=True,
                    title="Audience Sentiment Polarity (-1.0 to +1.0)",
                    template="plotly_dark"
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                if len(trace["dataframes"]) > 1 and not trace["dataframes"][1].empty:
                    df2 = trace["dataframes"][1]
                    num_cols2 = df2.select_dtypes(include=['float64', 'int64', 'int32']).columns
                    if len(num_cols2) >= 1:
                        fig2 = px.line(df2, x=df2.columns[0], y=num_cols2[0], template="plotly_dark", title=f"Trend: {num_cols2[0]}")
                        st.plotly_chart(fig2, use_container_width=True)

    # Step 3: Executive Strategy Brief
    st.markdown("### 🏛️ **Step 3: The Studio Head (Executive Strategic Brief)**")
    st.markdown(f"""
    <div style="background-color:#161b22; border: 1px solid #30363d; border-radius:12px; padding:24px;">
        {trace['executive_brief']}
    </div>
    """, unsafe_allow_html=True)

# ----------------- FOOTER -----------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 0.85rem;">
    🎬 <b>CinePulse AI</b> | Built for <b>Agentic Cinema: The Blockbuster Hackathon</b><br>
    Powered by <b>Google Cloud (Gemini)</b> & <b>ClickHouse Real-Time Analytics</b> | Open Source MIT License
</div>
""", unsafe_allow_html=True)
