"""
FinPulse AI — Streamlit Dashboard & Chat Interface
=====================================================
A risk intelligence dashboard with live BigQuery data and AI-powered chat.

Usage:
    export GOOGLE_APPLICATION_CREDENTIALS="path/to/your-key.json"
    streamlit run app/streamlit_app.py

GCP Config:
    PROJECT_ID = "elysium-501518"
"""

import streamlit as st
import pandas as pd
from google.cloud import bigquery

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="FinPulse AI — Risk Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
PROJECT_ID = "elysium-501518"

# ──────────────────────────────────────────────
# STYLING
# ──────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    .main { font-family: 'Inter', sans-serif; }

    .hero-title {
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: #8892a0;
        margin-top: 0;
    }

    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #2a2a4a;
        text-align: center;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #8892a0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .model-badge-flash {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .model-badge-pro {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .stChatMessage { border-radius: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────
# BIGQUERY CLIENT
# ──────────────────────────────────────────────
@st.cache_resource
def get_bq_client():
    return bigquery.Client(project=PROJECT_ID)


bq_client = get_bq_client()


# ──────────────────────────────────────────────
# DATA LOADING FUNCTIONS
# ──────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_risk_distribution():
    """Load risk score distribution for the bar chart."""
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
    FROM `{PROJECT_ID}.finpulse.transactions_enriched`
    GROUP BY risk_bucket
    ORDER BY risk_bucket
    """
    return bq_client.query(query).to_dataframe()


@st.cache_data(ttl=300)
def load_top_risk_transactions():
    """Load top 10 highest-risk transactions."""
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
    FROM `{PROJECT_ID}.finpulse.transactions_enriched`
    ORDER BY risk_score DESC, amount DESC
    LIMIT 10
    """
    return bq_client.query(query).to_dataframe()


@st.cache_data(ttl=300)
def load_summary_metrics():
    """Load summary metrics for the dashboard."""
    query = f"""
    SELECT
        COUNT(*) as total_transactions,
        SUM(CASE WHEN fraud_flag = 1 THEN 1 ELSE 0 END) as fraud_count,
        AVG(risk_score) as avg_risk_score,
        SUM(CASE WHEN risk_score >= 0.6 THEN 1 ELSE 0 END) as high_risk_count
    FROM `{PROJECT_ID}.finpulse.transactions_enriched`
    """
    return bq_client.query(query).to_dataframe()


# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────
st.markdown('<p class="hero-title">🔍 FinPulse AI</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-subtitle">AI-Powered Financial Risk Intelligence • Real-time Transaction Monitoring • RAG-Enhanced Analysis</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# ──────────────────────────────────────────────
# DASHBOARD SECTION
# ──────────────────────────────────────────────
st.subheader("📊 Risk Dashboard")

try:
    # Summary metrics
    metrics = load_summary_metrics()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Transactions",
            value=f"{metrics['total_transactions'].iloc[0]:,.0f}",
        )
    with col2:
        st.metric(
            label="Fraud Cases",
            value=f"{metrics['fraud_count'].iloc[0]:,.0f}",
        )
    with col3:
        st.metric(
            label="Avg Risk Score",
            value=f"{metrics['avg_risk_score'].iloc[0]:.4f}",
        )
    with col4:
        st.metric(
            label="High Risk (≥0.6)",
            value=f"{metrics['high_risk_count'].iloc[0]:,.0f}",
        )

    st.markdown("")

    # Two-column layout: chart + table
    chart_col, table_col = st.columns([1, 1])

    with chart_col:
        st.markdown("#### Risk Score Distribution")
        risk_dist = load_risk_distribution()
        st.bar_chart(
            risk_dist.set_index("risk_bucket")["transaction_count"],
            use_container_width=True,
        )

    with table_col:
        st.markdown("#### 🚨 Top 10 Highest-Risk Transactions")
        top_risk = load_top_risk_transactions()
        st.dataframe(
            top_risk[
                [
                    "transaction_id",
                    "account_id",
                    "amount",
                    "country",
                    "risk_score",
                    "fraud_flag",
                ]
            ].style.format(
                {
                    "amount": "${:,.2f}",
                    "risk_score": "{:.4f}",
                }
            ),
            use_container_width=True,
            height=380,
        )

except Exception as e:
    st.warning(
        f"⚠️ Dashboard data unavailable. Ensure BigQuery table `finpulse.transactions_enriched` exists.\n\nError: {e}"
    )

# ──────────────────────────────────────────────
# CHAT SECTION
# ──────────────────────────────────────────────
st.markdown("---")
st.subheader("💬 Ask FinPulse AI")
st.caption(
    "Ask questions about financial risks, transaction patterns, policies, and market conditions. "
    "Complex queries use RAG-grounded Gemini Pro; simple queries use Gemini Flash."
)

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "model" in message:
            model_class = "flash" if "Flash" in message["model"] else "pro"
            badge_class = f"model-badge-{model_class}"
            st.markdown(
                f'<span class="{badge_class}">⚡ {message["model"]}</span>',
                unsafe_allow_html=True,
            )

# Chat input
if prompt := st.chat_input("Ask a question about financial risks..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get AI response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                # Import here to avoid import errors when BigQuery isn't available
                import sys
                import os

                # Add parent directory to path for imports
                sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                from model_router import ask_finpulse, classify_query

                answer, model_used = ask_finpulse(prompt)

                st.markdown(answer)

                model_class = "flash" if "Flash" in model_used else "pro"
                badge_class = f"model-badge-{model_class}"
                st.markdown(
                    f'<span class="{badge_class}">⚡ {model_used}</span>',
                    unsafe_allow_html=True,
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "model": model_used,
                    }
                )
            except Exception as e:
                error_msg = f"⚠️ Error getting AI response: {e}"
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )

# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ About FinPulse AI")
    st.markdown(
        """
    **FinPulse AI** is a real-time financial risk intelligence
    platform powered by:

    - 🚀 **RAPIDS cuDF** — GPU-accelerated ETL
    - 🔍 **BigQuery Vector Search** — RAG retrieval
    - 🧠 **Gemini Flash/Pro** — Intelligent model routing
    - 📊 **BigQuery** — Scalable data warehouse
    - ☁️ **Cloud Run** — Serverless deployment

    ---

    **Model Routing:**
    - ⚡ **Flash** — Fast queries (risk scores, summaries, calculations)
    - 🧠 **Pro** — Complex analysis (risk memos, policy questions, market analysis)

    ---

    Built for the Google Cloud + NVIDIA Hackathon
    """
    )

    st.markdown("---")
    st.caption("© 2025 FinPulse AI • Powered by Google Cloud & NVIDIA")
