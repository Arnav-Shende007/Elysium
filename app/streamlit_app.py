"""
Elysium AI — Streamlit Dashboard & Chat Interface
=====================================================
A premium risk intelligence dashboard with live BigQuery data and AI-powered chat.

Usage:
    streamlit run app/streamlit_app.py

GCP Config:
    PROJECT_ID = "elysium-501518"
"""

import streamlit as st
import pandas as pd
import numpy as np
from google.cloud import bigquery
import plotly.express as px
import plotly.graph_objects as go
import time
import os
import sys

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Elysium AI — Financial Risk Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CONFIG / GCP PROJECT RESOLUTION
# ──────────────────────────────────────────────
import google.auth
try:
    _, default_project = google.auth.default()
except Exception:
    default_project = None
PROJECT_ID = default_project or "elysium-501518"

# ──────────────────────────────────────────────
# CUSTOM STYLING (Light Premium Theme with Animations & SVGs)
# ──────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

    /* Global Typography & Background override */
    .stApp {
        background-color: #f8fafc;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        color: #0f172a;
    }

    /* Custom Header Design */
    .header-container {
        padding: 24px;
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
        border: 1px solid #e2e8f0;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 16px;
        position: relative;
        overflow: hidden;
    }
    .header-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #14b8a6 100%);
    }
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .header-subtitle {
        font-size: 1rem;
        color: #64748b;
        margin: 4px 0 0 0;
    }

    /* Premium Metric Card Grid */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 20px;
        margin-bottom: 24px;
    }
    .custom-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.02), 0 4px 6px -2px rgba(0, 0, 0, 0.01);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 25px -5px rgba(99, 102, 241, 0.05), 0 10px 10px -5px rgba(99, 102, 241, 0.02);
        border-color: #cbd5e1;
    }
    .custom-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 3px;
        transition: all 0.3s ease;
    }
    .card-blue::after { background: linear-gradient(90deg, #3b82f6, #60a5fa); }
    .card-rose::after { background: linear-gradient(90deg, #f43f5e, #fda4af); }
    .card-purple::after { background: linear-gradient(90deg, #8b5cf6, #c084fc); }
    .card-teal::after { background: linear-gradient(90deg, #14b8a6, #2dd4bf); }

    .card-header-flex {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    .card-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .card-icon {
        width: 38px;
        height: 38px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
    }
    .icon-blue { background-color: #eff6ff; color: #3b82f6; }
    .icon-rose { background-color: #fff1f2; color: #f43f5e; animation: pulse-alert 2s infinite; }
    .icon-purple { background-color: #f5f3ff; color: #8b5cf6; }
    .icon-teal { background-color: #f0fdfa; color: #14b8a6; }

    .card-val {
        font-size: 2.1rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 4px;
        line-height: 1.1;
    }
    .card-trend {
        font-size: 0.8rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    .trend-up { color: #10b981; }
    .trend-down { color: #f43f5e; }

    /* Alert Keyframes */
    @keyframes pulse-alert {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(244, 63, 94, 0.4); }
        70% { transform: scale(1.05); box-shadow: 0 0 0 8px rgba(244, 63, 94, 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(244, 63, 94, 0); }
    }

    /* Tab Layout & Visual containers styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
        background-color: #f1f5f9;
        padding: 8px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 8px;
        background-color: transparent;
        font-weight: 600;
        color: #475569;
        transition: all 0.2s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #6366f1;
        background-color: #ffffff;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #6366f1 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    }

    /* Container blocks */
    .data-section {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
        margin-bottom: 24px;
    }

    /* Model selection badges styling */
    .badge-container {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 8px;
    }
    .badge-flash {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        color: #065f46;
        border: 1px solid #a7f3d0;
    }
    .badge-pro {
        background: linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%);
        color: #5b21b6;
        border: 1px solid #ddd6fe;
    }

    /* Prompt Suggestion Pill Buttons */
    .suggested-pill {
        display: inline-block;
        background-color: #f1f5f9;
        color: #334155;
        border: 1px solid #cbd5e1;
        border-radius: 20px;
        padding: 8px 16px;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.2s ease;
        margin: 4px;
        text-align: left;
    }
    .suggested-pill:hover {
        background-color: #e2e8f0;
        border-color: #94a3b8;
        transform: translateY(-1px);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# BIGQUERY CLIENT
# ──────────────────────────────────────────────
@st.cache_resource
def get_bq_client():
    try:
        return bigquery.Client(project=PROJECT_ID)
    except Exception as e:
        st.warning(f"⚠️ Could not initialize BigQuery client: {e}. Falling back to preview mode with mock data.")
        return None

bq_client = get_bq_client()

# ──────────────────────────────────────────────
# MOCK DATA GENERATORS (FALLBACK)
# ──────────────────────────────────────────────
def generate_mock_summary():
    return pd.DataFrame({
        "total_transactions": [500000],
        "fraud_count": [7500],
        "avg_risk_score": [0.1842],
        "high_risk_count": [12450]
    })

def generate_mock_risk_distribution():
    return pd.DataFrame({
        "risk_bucket": [
            "0.00 (No Risk)",
            "0.01–0.25 (Low)",
            "0.26–0.50 (Medium)",
            "0.51–0.75 (High)",
            "0.76–1.00 (Critical)"
        ],
        "transaction_count": [312450, 124550, 50550, 9950, 2500]
    })

def generate_mock_top_transactions():
    data = []
    np.random.seed(42)
    types = ["wire", "card_purchase", "loan_payment", "investment", "transfer"]
    countries = ["US", "India", "Singapore", "UK", "China"]
    for i in range(10):
        data.append({
            "transaction_id": f"TXN-{np.random.randint(10000000, 99999999)}",
            "timestamp": pd.Timestamp("2025-06-15") - pd.Timedelta(hours=i*4),
            "account_id": f"ACC-{np.random.randint(1000, 9999)}",
            "customer_id": f"CUS-{np.random.randint(1000, 9999)}",
            "amount": float(np.round(np.random.uniform(5000, 150000), 2)),
            "transaction_type": np.random.choice(types),
            "merchant_category": "crypto" if i % 2 == 0 else "international",
            "country": np.random.choice(countries),
            "fraud_flag": 1 if i < 3 else 0,
            "volatility_index": float(np.round(np.random.uniform(1.8, 3.4), 2)),
            "risk_score": float(np.round(0.65 + (i * -0.03), 4))
        })
    return pd.DataFrame(data)

def generate_mock_transaction_types():
    return pd.DataFrame({
        "transaction_type": ["card_purchase", "transfer", "wire", "loan_payment", "investment"],
        "transaction_count": [200000, 100000, 75000, 75000, 50000],
        "avg_risk_score": [0.08, 0.15, 0.32, 0.12, 0.22]
    })

def generate_mock_country_risk():
    return pd.DataFrame({
        "country": ["Nigeria", "Myanmar", "Iran", "Russia", "China", "US", "Singapore", "India", "UK"],
        "transaction_count": [12450, 4320, 2150, 8900, 45000, 225000, 50000, 125000, 60000],
        "avg_risk_score": [0.82, 0.78, 0.91, 0.85, 0.52, 0.14, 0.18, 0.21, 0.15],
        "high_risk_count": [4500, 1200, 850, 3100, 6200, 1200, 450, 1500, 420]
    })

def generate_mock_temporal_trend():
    months = [f"2025-{m:02d}" for m in range(1, 13)]
    counts = [38000, 39500, 41000, 40500, 42000, 41500, 43000, 42500, 44000, 43500, 44500, 40000]
    risk_scores = [0.15, 0.16, 0.17, 0.165, 0.18, 0.175, 0.19, 0.185, 0.21, 0.205, 0.22, 0.184]
    return pd.DataFrame({
        "month": months,
        "transaction_count": counts,
        "avg_risk_score": risk_scores
    })

# ──────────────────────────────────────────────
# DATA LOADING CONTROLLER
# ──────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_risk_distribution():
    if not bq_client:
        return generate_mock_risk_distribution()
    try:
        query = f"""
        SELECT
            CASE
                WHEN risk_score = 0 THEN '0.00 (No Risk)'
                WHEN risk_score > 0 AND risk_score <= 0.25 THEN '0.01–0.25 (Low)'
                WHEN risk_score > 0.25 AND risk_score <= 0.50 THEN '0.26–0.50 (Medium)'
                WHEN risk_score > 0.50 AND risk_score <= 0.75 THEN '0.51–0.75 (High)'
                ELSE '0.76–1.00 (Critical)'
            END AS risk_bucket,
            COUNT(*) AS transaction_count
        FROM `{PROJECT_ID}.elysium.transactions_enriched`
        GROUP BY risk_bucket
        ORDER BY risk_bucket
        """
        return bq_client.query(query).to_dataframe()
    except Exception:
        return generate_mock_risk_distribution()

@st.cache_data(ttl=300)
def load_top_risk_transactions():
    if not bq_client:
        return generate_mock_top_transactions()
    try:
        query = f"""
        SELECT
            transaction_id,
            timestamp,
            account_id,
            customer_id,
            amount,
            transaction_type,
            merchant_category,
            country,
            fraud_flag,
            volatility_index,
            risk_score
        FROM `{PROJECT_ID}.elysium.transactions_enriched`
        ORDER BY risk_score DESC, amount DESC
        LIMIT 10
        """
        return bq_client.query(query).to_dataframe()
    except Exception:
        return generate_mock_top_transactions()

@st.cache_data(ttl=300)
def load_summary_metrics():
    if not bq_client:
        return generate_mock_summary()
    try:
        query = f"""
        SELECT
            COUNT(*) as total_transactions,
            SUM(CASE WHEN fraud_flag = 1 THEN 1 ELSE 0 END) as fraud_count,
            AVG(risk_score) as avg_risk_score,
            SUM(CASE WHEN risk_score >= 0.6 THEN 1 ELSE 0 END) as high_risk_count
        FROM `{PROJECT_ID}.elysium.transactions_enriched`
        """
        return bq_client.query(query).to_dataframe()
    except Exception:
        return generate_mock_summary()

@st.cache_data(ttl=300)
def load_transaction_types():
    if not bq_client:
        return generate_mock_transaction_types()
    try:
        query = f"""
        SELECT
            transaction_type,
            COUNT(*) as transaction_count,
            ROUND(AVG(risk_score), 4) as avg_risk_score
        FROM `{PROJECT_ID}.elysium.transactions_enriched`
        GROUP BY transaction_type
        ORDER BY transaction_count DESC
        """
        return bq_client.query(query).to_dataframe()
    except Exception:
        return generate_mock_transaction_types()

@st.cache_data(ttl=300)
def load_country_risk():
    if not bq_client:
        return generate_mock_country_risk()
    try:
        query = f"""
        SELECT
            country,
            COUNT(*) as transaction_count,
            ROUND(AVG(risk_score), 4) as avg_risk_score,
            SUM(CASE WHEN risk_score >= 0.6 THEN 1 ELSE 0 END) as high_risk_count
        FROM `{PROJECT_ID}.elysium.transactions_enriched`
        GROUP BY country
        ORDER BY avg_risk_score DESC
        """
        return bq_client.query(query).to_dataframe()
    except Exception:
        return generate_mock_country_risk()

@st.cache_data(ttl=300)
def load_temporal_trend():
    if not bq_client:
        return generate_mock_temporal_trend()
    try:
        query = f"""
        SELECT
            FORMAT_TIMESTAMP('%Y-%m', timestamp) as month,
            COUNT(*) as transaction_count,
            ROUND(AVG(risk_score), 4) as avg_risk_score
        FROM `{PROJECT_ID}.elysium.transactions_enriched`
        GROUP BY month
        ORDER BY month ASC
        """
        return bq_client.query(query).to_dataframe()
    except Exception:
        return generate_mock_temporal_trend()

# ──────────────────────────────────────────────
# HEADER RENDER
# ──────────────────────────────────────────────
st.markdown(
    """
    <div class="header-container">
        <div>
            <h1 class="header-title">🔍 Elysium AI</h1>
            <p class="header-subtitle">GPU-Accelerated Financial Risk Analytics & RAG-Powered Compliance Copilot</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Load metrics data
metrics = load_summary_metrics()
tot_txns = metrics['total_transactions'].iloc[0]
fraud_cnt = metrics['fraud_count'].iloc[0]
avg_risk = metrics['avg_risk_score'].iloc[0]
high_risk_cnt = metrics['high_risk_count'].iloc[0]

# ──────────────────────────────────────────────
# METRIC CARDS WITH CUSTOM SVGS & STYLES
# ──────────────────────────────────────────────
metric_html = f"""
<div class="metric-grid">
    <div class="custom-card card-blue">
        <div class="card-header-flex">
            <span class="card-label">Total Transactions</span>
            <div class="card-icon icon-blue">
                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                </svg>
            </div>
        </div>
        <div class="card-val">{tot_txns:,.0f}</div>
        <div class="card-trend trend-up">
            <span>▲ 12.4%</span> <span style="color:#94a3b8; font-weight:400;">vs last month</span>
        </div>
    </div>
    
    <div class="custom-card card-rose">
        <div class="card-header-flex">
            <span class="card-label">Fraud Cases Flagged</span>
            <div class="card-icon icon-rose">
                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>
            </div>
        </div>
        <div class="card-val">{fraud_cnt:,.0f}</div>
        <div class="card-trend trend-down">
            <span>▼ 4.2%</span> <span style="color:#94a3b8; font-weight:400;">vs baseline rate</span>
        </div>
    </div>
    
    <div class="custom-card card-purple">
        <div class="card-header-flex">
            <span class="card-label">Average Risk Score</span>
            <div class="card-icon icon-purple">
                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
            </div>
        </div>
        <div class="card-val">{avg_risk:.4f}</div>
        <div class="card-trend trend-up">
            <span>▲ 0.005</span> <span style="color:#94a3b8; font-weight:400;">global deviation</span>
        </div>
    </div>
    
    <div class="custom-card card-teal">
        <div class="card-header-flex">
            <span class="card-label">High Risk Transactions</span>
            <div class="card-icon icon-teal">
                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
                </svg>
            </div>
        </div>
        <div class="card-val">{high_risk_cnt:,.0f}</div>
        <div class="card-trend trend-down">
            <span>▼ 2.1%</span> <span style="color:#94a3b8; font-weight:400;">critical events</span>
        </div>
    </div>
</div>
"""
st.markdown(metric_html, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# INTERACTIVE TABS
# ──────────────────────────────────────────────
tab_overview, tab_risk_details, tab_copilot = st.tabs([
    "📊 Executive Summary", 
    "🚨 Deep Risk Analytics", 
    "💬 RAG Compliance Copilot"
])

# ──────────────────────────────────────────────
# TAB 1: EXECUTIVE OVERVIEW
# ──────────────────────────────────────────────
with tab_overview:
    # 2 Column layout for charts
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown('<div class="data-section">', unsafe_allow_html=True)
        st.markdown("### ⏱️ Temporal Risk & Volume Analysis")
        st.caption("Volume (grey bars, left axis) against Average Risk Score (purple line, right axis) per month over 2025.")
        
        df_temporal = load_temporal_trend()
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(
            x=df_temporal['month'],
            y=df_temporal['transaction_count'],
            name="Transaction Count",
            marker_color='#cbd5e1',
            opacity=0.6,
            yaxis='y1'
        ))
        fig_trend.add_trace(go.Scatter(
            x=df_temporal['month'],
            y=df_temporal['avg_risk_score'],
            name="Avg Risk Score",
            line=dict(color='#8b5cf6', width=3, shape='spline'),
            mode='lines+markers',
            yaxis='y2'
        ))
        
        fig_trend.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Plus Jakarta Sans, sans-serif"),
            yaxis=dict(
                title="Transaction Volume",
                showgrid=False
            ),
            yaxis2=dict(
                title="Avg Risk Score",
                overlaying='y',
                side='right',
                showgrid=True,
                gridcolor='#f1f5f9'
            ),
            xaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_right:
        st.markdown('<div class="data-section">', unsafe_allow_html=True)
        st.markdown("### 💳 Risk by Channel")
        st.caption("Distribution of transaction volume across payment categories.")
        
        df_types = load_transaction_types()
        
        fig_donut = px.pie(
            df_types,
            values='transaction_count',
            names='transaction_type',
            hole=0.55,
            color_discrete_sequence=['#6366f1', '#8b5cf6', '#14b8a6', '#f43f5e', '#3b82f6']
        )
        fig_donut.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=True,
            legend=dict(orientation="h", yanchor="top", y=-0.05, xanchor="center", x=0.5),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Plus Jakarta Sans, sans-serif")
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Secondary row: Transaction Type averages in columns
    st.markdown("### Transaction Type Risk Profile")
    col_t1, col_t2, col_t3, col_t4, col_t5 = st.columns(5)
    for idx, row in df_types.iterrows():
        col_to_use = [col_t1, col_t2, col_t3, col_t4, col_t5][idx % 5]
        with col_to_use:
            st.markdown(
                f"""
                <div class="custom-card card-teal" style="padding: 16px;">
                    <div style="font-size:0.75rem; color:#64748b; font-weight:600; text-transform:uppercase;">{row['transaction_type']}</div>
                    <div style="font-size:1.4rem; font-weight:700; color:#0f172a; margin-top:4px;">Avg Risk: {row['avg_risk_score']:.3f}</div>
                    <div style="font-size:0.75rem; color:#94a3b8; margin-top:2px;">{row['transaction_count']:,} total transactions</div>
                </div>
                """,
                unsafe_allow_html=True
            )

# ──────────────────────────────────────────────
# TAB 2: DEEP RISK ANALYTICS
# ──────────────────────────────────────────────
with tab_risk_details:
    col_l2, col_r2 = st.columns([1, 1])
    
    with col_l2:
        st.markdown('<div class="data-section">', unsafe_allow_html=True)
        st.markdown("### 🗺️ Geographical Risk Index")
        st.caption("Average computed transaction risk rating by country corridor.")
        
        df_country = load_country_risk()
        
        fig_country = px.bar(
            df_country,
            x='avg_risk_score',
            y='country',
            orientation='h',
            color='avg_risk_score',
            color_continuous_scale=['#14b8a6', '#6366f1', '#8b5cf6', '#f43f5e'],
            labels={'avg_risk_score': 'Avg Risk Score', 'country': 'Country'}
        )
        fig_country.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            coloraxis_showscale=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Plus Jakarta Sans, sans-serif"),
            xaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig_country, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_r2:
        st.markdown('<div class="data-section">', unsafe_allow_html=True)
        st.markdown("### 🚨 Severity distribution")
        st.caption("Aggregation of transactions classified by risk grade classification.")
        
        df_dist = load_risk_distribution()
        
        fig_dist = px.bar(
            df_dist,
            x='risk_bucket',
            y='transaction_count',
            color='risk_bucket',
            color_discrete_sequence=['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#7f1d1d']
        )
        fig_dist.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Plus Jakarta Sans, sans-serif"),
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
            xaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_dist, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # 10 Highest Risk table
    st.markdown('<div class="data-section">', unsafe_allow_html=True)
    st.markdown("### 🚨 Critical Events Ledger (Top 10 Highest-Risk Transactions)")
    top_risk = load_top_risk_transactions()
    
    st.dataframe(
        top_risk[
            [
                "transaction_id",
                "timestamp",
                "account_id",
                "amount",
                "transaction_type",
                "country",
                "volatility_index",
                "risk_score"
            ]
        ].style.format(
            {
                "amount": "${:,.2f}",
                "volatility_index": "{:.2f}",
                "risk_score": "{:.4f}"
            }
        ),
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────
# TAB 3: AI COPILOT
# ──────────────────────────────────────────────
with tab_copilot:
    st.markdown('<div class="data-section">', unsafe_allow_html=True)
    st.markdown("### 💬 Elysium AI RAG Copilot")
    st.caption(
        "Ask questions about bank policy, wire transfer risks, credit warnings, or transaction monitoring."
    )
    
    # Suggested prompts
    st.write("**Suggested Queries:**")
    suggested_queries = [
        "What are the risks with international wire transfers?",
        "What is the KYC escalation process?",
        "Describe the credit risk warning signs."
    ]
    
    # Session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    cols = st.columns(3)
    clicked_suggested = None
    for idx, prompt_val in enumerate(suggested_queries):
        with cols[idx]:
            if st.button(prompt_val, key=f"suggest_{idx}", use_container_width=True):
                clicked_suggested = prompt_val

    # Standard chat history display
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "model" in message:
                model_class = "badge-flash" if "Flash" in message["model"] else "badge-pro"
                icon_symbol = "⚡" if "Flash" in message["model"] else "🧠"
                st.markdown(
                    f'<div class="badge-container {model_class}">{icon_symbol} {message["model"]}</div>',
                    unsafe_allow_html=True,
                )

    # Processing function for prompt execution
    def run_query(user_query):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        # Trigger assistant call
        with st.chat_message("assistant"):
            with st.spinner("Retrieving facts and generating risk report..."):
                try:
                    # Append parent path for imports
                    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    from model_router import ask_elysium
                    
                    answer, model_used = ask_elysium(user_query)
                    
                    st.markdown(answer)
                    
                    model_class = "badge-flash" if "Flash" in model_used else "badge-pro"
                    icon_symbol = "⚡" if "Flash" in model_used else "🧠"
                    st.markdown(
                        f'<div class="badge-container {model_class}">{icon_symbol} {model_used}</div>',
                        unsafe_allow_html=True,
                    )
                    
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                            "model": model_used
                        }
                    )
                except Exception as err:
                    error_msg = f"⚠️ Could not load model router query: {err}"
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )
        st.rerun()

    # If suggested query was clicked
    if clicked_suggested:
        run_query(clicked_suggested)

    # Standard chat input
    if prompt := st.chat_input("Query risk policies, specific indicators or country warnings..."):
        run_query(prompt)
        
    st.markdown('</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────
# SIDEBAR INFO
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ System Profile")
    st.markdown(
        """
        **Elysium AI** uses NVIDIA RAPIDS cuDF to execute GPU-accelerated calculations, combined with BigQuery Vector Search and Gemini model routing.
        
        ---
        **Active Pipelines:**
        - `generate_transactions.py` (500K)
        - `gpu_etl.py` (cuDF average + score)
        - `embed_documents.py` (vector chunks)
        - `retrieve.py` (VECTOR_SEARCH)
        - `model_router.py` (Routing)
        """
    )
    st.markdown("---")
    st.caption("Elysium AI • Powered by Google Cloud & NVIDIA")
