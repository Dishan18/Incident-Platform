# AI-Powered Incident Management and Decision Support Platform

Welcome to the Incident Intelligence and NOC Command Center Platform. This is an AI-powered system designed to assist IT Operations, NOC, Infrastructure, Middleware, Database, and support groups in analyzing, triaging, and managing operational incidents.

The platform combines machine learning predictions, database overrides, date-grouped timeline tracking, and generative AI agent root cause analyses in a unified dashboard.

---

## Key Features

*   **Intelligent Incident Routing**: Automatically predicts the target assignment group (Unix/Linux, Wintel, Batch, Middleware, Network, Database) based on incident descriptions using a Random Forest Classifier.
*   **Priority and MTTR Severity Prediction**: Classifies incident severity from P1 (Critical) to P4 (Low) and estimates expected resolution durations.
*   **Cognitive AI Root Cause Analysis**: Utilizes `gemini-2.5-flash` or the OpenRouter API (using model `nex-agi/nex-n2-pro:free` as configured) to query current incidents against similar historical resolutions, outputting root causes, confidence levels, explanations, and action items.
*   **SLA Live Tracking and Timer**: Allows operators to hold the SLA clock for an incident (e.g., when forwarded to a third party) and resume it when work continues. The system adjusts the SLA deadline by the total paused duration and shows a live status timer.
*   **L3 Escalation Advisor**: Evaluates L3 escalation risk (0 to 100 percent), generates escalation recommendations, and suggests target teams and justifications based on incident severity, SLA risk, and similarity comparisons. Contains a rule-based fallback heuristic when the AI model is unavailable.
*   **Duplicate Incident Check**: Scans incoming incident descriptions against active incidents. If a high description similarity (80 percent or higher using TF-IDF and Cosine Similarity) is detected, it flags a warning to avoid duplicate ticket generation.
*   **Static Layout Status Transitions**: Provides ITSM status controls (Open to Assigned to In Progress to Resolved to Closed or Cancelled) with zero layout shifting or text jumps in the UI.
*   **Multi-Team Assignments and Intersection Filters**: Supports assigning multiple comma-separated teams to an incident and filtering using intersection search (matches if any filter team is assigned).

---

## Project Structure

```text
TicketingPlatform/
├── app.py                  # Main application dashboard entry point
├── backend/
│   ├── database/           # SQLite relational schemas and SQLAlchemy ORM mapping
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
├── guide.html              # Interactive System Setup and Improvements Guide
└── README.md               # Main repository file (This file)
```

---

## Quick Start and Setup

### 1. Configure API Keys
Create a `.env` file in the root directory and declare your API keys and configuration:
```env
# Google Gemini API Key for fallback operations
GEMINI_API_KEY=your_gemini_api_key_here

# OpenRouter API Key for main root cause and L3 advisor operations
OPENROUTER_API_KEY=your_openrouter_api_key_here
```
The active AI model currently used for root cause analysis and L3 escalation reasoning is `nex-agi/nex-n2-pro:free` via OpenRouter.

### 2. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Initialize and Migrate the Database

#### For Fresh / Clean Installations
Initialize the schema and migrate the base datasets:
```bash
# Setup schemas and database
python -m scripts.init_db

# Populate database with historical telemetry
python -m scripts.migrate_csv_to_db
```

#### For Existing Relational DB Instances
If you have an existing database from previous versions of the platform, apply the migration scripts to add the SLA and L3 Escalation columns:
```bash
# Add SLA breach tracking column
python -m scripts.add_sla_breached_column

# Add SLA pause log tracking column
python -m scripts.add_sla_pause_log_column

# Add L3 Escalation Advisor columns
python -m scripts.add_l3_escalation_columns
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
