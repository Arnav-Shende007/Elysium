# 🔍 FinPulse AI — Real-Time Financial Risk Intelligence

> **An AI-powered risk intelligence platform** that combines GPU-accelerated data processing, RAG-enhanced knowledge retrieval, and intelligent model routing to deliver real-time financial risk analysis. Built for the Google Cloud × NVIDIA Hackathon.

[![Deploy to Cloud Run](https://img.shields.io/badge/Cloud%20Run-Deployed-blue?logo=google-cloud)](DEPLOYMENT_LINK)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/AryanMedigeri08/Elysium)

---

## 🎯 Problem Statement

Financial institutions process millions of transactions daily, requiring real-time risk assessment that balances speed with analytical depth. Traditional rule-based systems miss complex fraud patterns, while manual review creates bottlenecks. Organizations need an intelligent system that can rapidly score transaction risk, retrieve relevant institutional knowledge, and provide context-aware analysis — all at scale.

## 💡 Solution

FinPulse AI is an end-to-end risk intelligence platform that:
1. **Ingests and enriches** 500K+ transactions with GPU-accelerated ETL using RAPIDS cuDF
2. **Embeds and indexes** institutional knowledge documents for instant RAG retrieval via BigQuery Vector Search
3. **Intelligently routes** queries to Gemini Flash (fast/simple) or Gemini Pro (complex/RAG-grounded) based on query classification
4. **Visualizes** risk distributions and high-risk transactions in a real-time Streamlit dashboard deployed on Cloud Run

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────────┐
│  Cloud Storage   │────▶│   BigQuery   │────▶│  RAPIDS cuDF ETL    │
│  (Raw Data +     │     │  (Data       │     │  (GPU-Accelerated   │
│   RAG Documents) │     │   Warehouse) │     │   Risk Scoring)     │
└─────────────────┘     └──────┬───────┘     └──────────┬──────────┘
                               │                         │
                               ▼                         ▼
                    ┌──────────────────┐     ┌──────────────────────┐
                    │  BigQuery Vector │     │  BigQuery Enriched   │
                    │  Search (RAG)    │     │  Transactions        │
                    └────────┬─────────┘     └──────────┬───────────┘
                             │                          │
                             ▼                          ▼
                    ┌──────────────────────────────────────────────┐
                    │          Gemini Model Router                 │
                    │   ⚡ Flash (fast)  |  🧠 Pro (RAG-grounded) │
                    └────────────────────┬─────────────────────────┘
                                         │
                                         ▼
                    ┌──────────────────────────────────────────────┐
                    │         Streamlit Dashboard (Cloud Run)      │
                    │   📊 Risk Charts | 🚨 Alerts | 💬 AI Chat   │
                    └──────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Technology | Role in FinPulse AI |
|---|---|
| **Google Cloud Storage** | Raw data lake for transactions and RAG knowledge documents |
| **BigQuery** | Scalable data warehouse; hosts raw, enriched, and embedding tables |
| **BigQuery ML** | Generates text embeddings (`text-embedding-004`) for RAG pipeline |
| **BigQuery Vector Search** | Cosine similarity search over embedded knowledge base chunks |
| **Vertex AI Gemini 2.0 Flash** | Fast inference for simple risk queries (scores, summaries) |
| **Vertex AI Gemini 2.0 Pro** | Deep analysis with RAG-grounded context for complex queries |
| **NVIDIA RAPIDS cuDF** | GPU-accelerated pandas for ETL — rolling averages, risk scoring |
| **Vertex AI Workbench** | GPU notebook environment (L4) for data processing pipelines |
| **Cloud Run** | Serverless deployment of Streamlit dashboard |
| **Streamlit** | Interactive frontend with charts, tables, and AI chat interface |

---

## 📁 Project Structure

```
elysium/
├── app/
│   └── streamlit_app.py          # Streamlit dashboard + chat UI
├── rag_documents/                # 12 RAG knowledge base documents
│   ├── high_risk_countries.txt
│   ├── fraud_patterns.txt
│   ├── wire_transfer_risks.txt
│   ├── credit_risk_warnings.txt
│   ├── acme_corp_earnings.txt
│   ├── market_volatility_alert.txt
│   ├── semiconductor_outlook.txt
│   ├── fintech_disruption.txt
│   ├── global_trade_shifts.txt
│   ├── digital_currency_regulation.txt
│   ├── transaction_monitoring_policy.txt
│   └── kyc_aml_escalation_policy.txt
├── generate_transactions.py      # Synthetic data generator (500K rows)
├── gpu_etl.py                    # GPU-accelerated ETL pipeline
├── embed_documents.py            # RAG embedding + vector index
├── retrieve.py                   # Vector search retrieval function
├── model_router.py               # Gemini Flash/Pro intelligent router
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Cloud Run container config
└── README.md                     # This file
```

---

## 🚀 Setup & Run

### Prerequisites
- Google Cloud project with APIs enabled (BigQuery, Cloud Storage, Vertex AI, Cloud Run)
- Service account with roles: BigQuery Admin, Storage Admin, Vertex AI User
- Vertex AI Workbench instance with GPU (L4) for ETL pipeline

### Step 1: Data Generation (Vertex AI Workbench)
```bash
# In a Vertex AI Workbench notebook
python generate_transactions.py
```

### Step 2: GPU ETL (Vertex AI Workbench)
```python
# First cell:
%load_ext cudf.pandas
# Then run:
python gpu_etl.py
```

### Step 3: RAG Pipeline (Vertex AI Workbench)
```bash
# Upload documents to GCS
gsutil cp rag_documents/*.txt gs://elysium-data/rag/

# Generate embeddings and create vector index
python embed_documents.py

# Test retrieval
python retrieve.py
```

### Step 4: Test Locally
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your-key.json"
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

### Step 5: Deploy to Cloud Run
```bash
gcloud run deploy finpulse-ai --source . --region us-central1 --allow-unauthenticated
```

---

## 🔗 Links

| Resource | Link |
|---|---|
| 🌐 **Live Demo** | [DEPLOYMENT_LINK] |
| 🎥 **Demo Video** | [DEMO_VIDEO_LINK] |
| 📊 **Presentation** | [PPT_LINK] |
| 💻 **GitHub** | [https://github.com/AryanMedigeri08/Elysium](https://github.com/AryanMedigeri08/Elysium) |

---

## 👤 Team

**Aryan Medigeri** — Solo participant

---

*Built with ❤️ using Google Cloud and NVIDIA technologies*
