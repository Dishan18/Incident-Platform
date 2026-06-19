# AI-Powered Incident Management and Decision Support Platform

Welcome to the Incident Intelligence and NOC Command Center Platform. This is an AI-powered system designed to assist IT Operations, NOC, Infrastructure, Middleware, Database, and support groups in analyzing, triaging, and managing operational incidents.

The platform combines machine learning predictions, database overrides, date-grouped timeline tracking, and generative AI agent root cause analyses in a unified dashboard.

---

## Key Features

*   **Intelligent Incident Routing**: Automatically predicts the target assignment group (Unix/Linux, Wintel, Batch, Middleware, Network, Database) based on incident descriptions using a Random Forest Classifier.
*   **Priority and MTTR Severity Prediction**: Classifies incident severity from P1 (Critical) to P4 (Low) and estimates expected resolution durations.
*   **Cognitive AI Root Cause Analysis**: Utilizes OpenRouter (using model `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` as configured) with an automatic, direct fallback to Google's Gemini API (`gemini-2.5-flash` in JSON mode) when OpenRouter calls fail or rate-limit (429), querying current incidents against similar historical resolutions to output root causes, confidence levels, explanations, and action items.
*   **SLA Live Tracking and Timer**: Standardizes P1 priority SLA targets to **1 Hour**. Allows operators to hold the SLA clock for an incident (e.g., when forwarded to a third party) and resume it when work continues, adjusting the SLA deadline dynamically.
*   **L3 Escalation Advisor**: Evaluates L3 escalation risk (0 to 100 percent), generates escalation recommendations, and suggests target teams and justifications based on incident severity, SLA risk, and similarity comparisons. Automatically falls back to Google's Gemini API (`gemini-2.5-flash`) on OpenRouter failures, or a rule-based heuristic when offline.
*   **Sequential Year-Based IDs**: Generates sequential IDs conforming strictly to the format `INC-YYYY-000XX` based on current calendar year and resets increments appropriately.
*   **Duplicate Incident Check**: Scans incoming incident descriptions against active incidents. Uses normalized text cleaning (standardizing synonym phrases like `"login"` vs. `"log into"`, `"cant"` vs. `"can't"`) and TF-only cosine similarity (disabling IDF weighting) to reliably intercept duplicates scoring 80% or higher and present an override warning dialog.
*   **Static Layout Status Transitions**: Provides ITSM status controls (Open to Assigned to In Progress to Resolved to Closed or Cancelled) with zero layout shifting or text jumps in the UI.
*   **Multi-Team Assignments and Intersection Filters**: Supports assigning multiple comma-separated teams to an incident and filtering using intersection search (matches if any filter team is assigned).

---

## Project Structure

```text
TicketingPlatform/
├── app.py                  # Main application dashboard entry point
├── backend/
│   ├── database/           # DB connection engine (Azure Postgres) and ORM schemas
│   ├── incident/           # ITSM state machines, creators, status changers
│   └── ml/                 # Classifiers, TF-IDF similarities, Gemini and OpenRouter Agents
├── frontend/
│   ├── components/         # Status controls, timeline lists, custom cards
│   ├── pages/              # Overview stats, Incidents tracker, predictions tabs
│   └── styles/             # Global premium dark NOC dashboard styles
├── k8s/                    # Kubernetes Deployment and NodePort Service manifests
├── data/                   # Historical training datasets and notebooks
├── models/                 # Serialized scikit-learn training models (.pkl)
├── Dockerfile              # Docker container image build specifications
├── frontend.md             # Detailed Frontend Technical Docs
├── backend.md              # Detailed Backend Technical Docs
├── azure.md                # Detailed Azure Deployment and Operations Guide
├── requirements.txt        # Production dependency specifications
└── README.md               # Main repository file (This file)
```

---

## Quick Start and Setup

### 1. Configure Environment Variables
Create a `.env` file in the root directory and declare your API keys and configuration:
```env
# Google Gemini API Key for fallback operations
GEMINI_API_KEY=your_gemini_api_key_here

# OpenRouter API Key for main root cause and L3 advisor operations
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Database Configuration (Azure Postgres)
POSTGRES_HOST=your-postgres-host.postgres.database.azure.com
POSTGRES_DB=postgres
POSTGRES_USER=your_postgres_username
POSTGRES_PASSWORD=your_postgres_password

# Azure Blob Storage Configuration (for model files and RCA reports)
AZURE_STORAGE_CONNECTION_STRING=your_azure_connection_string
```
The active AI model currently used for root cause analysis and L3 advisor operations is `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` via OpenRouter, with automated direct fallback to `gemini-2.5-flash` using `GEMINI_API_KEY` on rate limits or API failures.

### 2. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Initialize and Setup the Database
Construct the relational tables on the Postgres server:
```bash
# Create the relational schemas on the Postgres server
python -m scripts.create_postgres_tables

# Validate schema tables existence
python -m scripts.test_postgres_schema
```

### 4. Start Dashboard App
```bash
streamlit run app.py --server.port 8501 --server.address 127.0.0.1
```
Open **[http://127.0.0.1:8501](http://127.0.0.1:8501)** in your browser to access the dashboard command center.

### 5. Running with Docker & Kubernetes

Alternatively, you can run the platform in a containerized environment.

#### Running with Docker
1. **Build the Container Image:**
   ```bash
   docker build -t ticketing-platform:v1 .
   ```
2. **Run the Container (passing environment variables):**
   ```bash
   docker run -p 8501:8501 --env-file .env ticketing-platform:v1
   ```

#### Running with Kubernetes
1. **Apply Manifests to Cluster:**
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```
2. **Access the Streamlit Dashboard (via Port Forwarding):**
   ```bash
   kubectl port-forward service/ticketing-platform-service 8501:8501
   ```
   Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

## Deep-Dive Documentation

For detailed technical specifications and guides, refer to:
- **Frontend Specs**: [frontend.md](file:///d:/TicketingPlatform/frontend.md)
- **Backend Specs**: [backend.md](file:///d:/TicketingPlatform/backend.md)
- **Interactive Guide**: Open the local [guide.html](file:///d:/TicketingPlatform/guide.html) in your browser.
