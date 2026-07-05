# FinPulse AI — Build Task List & Prompts

Use this as your working checklist. Each task says which tool to use and gives a ready prompt to paste in.

---

## PHASE 0 — GCP Console / Cloud Shell (no AI tool needed)

- [ ] Create/select GCP project
- [ ] Enable APIs: BigQuery, Cloud Storage, Vertex AI, Cloud Run
- [ ] Create bucket: `gsutil mb -l us-central1 gs://finpulse-data-yourname/`
- [ ] Create BigQuery dataset `finpulse` (via the ⋮ menu next to your project name)
- [ ] Create Vertex AI Workbench notebook instance (GPU: L4)
- [ ] Create service account with roles: BigQuery Admin, Storage Admin, Vertex AI User → download JSON key (keep out of GitHub)

---

## PHASE 1 — Antigravity: Synthetic Transaction Data Generator

**Prompt to paste into Antigravity:**

> Write a Python script called `generate_transactions.py` that generates a synthetic financial transactions dataset for a hackathon project called FinPulse AI. Requirements:
> - Use pandas and numpy, ~500,000 rows
> - Columns: transaction_id, timestamp (minute-level over 2025), account_id, customer_id, amount (lognormal distribution, mix of positive/negative), transaction_type (wire, card_purchase, loan_payment, investment, transfer), merchant_category (retail, international, crypto, supplier, salary), country (US, India, Singapore, UK, China with realistic weighted distribution), fraud_flag (imbalanced, ~1.5% positive), volatility_index (uniform 0.2 to 3.5)
> - Save to parquet locally, then include the `gsutil cp` command to upload to `gs://finpulse-data-yourname/`
> - Add a final step that loads the parquet file into BigQuery table `finpulse.transactions.raw` using `pandas.to_gbq()` or the `google.cloud.bigquery` client, whichever is more reliable in a Vertex AI Workbench notebook
> - Add print statements showing row count and a sample after each step so I can verify it worked
> - Wrap everything so it can run cleanly inside a Jupyter/Colab-style notebook cell in Vertex AI Workbench

**Where to run it:** Inside your Vertex AI Workbench notebook (not locally)

**Verify:** Check BigQuery console → `finpulse.transactions.raw` table exists with ~500,000 rows

---

## PHASE 2 — Antigravity: RAG Knowledge Documents

**Prompt to paste into Antigravity :**

> Generate 12 short finance knowledge documents (200-800 words each, plain text) for a RAG knowledge base for a fictional bank/fintech risk intelligence system called FinPulse AI. Cover this mix:
> - 4 internal risk memos (e.g., high-risk countries and their risk factors, fraud pattern red flags, wire transfer risk indicators, credit risk warning signs)
> - 3 market/economic summaries (e.g., quarterly earnings summary for a fictional company "Acme Corp", market volatility alert, sector outlook for semiconductors)
> - 3 news-style articles (short, realistic headlines + 2-3 paragraph summaries about financial market events — keep these generic/fictional, not real company names or real events)
> - 2 internal policy documents (e.g., transaction monitoring policy, KYC/AML escalation policy)
> Output each as a separate file with a clear filename (e.g., `high_risk_countries.txt`, `fraud_patterns.txt`) and the content ready to save directly as .txt files. Make the content specific and detailed enough to be genuinely useful for a retrieval system (concrete numbers, named risk factors, thresholds) rather than generic filler.

**Where to save:** Local `rag_documents/` folder, then:
```
gsutil cp rag_documents/*.txt gs://finpulse-data-yourname/rag/
```

---

## PHASE 3 — Antigravity: GPU ETL + RAG Embedding Pipeline

### 3a. GPU ETL script

**Prompt for Antigravity:**

> Write a Python script `gpu_etl.py` for a Vertex AI Workbench notebook with GPU. It should:
> - Load `%load_ext cudf.pandas` for GPU acceleration
> - Read the `finpulse.transactions.raw` table from BigQuery into a cudf-accelerated pandas DataFrame
> - Sort by timestamp within account_id, compute a rolling 50-transaction average of `amount` per account_id
> - Compute a `risk_score` column combining: volatility_index > 1.5, amount deviating >3x from rolling average, and fraud_flag, each weighted (0.4/0.35/0.25)
> - Add a timing block using `time.time()` before/after the heavy operations so I can show GPU speedup in my demo
> - Write the enriched result back to BigQuery as `finpulse.transactions.enriched`
> - Include clear print statements confirming row counts and elapsed time

### 3b. RAG embedding + vector index

**Prompt for Antigravity:**

> Write a Python script `embed_documents.py` that:
> - Reads all `.txt` files from `gs://finpulse-data-yourname/rag/`
> - Chunks each document into ~300-word chunks with document filename as metadata
> - Generates embeddings for each chunk using BigQuery's `ML.GENERATE_EMBEDDING` with the `text-embedding-004` model (write this as a BigQuery SQL statement executed via the Python client, not the Gemini SDK directly)
> - Creates a table `finpulse.rag.embeddings` with columns: chunk_id, content, metadata (filename), embedding
> - After the table is populated, generate the SQL to create a vector index on the embedding column using `CREATE VECTOR INDEX` with COSINE distance
> - Include verification: query the table and print row count + confirm the index was created successfully

### 3c. Retrieval function

**Prompt for Antigravity:**

> Write `retrieve.py` with a function `retrieve_context(query: str, top_k=5)` that:
> - Embeds the incoming query using the same `text-embedding-004` model via BigQuery
> - Runs a `VECTOR_SEARCH` query against `finpulse.rag.embeddings` to find the top_k most similar chunks
> - Returns the concatenated chunk contents as a single context string, along with the source filenames used
> - Include a test call at the bottom with a sample query like "What are the risks with international wire transfers?" so I can verify it returns relevant chunks

### 3d. Model router

**Prompt for Antigravity:**

> Write `model_router.py` with:
> - A `classify_query(query: str)` function that returns "flash" for queries containing keywords like risk score, quick, current, summary, how much, calculate — and "pro" otherwise
> - An `ask_finpulse(query: str)` function that: calls `classify_query`, if "pro" calls `retrieve_context` from retrieve.py to get grounded context, builds a prompt instructing the model to act as a senior financial risk analyst, calls Gemini (gemini-2.0-flash for "flash" path, gemini-2.0-pro for "pro" path) via BigQuery's `AI.GENERATE_TEXT` or the Vertex AI Gemini SDK — pick whichever is more stable to call from a Cloud Run deployed app later, not just a notebook
> - Returns both the answer text and which model was used
> - Include 2 test calls at the bottom, one that should route to flash and one to pro, printing both results

**Where to run 3a-3d:** Same Vertex AI Workbench notebook, one after another, verifying each output in BigQuery before moving to the next.

---

## PHASE 4 — Antigravity: Frontend App

**Prompt for Antigravity:**

> Write a Streamlit app `streamlit_app.py` for FinPulse AI that:
> - Has a title and short caption describing the tool
> - Has a chat-style text input where the user asks a question
> - On submit, calls `ask_finpulse()` from `model_router.py`
> - Displays the answer, and a caption showing which model was used (Flash/Pro)
> - Also displays a simple dashboard section above the chat: a bar chart of risk_score distribution and a table of the top 10 highest-risk transactions, both pulled live from `finpulse.transactions.enriched` in BigQuery using the `google-cloud-bigquery` Python client
> - Include a `requirements.txt` with all needed packages (streamlit, google-cloud-bigquery, pandas, etc.)
> - Make sure it reads GCP credentials via environment variable `GOOGLE_APPLICATION_CREDENTIALS` so it works both locally and later in Cloud Run

**Test locally first:**
```
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your-key.json"
streamlit run app/streamlit_app.py
```

---

## PHASE 5 — GitHub
https://github.com/AryanMedigeri08/Elysium
- [ ] Create repo, push all scripts/docs/Dockerfile/requirements.txt
- [ ] Add `.gitignore` (service account JSON, `.env`)
- [ ] Write README last, once deployed URL is known

**Prompt for Antigravity (README):**

> Write a README.md for a GitHub repo called FinPulse AI, a hackathon project. Include: one-paragraph problem statement and solution summary, an architecture section describing the flow (Cloud Storage → BigQuery → RAPIDS/cuDF ETL → BigQuery Vector Search RAG → Gemini Flash/Pro router → Streamlit dashboard on Cloud Run), a tech stack table mapping each Google Cloud and NVIDIA tool used to what it does in this project, setup/run instructions, and placeholders for [Deployment Link], [Demo Video Link], and [PPT Link] that I will fill in.

---

## PHASE 6 — Cloud Run Deployment

- [ ] Add `Dockerfile` (see earlier message for the shape)
- [ ] From repo folder in Cloud Shell:
```
gcloud run deploy finpulse-ai --source . --region us-central1 --allow-unauthenticated
```
- [ ] Attach service account to the Cloud Run service (console → Cloud Run → service → Edit → Security tab)
- [ ] Test the public URL

---

## PHASE 7 — Submission Wrap-up

- [ ] Record demo video (≤3 min) using the live Cloud Run URL
- [ ] Build PPT (problem → solution → architecture → GPU speedup numbers → screenshots → impact)
- [ ] Write brief description (3-4 sentences)
- [ ] Submit: Deployment Link, PPT, GitHub link, Demo Video link, Brief description
