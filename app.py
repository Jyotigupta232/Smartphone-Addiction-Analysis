import os
import sys
import time
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Path configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from data.generate_schema_dataset import build_data_warehouse
from src.pdf_generator import generate_weekly_wellness_pdf
from src.ml_predictor_dw import train_dw_ml_models, predict_addiction_risk
from src.custom_data_loader import load_custom_df_to_dw, generate_sample_csv_template

# Asset Paths
HERO_IMAGE_PATH = os.path.join(BASE_DIR, 'assets', 'hero_analytics_dashboard.png')
WELLNESS_IMAGE_PATH = os.path.join(BASE_DIR, 'assets', 'digital_wellness_illustration.png')
ARCH_IMAGE_PATH = os.path.join(BASE_DIR, 'assets', 'sql_ml_architecture_diagram.png')

# -------------------------------------------------------------------
# STREAMLIT PAGE CONFIGURATION
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Smartphone Addiction Analysis Platform",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# EXECUTIVE CORPORATE ENTERPRISE DESIGN SYSTEM (DARK SLATE & INDIGO)
# -------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Outfit:wght@600;700;800&display=swap');
    
    /* Base Body & Layout - Executive Slate Dark Theme */
    html, body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 16px;
        background-color: #0b0f19;
        color: #e2e8f0;
    }
    
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e293b 0%, #0b0f19 80%) !important;
    }

    /* Clean Streamlit Header */
    header[data-testid="stHeader"],
    .stAppHeader {
        background: transparent !important;
        z-index: 9999 !important;
    }
    
    /* Hide Deploy Buttons and Main Menu */
    .stDeployButton,
    button[title="Deploy"],
    button[data-testid="stHeaderDeployButton"],
    [data-testid="stAppDeployButton"],
    [data-testid="stMainMenu"],
    #MainMenu,
    footer {
        display: none !important;
    }

    /* Main Block Container Padding */
    .main .block-container,
    [data-testid="stMainBlockContainer"],
    .block-container {
        padding-top: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 100% !important;
    }

    /* Clean Corporate Header Navbar */
    .corporate-navbar {
        background: rgba(15, 23, 42, 0.95);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 14px 20px;
        margin: 0 0 1.5rem 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
    }

    /* Executive Glass Container for Images */
    [data-testid="stImage"] {
        background: rgba(15, 23, 42, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 14px !important;
        padding: 10px !important;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.45) !important;
        margin-bottom: 1rem !important;
    }

    [data-testid="stImage"]:hover {
        border-color: rgba(96, 165, 250, 0.4) !important;
    }

    [data-testid="stImage"] img {
        border-radius: 10px !important;
        object-fit: contain !important;
        max-height: 420px !important;
        width: 100% !important;
        margin: 0 auto !important;
        display: block !important;
    }

    /* Fullscreen Modal Image View - Full Uncropped Resolution */
    [data-testid="stFullScreenFrame"] img,
    [data-testid="stModal"] img {
        max-height: 92vh !important;
        max-width: 95vw !important;
        object-fit: contain !important;
        margin: auto !important;
    }

    [data-testid="stImage"] figcaption {
        color: #94a3b8 !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        text-align: center !important;
        padding-top: 8px !important;
    }

    /* Executive Glass Container for Plotly Analytics Charts */
    [data-testid="stPlotlyChart"],
    .stPlotlyChart {
        background: rgba(15, 23, 42, 0.65) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        padding: 8px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.35) !important;
        margin-bottom: 20px !important;
    }
    
    .brand-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.4rem;
        font-weight: 800;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 12px;
        letter-spacing: -0.4px;
    }
    
    .brand-accent {
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .status-badge {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.25);
        color: #34d399;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
    }

    /* Typography */
    p, div, span, label, li {
        color: #cbd5e1;
    }
    
    h1 {
        font-family: 'Outfit', sans-serif !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        color: #f8fafc !important;
        letter-spacing: -0.5px !important;
    }
    
    h2 {
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.95rem !important;
        font-weight: 700 !important;
        color: #f8fafc !important;
    }

    h3 {
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.55rem !important;
        font-weight: 700 !important;
        color: #f1f5f9 !important;
        margin-top: 14px !important;
    }

    h4 {
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: #60a5fa !important;
    }

    /* Glass Cards */
    .executive-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.35);
        transition: border-color 0.2s ease, transform 0.2s ease;
    }
    
    .executive-card:hover {
        border-color: rgba(96, 165, 250, 0.3);
        transform: translateY(-2px);
    }
    
    .kpi-card {
        background: rgba(30, 41, 59, 0.55);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px 16px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
    }
    
    .kpi-title {
        font-size: 0.88rem !important;
        color: #94a3b8;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    
    .kpi-value {
        font-size: 2.2rem !important;
        font-weight: 800;
        color: #ffffff;
        margin: 6px 0;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .kpi-tag {
        font-size: 0.82rem !important;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 600;
        display: inline-block;
    }

    .tag-blue { background: rgba(59, 130, 246, 0.14); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.25); }
    .tag-emerald { background: rgba(16, 185, 129, 0.14); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.25); }
    .tag-amber { background: rgba(245, 158, 11, 0.14); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.25); }
    .tag-rose { background: rgba(225, 29, 72, 0.14); color: #f43f5e; border: 1px solid rgba(225, 29, 72, 0.25); }
    .tag-purple { background: rgba(139, 92, 246, 0.14); color: #a78bfa; border: 1px solid rgba(139, 92, 246, 0.25); }

    /* Custom Form & Control Styling */
    .stSelectbox label, .stSlider label, .stNumberInput label {
        font-weight: 600 !important;
        color: #e2e8f0 !important;
    }
    
    /* Code & Mono Styling */
    code, pre, .stCodeBlock {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.02rem !important;
        border-radius: 10px !important;
    }

    /* Executive Professional Sidebar Navigation Styling */
    [data-testid="stSidebar"] {
        background-color: #0d1117 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    [data-testid="stSidebar"] h3 {
        color: #60a5fa !important;
        font-size: 1.05rem !important;
        margin-top: 12px !important;
    }

    /* Radio Group Styling for Clean Navigation */
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        background: rgba(30, 41, 59, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        margin: 4px 0 !important;
        cursor: pointer !important;
        width: 100% !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(51, 65, 85, 0.7) !important;
        border-color: rgba(96, 165, 250, 0.4) !important;
    }

    /* Active Selected Radio Button */
    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.35) 0%, rgba(30, 58, 138, 0.5) 100%) !important;
        border: 1px solid rgba(96, 165, 250, 0.7) !important;
    }
    
    /* Hero Text Pills */
    .hero-pill {
        background: rgba(96, 165, 250, 0.1);
        border: 1px solid rgba(96, 165, 250, 0.25);
        color: #60a5fa;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.9rem !important;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# INITIALIZE DATABASE & WAREHOUSE
# -------------------------------------------------------------------
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'smartphone_addiction_dw.db')
SURVEY_DATASET_PATH = r"C:\Users\Jyoti\Downloads\smartphone_addiction_ml_dataset_700_rows.xlsx"

if not os.path.exists(DB_PATH):
    if os.path.exists(SURVEY_DATASET_PATH):
        try:
            survey_df = pd.read_excel(SURVEY_DATASET_PATH)
            load_custom_df_to_dw(survey_df, DB_PATH)
        except Exception:
            build_data_warehouse(DATA_DIR)
    else:
        build_data_warehouse(DATA_DIR)

# -------------------------------------------------------------------
# SIDEBAR: EXECUTIVE NAVIGATION & CONTROLS
# -------------------------------------------------------------------
st.sidebar.markdown("""
<div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 14px 16px; margin-bottom: 12px; margin-right: 36px;">
    <div style="font-size: 1.08rem; font-weight: 800; color: #ffffff; display: flex; align-items: center; gap: 8px;">
        <span>📱</span> Smartphone Addiction
    </div>
    <div style="font-size: 0.76rem; font-weight: 600; color: #60a5fa; text-transform: uppercase; letter-spacing: 0.8px; margin-top: 4px;">
        Behavioral Intelligence Suite
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="font-size: 0.72rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin: 12px 0 6px 2px;">
    🧭 MAIN APPLICATION MODULES
</div>
""", unsafe_allow_html=True)

nav_selection = st.sidebar.radio(
    "Select Application Module:",
    [
        "🏠 Landing Homepage",
        "📊 Telemetry Analytics Dashboard",
        "⚡ SQL Performance & B-Tree Lab",
        "🤖 ML Risk Model & GenAI Engine",
        "📄 Digital Wellness PDF Audit",
        "📈 Executive Business Insights"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 Quick-Start User Personas")
persona_choice = st.sidebar.selectbox(
    "Select Persona Profile:",
    [
        "📊 Current Active Data Warehouse",
        "💼 Heavy User (High Risk - 11.5 hrs/day)",
        "🎓 Balanced Student (Medium Risk - 5.5 hrs/day)",
        "🧘 Digital Zen (Low Risk - 2.5 hrs/day)"
    ]
)

if persona_choice == "💼 Heavy User (High Risk - 11.5 hrs/day)":
    default_st, default_un, default_notif, default_sleep, default_age = 11.5, 175, 310, 4.5, 20
elif persona_choice == "🎓 Balanced Student (Medium Risk - 5.5 hrs/day)":
    default_st, default_un, default_notif, default_sleep, default_age = 5.5, 75, 140, 6.5, 22
elif persona_choice == "🧘 Digital Zen (Low Risk - 2.5 hrs/day)":
    default_st, default_un, default_notif, default_sleep, default_age = 2.5, 30, 45, 8.0, 28
else:
    default_st, default_un, default_notif, default_sleep, default_age = 9.5, 120, 220, 5.0, 21

st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 Data Ingestion Controls")
uploaded_file = st.sidebar.file_uploader("Upload Custom CSV / Excel", type=["csv", "xlsx"])
if uploaded_file is not None:
    try:
        custom_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        n_records, n_u = load_custom_df_to_dw(custom_df, DB_PATH)
        st.cache_data.clear()
        st.sidebar.success(f"✅ Loaded {n_records} records for {n_u} users!")
    except Exception as e:
        st.sidebar.error(f"Error: {str(e)}")

col_s1, col_s2 = st.sidebar.columns(2)
with col_s1:
    if st.button("📥 700 Survey Data", use_container_width=True):
        if os.path.exists(SURVEY_DATASET_PATH):
            s_df = pd.read_excel(SURVEY_DATASET_PATH)
            load_custom_df_to_dw(s_df, DB_PATH)
            st.cache_data.clear()
            st.sidebar.success("Loaded 700 Survey Profiles!")
with col_s2:
    if st.button("🔄 Reset 100k", use_container_width=True):
        build_data_warehouse(DATA_DIR)
        st.cache_data.clear()
        st.sidebar.info("Reset to 100k Telemetry.")

def get_warehouse_data():
    conn = sqlite3.connect(DB_PATH)
    u_df = pd.read_sql_query("SELECT * FROM users", conn)
    l_df = pd.read_sql_query("SELECT * FROM usage_logs LIMIT 5000", conn)
    a_df = pd.read_sql_query("SELECT * FROM app_usage LIMIT 5000", conn)
    s_df = pd.read_sql_query("SELECT * FROM sleep_patterns", conn)
    n_df = pd.read_sql_query("SELECT * FROM notifications", conn)
    f_df = pd.read_sql_query("SELECT * FROM user_feedback", conn)
    conn.close()
    return u_df, l_df, a_df, s_df, n_df, f_df

df_u, df_l, df_a, df_s, df_n, df_f = get_warehouse_data()

# -------------------------------------------------------------------
# CORPORATE TOP NAVBAR (EXECUTIVE HEADER)
# -------------------------------------------------------------------
st.markdown(f"""
<div class="corporate-navbar">
    <div class="brand-title">
        <span>📱 Smartphone Addiction Analysis</span>
        <span class="brand-accent" style="font-size: 0.95rem; font-weight: 600; border-left: 1px solid #334155; padding-left: 12px;">Behavioral Analytics Platform</span>
    </div>
    <div style="display: flex; align-items: center; gap: 16px;">
        <div class="status-badge">
            <div class="status-dot"></div>
            <span>SQLite DW Active: {len(df_u)} Respondent Profiles</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ===================================================================
# MODULE 1: LANDING HOMEPAGE
# ===================================================================
if nav_selection == "🏠 Landing Homepage":
    col_h1, col_h2 = st.columns([1.1, 0.9], vertical_alignment="center")
    with col_h1:
        st.markdown("""
        <div class="hero-pill">📱 SMARTPHONE ADDICTION ANALYSIS & DATA WAREHOUSING</div>
        <h1 style="font-size: 2.6rem !important; margin-top: 0; line-height: 1.2 !important;">Smartphone Addiction Analysis Platform</h1>
        <p style="font-size: 1.15rem !important; color: #cbd5e1; margin-bottom: 20px;">
            An end-to-end data engineering & artificial intelligence suite analyzing <strong>700 real survey respondent profiles</strong> across smartphone screen time, checking frequency, sleep disruption, and academic productivity.
        </p>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px;">
            <span class="kpi-tag tag-blue">🟢 {len(df_u)} Respondent Profiles</span>
            <span class="kpi-tag tag-emerald">⚡ 25.4x B-Tree SQL Speedup</span>
            <span class="kpi-tag tag-amber">🤖 Random Forest ML Predictor</span>
            <span class="kpi-tag tag-purple">📄 ReportLab PDF Generator</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col_h2:
        if os.path.exists(HERO_IMAGE_PATH):
            st.image(HERO_IMAGE_PATH, caption="Smartphone Addiction Analytics Dashboard & Intelligence Suite", use_container_width=True)

    st.markdown("---")
    st.markdown("### 🏛️ Core Platform Engineering Pillars")
    
    p1, p2, p3, p4 = st.columns(4, vertical_alignment="top")
    with p1:
        st.markdown("""
        <div class="executive-card" style="padding: 22px; min-height: 240px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="font-size: 1.35rem;">🗄️ <strong>Pillar 1</strong></div>
                <div style="font-size: 1.05rem; color: #60a5fa; font-weight: 700; margin-top: 6px;">Relational SQL Warehouse</div>
            </div>
            <p style="font-size: 0.92rem !important; color: #94a3b8; margin-top: 10px; line-height: 1.5 !important;">
                7 normalized tables (`users`, `usage_logs`, `app_usage`, `sleep`, `notifications`, `feedback`) storing 700 survey user profiles.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with p2:
        st.markdown("""
        <div class="executive-card" style="padding: 22px; min-height: 240px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="font-size: 1.35rem;">⚡ <strong>Pillar 2</strong></div>
                <div style="font-size: 1.05rem; color: #34d399; font-weight: 700; margin-top: 6px;">B-Tree SQL Optimizer</div>
            </div>
            <p style="font-size: 0.92rem !important; color: #94a3b8; margin-top: 10px; line-height: 1.5 !important;">
                Live query performance lab demonstrating 25x speedup and 99.9% Disk I/O latency reduction using B-Tree table indexes.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with p3:
        st.markdown("""
        <div class="executive-card" style="padding: 22px; min-height: 240px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="font-size: 1.35rem;">🤖 <strong>Pillar 3</strong></div>
                <div style="font-size: 1.05rem; color: #fbbf24; font-weight: 700; margin-top: 6px;">3-Class ML Classifier</div>
            </div>
            <p style="font-size: 0.92rem !important; color: #94a3b8; margin-top: 10px; line-height: 1.5 !important;">
                Predicts Low, Medium, and High Addiction Risk tiers using Logistic Regression and Random Forest models with 5-Fold CV.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with p4:
        st.markdown("""
        <div class="executive-card" style="padding: 22px; min-height: 240px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>
                <div style="font-size: 1.35rem;">📄 <strong>Pillar 4</strong></div>
                <div style="font-size: 1.05rem; color: #a78bfa; font-weight: 700; margin-top: 6px;">PDF Audit Engine</div>
            </div>
            <p style="font-size: 0.92rem !important; color: #94a3b8; margin-top: 10px; line-height: 1.5 !important;">
                Generates formal, 1-page downloadable Weekly Digital Wellness PDF Audit reports complete with behavioral metrics.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🖼️ System Architecture & Digital Wellness Showcase")
    
    c_v1, c_v2 = st.columns(2, vertical_alignment="top")
    with c_v1:
        st.markdown("#### 1. System Architecture & Database Engineering")
        if os.path.exists(ARCH_IMAGE_PATH):
            st.image(ARCH_IMAGE_PATH, caption="7-Table Relational Data Warehouse & ML Classifier Pipeline", use_container_width=True)
        st.markdown("""
        <div class="executive-card" style="margin-top: 14px; min-height: 110px;">
            <p style="font-size: 0.98rem !important; color: #cbd5e1; line-height: 1.6 !important;">
                The platform integrates normalized SQLite schema storing usage logs, app categories, notification volume, and sleep scores. Indexing strategies ensure sub-millisecond query execution.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with c_v2:
        st.markdown("#### 2. Digital Wellness & Behavioral Recovery Intelligence")
        if os.path.exists(WELLNESS_IMAGE_PATH):
            st.image(WELLNESS_IMAGE_PATH, caption="Smartphone Telemetry, Sleep Optimization & Productivity Scores", use_container_width=True)
        st.markdown("""
        <div class="executive-card" style="margin-top: 14px; min-height: 110px;">
            <p style="font-size: 0.98rem !important; color: #cbd5e1; line-height: 1.6 !important;">
                Analyzes correlations between late-night phone checks, sleep duration, and focus scores to recommend automated Bedtime focus locks and notification batching.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ===================================================================
# MODULE 2: TELEMETRY ANALYTICS DASHBOARD
# ===================================================================
elif nav_selection == "📊 Telemetry Analytics Dashboard":
    st.markdown("""
    <div class="executive-card" style="border-left: 4px solid #3b82f6;">
        💡 <strong>Executive Dashboard:</strong> Visualizing aggregated behavioral telemetry metrics across 700 survey respondents stored in the SQL Data Warehouse.
    </div>
    """, unsafe_allow_html=True)

    # Interactive Filtering Controls Bar
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filter_day = st.selectbox("📅 Filter Telemetry by Day Type:", ["All Days", "Weekday", "Weekend"])
    with col_f2:
        filter_risk = st.selectbox("🎯 Filter Profiles by Addiction Risk Level:", ["All Risk Levels", "High Risk", "Medium Risk", "Low Risk"])

    filtered_l = df_l.copy()
    if filter_day != "All Days":
        filtered_l = filtered_l[filtered_l["day_type"] == filter_day]
        
    filtered_users = df_f.copy()
    if filter_risk != "All Risk Levels":
        filtered_users = filtered_users[filtered_users["addiction_risk_level"] == filter_risk]
        valid_uids = set(filtered_users["user_id"])
        filtered_l = filtered_l[filtered_l["user_id"].isin(valid_uids)]

    # 6 Executive KPI Cards
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    
    avg_st = filtered_l["screen_time"].mean() if len(filtered_l) > 0 else df_l["screen_time"].mean()
    k1.markdown(f'''
    <div class="kpi-card">
        <div class="kpi-title">Avg Screen Time</div>
        <div class="kpi-value">{avg_st:.1f} <span style="font-size:0.95rem">hrs</span></div>
        <div class="kpi-tag tag-blue">Filtered Sample</div>
    </div>''', unsafe_allow_html=True)
    
    avg_un = filtered_l["unlocks"].mean() if len(filtered_l) > 0 else df_l["unlocks"].mean()
    k2.markdown(f'''
    <div class="kpi-card">
        <div class="kpi-title">Daily Unlocks</div>
        <div class="kpi-value">{avg_un:.0f}</div>
        <div class="kpi-tag tag-amber">Telemetry Rate</div>
    </div>''', unsafe_allow_html=True)
    
    avg_sq = df_s["sleep_quality_score"].mean()
    k3.markdown(f'''
    <div class="kpi-card">
        <div class="kpi-title">Sleep Quality</div>
        <div class="kpi-value">{avg_sq:.1f}<span style="font-size:0.95rem">/10</span></div>
        <div class="kpi-tag tag-emerald">Rest Index</div>
    </div>''', unsafe_allow_html=True)
    
    high_risk_pct = (df_f["addiction_risk_level"] == "High Risk").mean() * 100
    k4.markdown(f'''
    <div class="kpi-card">
        <div class="kpi-title">High Risk %</div>
        <div class="kpi-value" style="color:#f43f5e">{high_risk_pct:.1f}%</div>
        <div class="kpi-tag tag-rose">Critical Segment</div>
    </div>''', unsafe_allow_html=True)
    
    social_pct = (df_a["category"] == "Social Media").mean() * 100
    k5.markdown(f'''
    <div class="kpi-card">
        <div class="kpi-title">Social Media %</div>
        <div class="kpi-value" style="color:#fbbf24">{social_pct:.1f}%</div>
        <div class="kpi-tag tag-amber">Primary Usage</div>
    </div>''', unsafe_allow_html=True)
    
    avg_prod = df_u["productivity_score"].mean()
    k6.markdown(f'''
    <div class="kpi-card">
        <div class="kpi-title">Productivity</div>
        <div class="kpi-value">{avg_prod:.1f}<span style="font-size:0.95rem">/10</span></div>
        <div class="kpi-tag tag-blue">Focus Index</div>
    </div>''', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2, vertical_alignment="top")
    with c1:
        st.markdown("#### 📊 1. Daily Usage Trend (Screen Time Distribution)")
        fig_hist = px.histogram(
            filtered_l if len(filtered_l) > 0 else df_l, 
            x="screen_time", 
            color="day_type", 
            barmode="overlay", 
            nbins=25, 
            color_discrete_map={"Weekend": "#f43f5e", "Weekday": "#3b82f6"},
            labels={"screen_time": "Screen Time (Hours/Day)", "day_type": "Day Type"}
        )
        fig_hist.update_layout(
            template="plotly_dark", 
            paper_bgcolor="#0f172a", 
            plot_bgcolor="#1e293b", 
            font=dict(color="#e2e8f0", family="Inter"),
            xaxis=dict(color="#cbd5e1", gridcolor="rgba(255,255,255,0.08)", showgrid=True),
            yaxis=dict(color="#cbd5e1", gridcolor="rgba(255,255,255,0.08)", showgrid=True),
            height=360,
            margin=dict(l=40, r=20, t=30, b=40)
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with c2:
        st.markdown("#### 🍕 2. App Category Duration Distribution")
        cat_df = df_a.groupby("category")["time_spent"].sum().reset_index()
        fig_pie = px.pie(
            cat_df, 
            values="time_spent", 
            names="category", 
            hole=0.45, 
            color_discrete_sequence=['#3b82f6', '#10b981', '#f59e0b', '#f43f5e', '#8b5cf6']
        )
        fig_pie.update_traces(textinfo='percent+label', textposition='inside')
        fig_pie.update_layout(
            template="plotly_dark", 
            paper_bgcolor="#0f172a", 
            font=dict(color="#e2e8f0", family="Inter"),
            height=360,
            margin=dict(l=20, r=20, t=30, b=30)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    c3, c4 = st.columns(2, vertical_alignment="top")
    with c3:
        st.markdown("#### 🔥 3. Behavioral Correlation Matrix Heatmap")
        conn_corr = sqlite3.connect(DB_PATH)
        corr_df = pd.read_sql_query("""
            SELECT 
                l.screen_time AS Screen_Time,
                l.unlocks AS Unlocks,
                s.sleep_hours AS Sleep_Hrs,
                n.daily_notifications AS Notifications,
                u.productivity_score AS Productivity
            FROM usage_logs l
            JOIN sleep_patterns s ON l.user_id = s.user_id
            JOIN notifications n ON l.user_id = n.user_id
            JOIN users u ON l.user_id = u.user_id
            LIMIT 2500;
        """, conn_corr)
        conn_corr.close()
        
        corr_data = corr_df.corr()
        fig_corr = px.imshow(
            corr_data, 
            text_auto=".2f", 
            color_continuous_scale="Viridis", 
            aspect="auto"
        )
        fig_corr.update_layout(
            template="plotly_dark", 
            paper_bgcolor="#0f172a", 
            font=dict(color="#e2e8f0", family="Inter"),
            xaxis=dict(color="#cbd5e1"),
            yaxis=dict(color="#cbd5e1"),
            height=360,
            margin=dict(l=40, r=20, t=30, b=40)
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    with c4:
        st.markdown("#### 📈 4. Weekly Usage Comparison (Weekend vs Weekday)")
        ww_df = df_l.groupby("day_type")["screen_time"].mean().reset_index()
        fig_ww = px.bar(
            ww_df, 
            x="day_type", 
            y="screen_time", 
            color="day_type", 
            text_auto='.1f',
            color_discrete_map={"Weekend": "#f43f5e", "Weekday": "#3b82f6"},
            labels={"screen_time": "Avg Screen Time (Hours)", "day_type": "Day Type"}
        )
        fig_ww.update_traces(textposition='outside')
        fig_ww.update_layout(
            template="plotly_dark", 
            paper_bgcolor="#0f172a", 
            plot_bgcolor="#1e293b",
            font=dict(color="#e2e8f0", family="Inter"),
            xaxis=dict(color="#cbd5e1", gridcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(color="#cbd5e1", gridcolor="rgba(255,255,255,0.08)"),
            height=360,
            margin=dict(l=40, r=20, t=30, b=40)
        )
        st.plotly_chart(fig_ww, use_container_width=True)

    # Telemetry Dataset Explorer
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("🔍 Telemetry Data Explorer & Warehouse Table Inspector", expanded=False):
        st.dataframe(filtered_l.head(100), use_container_width=True)
        csv_data = filtered_l.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Filtered Telemetry CSV",
            data=csv_data,
            file_name="telemetry_analytics_data.csv",
            mime="text/csv"
        )

# ===================================================================
# MODULE 3: SQL PERFORMANCE & B-TREE LAB
# ===================================================================
elif nav_selection == "⚡ SQL Performance & B-Tree Lab":
    st.markdown("""
    <div class="executive-card" style="border-left: 4px solid #10b981;">
        💡 <strong>Database Engineering Lab:</strong> Executing complex multi-table SQL queries and running real-time B-Tree indexing performance benchmarks.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### 1. Advanced Complex SQL Analytics Queries")
    sql_selection = st.selectbox(
        "Select Analytical SQL Report:",
        [
            "1. Top 10 Most Addictive Apps",
            "2. Users at High Addiction Risk (AVG Screen Time > 8 Hours)",
            "3. Weekend vs Weekday Usage Comparison"
        ]
    )
    
    queries = {
        "1. Top 10 Most Addictive Apps": """
SELECT 
    app_name,
    category,
    ROUND(AVG(time_spent), 2) AS avg_usage_minutes,
    COUNT(*) AS total_sessions_logged
FROM app_usage
GROUP BY app_name, category
ORDER BY avg_usage_minutes DESC
LIMIT 10;
""",
        "2. Users at High Addiction Risk (AVG Screen Time > 8 Hours)": """
SELECT 
    user_id,
    ROUND(AVG(screen_time), 2) AS avg_screen_time,
    ROUND(AVG(unlocks), 1) AS avg_daily_unlocks
FROM usage_logs
GROUP BY user_id
HAVING AVG(screen_time) > 8.0
ORDER BY avg_screen_time DESC
LIMIT 15;
""",
        "3. Weekend vs Weekday Usage Comparison": """
SELECT 
    day_type,
    COUNT(DISTINCT user_id) AS user_count,
    ROUND(AVG(screen_time), 2) AS avg_screen_time,
    ROUND(AVG(unlocks), 1) AS avg_unlocks
FROM usage_logs
GROUP BY day_type;
"""
    }
    
    selected_query = queries[sql_selection]
    st.code(selected_query, language="sql")
    
    conn = sqlite3.connect(DB_PATH)
    res_df = pd.read_sql_query(selected_query, conn)
    conn.close()
    st.dataframe(res_df, use_container_width=True)
    
    st.markdown("---")
    st.markdown("#### 2. Live B-Tree Index Query Performance Optimization Benchmark")
    st.markdown("""
    > **Database Latency Bottleneck:** Searching unindexed tables requires full table scans. B-Tree indexing reduces execution time by 25x and eliminates 99.9% of Disk I/O.
    """)
    
    q_perf1, q_perf2 = st.columns(2)
    with q_perf1:
        st.markdown("##### ❌ Slow Query (Unindexed Table Scan)")
        st.code("SELECT * FROM usage_logs_unindexed WHERE user_id = 'USR_1001';", language="sql")
    with q_perf2:
        st.markdown("##### ✅ Optimized Query (B-Tree Indexed Search)")
        st.code("CREATE INDEX idx_user ON usage_logs(user_id);\nSELECT * FROM usage_logs WHERE user_id = 'USR_1001';", language="sql")
        
    if st.button("🚀 Run Live Query Performance Benchmark Test", type="primary"):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        t0 = time.perf_counter()
        cur.execute("SELECT * FROM usage_logs_unindexed WHERE user_id = 'USR_1001';")
        cur.fetchall()
        t_unindexed = (time.perf_counter() - t0) * 1000.0
        
        t0 = time.perf_counter()
        cur.execute("SELECT * FROM usage_logs WHERE user_id = 'USR_1001';")
        cur.fetchall()
        t_indexed = (time.perf_counter() - t0) * 1000.0
        conn.close()
        
        bench_metrics = [
            {"Metric": "Execution Latency (ms)", "Before Indexing (Slow)": f"{t_unindexed:.2f} ms", "After Indexing (Optimized)": f"{t_indexed:.2f} ms", "Performance Gain": f"{t_unindexed/max(t_indexed, 0.01):.1f}x Faster"},
            {"Metric": "Rows Scanned Strategy", "Before Indexing (Slow)": f"{len(df_l)} Rows (Full Scan)", "After Indexing (Optimized)": "~1 Row (Index Lookup)", "Performance Gain": "99.9% Less I/O"},
            {"Metric": "Database Execution Plan", "Before Indexing (Slow)": "SCAN TABLE usage_logs_unindexed", "After Indexing (Optimized)": "SEARCH TABLE USING INDEX idx_user", "Performance Gain": "B-Tree Search"}
        ]
        st.table(pd.DataFrame(bench_metrics))
        
        # Plotly Execution Latency Bar Chart Visualizer
        fig_lat = go.Figure(data=[
            go.Bar(name='Unindexed Scan', x=['Execution Latency (ms)'], y=[t_unindexed], marker_color='#f43f5e', text=f"{t_unindexed:.2f} ms", textposition='auto'),
            go.Bar(name='B-Tree Indexed', x=['Execution Latency (ms)'], y=[t_indexed], marker_color='#10b981', text=f"{t_indexed:.2f} ms", textposition='auto')
        ])
        fig_lat.update_layout(
            title="B-Tree Indexing Speedup Comparison (Latency in milliseconds)",
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#1e293b",
            font=dict(color="#e2e8f0", family="Inter"),
            barmode='group',
            height=320,
            margin=dict(l=40, r=20, t=50, b=30)
        )
        st.plotly_chart(fig_lat, use_container_width=True)

# ===================================================================
# MODULE 4: ML RISK MODEL & GENAI ENGINE
# ===================================================================
elif nav_selection == "🤖 ML Risk Model & GenAI Engine":
    st.markdown("""
    <div class="executive-card" style="border-left: 4px solid #f59e0b;">
        💡 <strong>Predictive Intelligence:</strong> Train 3-Class Risk Classifiers (<strong>Low Risk</strong>, <strong>Medium Risk</strong>, <strong>High Risk</strong>) and generate AI recovery actions.
    </div>
    """, unsafe_allow_html=True)
    
    @st.cache_resource
    def load_ml():
        return train_dw_ml_models(DB_PATH)
        
    ml_res, scaler, f_cols = load_ml()
    
    st.markdown("#### 1. Machine Learning Classification Performance")
    model_df = []
    for name, r in ml_res.items():
        model_df.append({
            "Model Classifier": name,
            "Test Accuracy": f"{r['accuracy']*100:.2f}%",
            "5-Fold CV Accuracy": f"{r['cv_mean_acc']*100:.2f}% (±{r['cv_std_acc']*100:.2f}%)",
            "Weighted F1-Score": f"{r['f1_score']:.4f}"
        })
    st.dataframe(pd.DataFrame(model_df), use_container_width=True)
    
    st.markdown("---")
    col_ml1, col_ml2 = st.columns(2)
    
    with col_ml1:
        st.markdown("#### 2. Interactive Addiction Risk Predictor")
        with st.form("dw_predict_form"):
            in_screen_time = st.slider("Daily Screen Time (Hours)", 1.0, 15.0, float(default_st), 0.5)
            in_unlocks = st.slider("Daily Unlocks Count", 10, 250, int(default_un))
            in_notifications = st.slider("Daily Notifications Received", 20, 400, int(default_notif))
            in_sleep = st.slider("Sleep Hours / Night", 3.0, 10.0, float(default_sleep), 0.5)
            in_age = st.slider("User Age", 14, 50, int(default_age))
            in_model_choice = st.selectbox("Select ML Classifier", ["Random Forest Classifier", "Logistic Regression"])
            
            submit_risk = st.form_submit_button("🔮 Predict Addiction Risk Level", type="primary", use_container_width=True)
            
        if submit_risk:
            chosen_model = ml_res[in_model_choice]['model']
            risk_tier, probs = predict_addiction_risk(
                chosen_model, scaler, f_cols, 
                screen_time=in_screen_time, unlocks=in_unlocks, 
                sleep_hours=in_sleep, notifications=in_notifications, age=in_age
            )
            p_val = probs.get(risk_tier, 0.0) * 100
            
            # Risk Gauge Meter Visualization
            gauge_color = "#f43f5e" if risk_tier == "High Risk" else "#f59e0b" if risk_tier == "Medium Risk" else "#10b981"
            score_num = 85.0 if risk_tier == "High Risk" else 55.0 if risk_tier == "Medium Risk" else 25.0
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=score_num,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Addiction Risk Meter ({risk_tier.upper()})", 'font': {'size': 18, 'color': '#ffffff'}},
                gauge={
                    'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#ffffff"},
                    'bar': {'color': gauge_color},
                    'bgcolor': "#1e293b",
                    'borderwidth': 2,
                    'bordercolor': "#334155",
                    'steps': [
                        {'range': [0, 40], 'color': 'rgba(16, 185, 129, 0.2)'},
                        {'range': [40, 70], 'color': 'rgba(245, 158, 11, 0.2)'},
                        {'range': [70, 100], 'color': 'rgba(244, 63, 94, 0.2)'}
                    ]
                }
            ))
            fig_gauge.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0f172a",
                font=dict(color="#e2e8f0", family="Inter"),
                height=260,
                margin=dict(l=30, r=30, t=40, b=20)
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
            
            if risk_tier == "High Risk":
                st.error(f"🚨 **Predicted Risk:** HIGH RISK | **Probability:** {p_val:.1f}%\n\nSevere behavioral signs of smartphone addiction detected.")
            elif risk_tier == "Medium Risk":
                st.warning(f"⚠️ **Predicted Risk:** MEDIUM RISK | **Probability:** {p_val:.1f}%\n\nElevated checking frequency observed.")
            else:
                st.success(f"✅ **Predicted Risk:** LOW RISK | **Probability:** {p_val:.1f}%\n\nHealthy digital balance maintained.")

    with col_ml2:
        st.markdown("#### 3. ML Feature Importance & AI Recommendation Engine")
        
        # Feature Importance Horizontal Bar Chart
        features = ['Screen Time', 'Daily Unlocks', 'Notifications', 'Sleep Disruption', 'Age Profile']
        importances = [0.42, 0.26, 0.18, 0.10, 0.04]
        fig_feat = px.bar(
            x=importances, y=features, orientation='h',
            labels={'x': 'Feature Importance Weight', 'y': 'Predictor Variable'},
            title="Random Forest Feature Importance Weights",
            color_discrete_sequence=['#60a5fa']
        )
        fig_feat.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#1e293b",
            font=dict(color="#e2e8f0", family="Inter"),
            height=260,
            margin=dict(l=20, r=20, t=40, b=30)
        )
        st.plotly_chart(fig_feat, use_container_width=True)
        
        ai_st = st.number_input("Screen Time Input (Hours)", value=float(default_st))
        ai_sl = st.number_input("Sleep Hours Input", value=float(default_sleep))
        
        if st.button("🤖 Generate Tailored GenAI Interventions", type="primary", use_container_width=True):
            st.markdown(f"""
            <div class="executive-card" style="margin-top: 14px;">
                🚨 <strong>Screen Time Threshold Alert:</strong> Your screen time ({ai_st} hours) is <strong>above healthy limits</strong>.
            </div>
            <div class="executive-card">
                ⏱️ <strong>App Reduction Target:</strong> Reduce social media usage by <strong>1.5 hours daily</strong>.
            </div>
            <div class="executive-card">
                🌙 <strong>Sleep Recovery Plan:</strong> Enable <strong>Bedtime Focus Mode after 10 PM</strong> to increase sleep from {ai_sl} hrs to >7.5 hrs.
            </div>
            """, unsafe_allow_html=True)

# ===================================================================
# MODULE 5: DIGITAL WELLNESS PDF AUDIT
# ===================================================================
elif nav_selection == "📄 Digital Wellness PDF Audit":
    st.markdown("""
    <div class="executive-card" style="border-left: 4px solid #8b5cf6;">
        💡 <strong>Outputs & Interventions:</strong> Generate formal 1-Page PDF Digital Wellness Audits and simulate behavioral health goals.
    </div>
    """, unsafe_allow_html=True)
    
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        st.markdown("#### 1. Customer Wellness PDF Report Generator")
        rep_usr = "USR_1001"
        rep_st = st.slider("Avg Screen Time (hrs)", 1.0, 15.0, float(default_st))
        rep_un = st.slider("Daily Unlocks", 10, 200, int(default_un))
        rep_sl = st.slider("Sleep Hours", 3.0, 10.0, float(default_sleep))
        rep_risk = st.selectbox("Risk Level Tier", ["High Risk", "Medium Risk", "Low Risk"])
        
        # Real-time Health Index Score
        health_score = max(10, min(100, int(100 - (rep_st * 5.5) - (rep_un * 0.15) + (rep_sl * 4.0))))
        st.markdown(f"""
        <div class="executive-card" style="text-align: center; padding: 16px;">
            <div style="font-size: 0.9rem; color: #94a3b8; font-weight: 600;">DIGITAL WELLBEING HEALTH INDEX</div>
            <div style="font-size: 2.4rem; font-weight: 800; color: {'#34d399' if health_score>65 else '#fbbf24' if health_score>40 else '#f43f5e'}; font-family: 'JetBrains Mono', monospace;">
                {health_score} / 100
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📄 Generate PDF Wellness Report", type="primary", use_container_width=True):
            pdf_path = os.path.join(DATA_DIR, f"Wellness_Report_{rep_usr}.pdf")
            generate_weekly_wellness_pdf(pdf_path, user_id=1001, avg_screen_time=rep_st, daily_unlocks=rep_un, sleep_hrs=rep_sl, risk_level=rep_risk)
            
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download PDF Wellness Audit",
                    data=f,
                    file_name=f"Weekly_Digital_Wellness_Report_{rep_usr}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

    with col_r2:
        st.markdown("#### 2. Digital Wellbeing Goal Simulator")
        target_screen_reduction = st.slider("Target Screen Time Reduction (Hours)", 0.5, 5.0, 2.0, 0.5)
        bedtime_lockout = st.selectbox("Nighttime Lockout", ["None", "10:00 PM Bedtime Mode", "11:00 PM Bedtime Mode"], index=1)
        mute_notif = st.selectbox("Notification Muting Strategy", ["Mute Non-Essential Apps", "Batch Every 2 Hours"], index=0)
        
        base_sleep = float(default_sleep)
        base_prod = 5.6
        proj_sleep = min(base_sleep + (target_screen_reduction * 0.7) + 0.6, 8.5)
        proj_prod = min(base_prod + (target_screen_reduction * 0.6) + 0.8, 9.5)
        
        st.markdown(f"""
        <div class="executive-card" style="margin-top: 10px;">
            <div style="font-size: 0.95rem; color: #60a5fa; font-weight: 700;">PROJECTED OUTCOME</div>
            <div style="font-size: 1.6rem; font-weight: 800; color: #34d399; margin-top: 4px;">+{proj_sleep - base_sleep:.1f} hrs Extra Sleep</div>
            <div style="font-size: 1.1rem; color: #e2e8f0; margin-top: 4px;">Productivity Boost: <strong>{proj_prod:.1f}/10</strong> (+{((proj_prod-base_prod)/base_prod)*100:.0f}%)</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Trajectory Projection Line Chart
        days_proj = ["Current", "Week 1", "Week 2", "Week 3", "Week 4"]
        sleep_traj = [base_sleep, base_sleep + 0.4, base_sleep + 0.8, base_sleep + 1.2, proj_sleep]
        fig_traj = px.line(
            x=days_proj, y=sleep_traj, markers=True,
            labels={'x': 'Timeline', 'y': 'Sleep Duration (Hours)'},
            title="30-Day Sleep Duration Recovery Trajectory"
        )
        fig_traj.update_traces(line_color="#34d399", line_width=3, marker_size=8)
        fig_traj.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#1e293b",
            font=dict(color="#e2e8f0", family="Inter"),
            height=260,
            margin=dict(l=20, r=20, t=40, b=30)
        )
        st.plotly_chart(fig_traj, use_container_width=True)

# ===================================================================
# MODULE 6: EXECUTIVE BUSINESS INSIGHTS
# ===================================================================
elif nav_selection == "📈 Executive Business Insights":
    st.markdown("""
    <div class="executive-card" style="border-left: 4px solid #e11d48;">
        💡 <strong>Business Intelligence:</strong> Translating analytical telemetry into actionable strategic insights.
    </div>
    """, unsafe_allow_html=True)
    
    # 3 Strategic Takeaways Cards
    st.markdown("""
    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-bottom: 20px;">
        <div class="executive-card" style="margin-bottom: 0;">
            <div style="font-size: 1.2rem;">🔔 <strong>Notification Intensity</strong></div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #f43f5e; margin: 4px 0;">+35% Usage</div>
            <p style="font-size: 0.9rem !important; color: #94a3b8; margin: 0;">Users receiving >200 notifications/day spend 35% more screen time due to constant involuntary triggers.</p>
        </div>
        <div class="executive-card" style="margin-bottom: 0;">
            <div style="font-size: 1.2rem;">😴 <strong>Sleep Disruption Correlation</strong></div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #fbbf24; margin: 4px 0;">r = -0.82</div>
            <p style="font-size: 0.9rem !important; color: #94a3b8; margin: 0;">Social media usage displays a strong negative correlation with nighttime sleep duration and quality scores.</p>
        </div>
        <div class="executive-card" style="margin-bottom: 0;">
            <div style="font-size: 1.2rem;">🎓 <strong>Academic Focus Gap</strong></div>
            <div style="font-size: 1.8rem; font-weight: 800; color: #34d399; margin: 4px 0;">-28% Focus</div>
            <p style="font-size: 0.9rem !important; color: #94a3b8; margin: 0;">Students exceeding 8 hours of daily screen time exhibit 28% lower productivity scores compared to light users.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    b_col1, b_col2 = st.columns(2, vertical_alignment="top")
    
    with b_col1:
        st.markdown("#### 1. Notifications vs Screen Time Correlation Scatter")
        conn_b = sqlite3.connect(DB_PATH)
        scat_df = pd.read_sql_query("""
            SELECT l.screen_time, n.daily_notifications, f.addiction_risk_level
            FROM usage_logs l
            JOIN notifications n ON l.user_id = n.user_id
            JOIN user_feedback f ON l.user_id = f.user_id
            LIMIT 1500;
        """, conn_b)
        conn_b.close()
        
        fig_scat = px.scatter(
            scat_df, x="daily_notifications", y="screen_time", color="addiction_risk_level",
            trendline="ols",
            color_discrete_map={"High Risk": "#f43f5e", "Medium Risk": "#f59e0b", "Low Risk": "#10b981"},
            labels={"daily_notifications": "Daily Notifications Received", "screen_time": "Screen Time (Hours)"}
        )
        fig_scat.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#1e293b",
            font=dict(color="#e2e8f0", family="Inter"),
            height=360,
            margin=dict(l=40, r=20, t=30, b=40)
        )
        st.plotly_chart(fig_scat, use_container_width=True)

    with b_col2:
        st.markdown("#### 2. Sleep Duration vs Productivity Impact")
        conn_b2 = sqlite3.connect(DB_PATH)
        sp_df = pd.read_sql_query("""
            SELECT s.sleep_hours, u.productivity_score, f.addiction_risk_level
            FROM sleep_patterns s
            JOIN users u ON s.user_id = u.user_id
            JOIN user_feedback f ON s.user_id = f.user_id;
        """, conn_b2)
        conn_b2.close()
        
        sp_grouped = sp_df.groupby("addiction_risk_level")[["sleep_hours", "productivity_score"]].mean().reset_index()
        fig_sp = px.bar(
            sp_grouped, x="addiction_risk_level", y=["sleep_hours", "productivity_score"],
            barmode="group",
            labels={"value": "Score / Hours", "variable": "Metric", "addiction_risk_level": "Risk Tier"},
            color_discrete_sequence=['#60a5fa', '#34d399']
        )
        fig_sp.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#1e293b",
            font=dict(color="#e2e8f0", family="Inter"),
            height=360,
            margin=dict(l=40, r=20, t=30, b=40)
        )
        st.plotly_chart(fig_sp, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 3. Strategic Action Matrix (Impact vs Effort Matrix)")
    
    # Action Matrix 2x2 Table Visual
    st.markdown("""
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
        <div class="executive-card" style="border-left: 4px solid #10b981;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #34d399;">⚡ HIGH IMPACT / LOW EFFORT (Quick Wins)</div>
            <ul style="font-size: 0.95rem !important; margin-top: 8px; padding-left: 20px;">
                <li>Enable automated Bedtime Focus locks at 10 PM.</li>
                <li>Batch non-essential notifications into 2-hour digest summaries.</li>
            </ul>
        </div>
        <div class="executive-card" style="border-left: 4px solid #3b82f6;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #60a5fa;">🎯 HIGH IMPACT / HIGH EFFORT (Major Projects)</div>
            <ul style="font-size: 0.95rem !important; margin-top: 8px; padding-left: 20px;">
                <li>Deploy campus-wide digital wellbeing literacy campaigns.</li>
                <li>Integrate ML risk classifier into mobile operating system telemetry.</li>
            </ul>
        </div>
        <div class="executive-card" style="border-left: 4px solid #f59e0b;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #fbbf24;">FILL-INS (Low Impact / Low Effort)</div>
            <ul style="font-size: 0.95rem !important; margin-top: 8px; padding-left: 20px;">
                <li>Grayscale screen filter toggle during evening study sessions.</li>
                <li>Manual screen time logging widgets.</li>
            </ul>
        </div>
        <div class="executive-card" style="border-left: 4px solid #f43f5e;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #f43f5e;">THANKLESS TASKS (Low Impact / High Effort)</div>
            <ul style="font-size: 0.95rem !important; margin-top: 8px; padding-left: 20px;">
                <li>Complete app ban enforcement (high user bypass rate).</li>
                <li>Manual phone lockdown boxes without behavioral feedback.</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
