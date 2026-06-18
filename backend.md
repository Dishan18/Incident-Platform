# Backend Architecture Documentation

The backend is built around an Azure PostgreSQL database, an SQLAlchemy ORM layer, operational lifecycle workflows, and a dual-tier ML model consisting of TF-IDF Cosine Similarity and a generative OpenRouter agent.

---

## 1. Directory Structure

The backend code resides in the `/backend` directory, with auxiliary setup and migration scripts in the `/scripts` directory:

```text
backend/
├── __init__.py
├── database/
│   ├── __init__.py
│   ├── db.py                 # Database engine connection (Azure PostgreSQL)
│   ├── models.py             # SQLAlchemy Incident database schema definition
│   └── incident_repository.py# SQLAlchemy operations (CRUD, updates, overrides, L3 status)
├── incident/
│   ├── __init__.py
│   ├── create_incident.py    # Sequential ID generation (ignores test codes), ML triage, inserts
│   ├── update_incident.py    # Transition rules, state updates, metric logging, SLA hold/resume
│   ├── incident_repository.py# Grouping and data mapping helpers for frontend
│   └── test_sla.py           # Unit tests validating SLA calculations and pause logic
└── ml/
    ├── __init__.py
    ├── model_registry.py     # Cloud Model registry ensuring local caching from Azure Blob Storage
    ├── predict_incident.py   # Heuristic prediction model (Fallback)
    ├── predict_priority.py   # Random Forest priority prediction model
    ├── predict_resolution.py # Logistic Regression resolution time estimation
    ├── predict_team.py       # Random Forest team assignment model
    ├── similar_incidents.py  # Normalized text TF-only similarity search (use_idf=False)
    ├── explain_prediction.py # Statistical matching for ML model
    ├── root_cause_agent.py   # OpenRouter integration and key normalization
    ├── l3_escalation_advisor.py # L3 escalation advisor utilizing LLM or fallback rules
    ├── test_duplicate_detection.py # CLI runner for duplicate checking validation
    ├── test_l3_escalation.py # CLI runner for L3 escalation advisor validation
    ├── test_root_cause.py    # Root cause analysis CLI runner
    ├── train_priority.py     # Priority classifier training script and Azure cloud uploader
    ├── train_resolution.py   # Resolution model training script and Azure cloud uploader
    └── train_team.py         # Team routing classifier training script and Azure cloud uploader

scripts/
├── add_l3_escalation_columns.py # DB migration adding L3 escalation columns
├── add_sla_breached_column.py   # DB migration adding SLA breached column
├── add_sla_pause_log_column.py  # DB migration adding SLA pause log column
├── create_postgres_tables.py    # Relational database creator for Azure PostgresFlexible
├── test_postgres_write.py       # standalone Postgres read/write/delete validator
├── test_postgres_schema.py      # Postgres schema inspector verifying tables exist
├── migrate_sqlite_to_postgres.py# Model-driven SQLite to PostgreSQL migration script
├── init_db.py                   # Relational DB initialization script
└── migrate_csv_to_db.py         # Migrate CSV ticket telemetry to SQLite DB

Deployment/
├── Dockerfile                   # Docker container build script (based on python:3.11-slim)
└── k8s/                         # Kubernetes manifests directory
    ├── deployment.yaml          # K8s deployment file exposing port 8501
    ├── service.yaml             # NodePort Service mapping port 8501 to targetPort 8501
    └── secret.yaml              # Kubernetes secret yaml for DB & OpenRouter configuration
```

---

## 2. Database Schema and ORM Model

The platform connects to Azure Database for PostgreSQL Flexible Server using secure SSL (`sslmode="require"`) and psycopg2 drivers.

Mapped to table `live_incidents` via SQLAlchemy ([models.py](file:///d:/TicketingPlatform/backend/database/models.py)):

| Column Name | SQLAlchemy Type | Purpose |
| :--- | :--- | :--- |
| `incident_id` | `String` (PK) | Unique sequential ID (for example: `INC-2026-00001`) |
| `description` | `String` | Symptom description |
| `application` | `String` | Name of affected system |
| `affected_users` | `Integer` | Scale of impact |
| `impact_scope` | `String` | single_user, department, site, enterprise |
| `environment` | `String` | Production, UAT, Development |
| `category` | `String` | Derived operational category |
| `ai_predicted_team` | `String` | Model predicted assignment group (Immutable) |
| `ai_predicted_priority` | `String` | Model predicted priority level (Immutable) |
| `ai_predicted_resolution_time` | `Float` | Model resolution duration prediction (Immutable) |
| `assigned_team` | `String` | Active operational assignment (Mutable, comma-separated list of teams) |
| `priority` | `String` | Active priority level (Mutable) |
| `root_cause` | `String` | Documented actual root cause (Mutable) |
| `status` | `String` | Lifecycle state (Open, Assigned, In Progress, Resolved, Closed, Cancelled) |
| `team_overridden` | `Boolean` | True if `assigned_team != ai_predicted_team` |
| `priority_overridden` | `Boolean` | True if `priority != ai_predicted_priority` |
| `actual_resolution_time` | `Integer` | Spent minutes logged upon resolution (Mutable) |
| `created_at` | `DateTime` | Incident creation time |
| `assigned_at` | `DateTime` | Timestamp of state transition to Assigned |
| `in_progress_at` | `DateTime` | Timestamp of state transition to In Progress |
| `resolved_at` | `DateTime` | Timestamp of state transition to Resolved |
| `closed_at` | `DateTime` | Timestamp of state transition to Closed |
| `sla_breached` | `Boolean` | True if resolution timestamp exceeded SLA limit (adjusted for pause time) |
| `sla_pause_log` | `String` (TEXT) | JSON array of pause events (for example: `[{"action": "hold", "at": "timestamp"}]`) |
| `l3_escalation_risk` | `Integer` | Estimated risk score of SLA breach or complexity (0 to 100) |
| `l3_escalation_recommended` | `Boolean` | Recommends if the incident should escalate to L3 support |
| `l3_escalation_reasons` | `String` (TEXT) | JSON array of reasons justifying the risk score and recommendation |
| `l3_escalation_team` | `String` | Recommended target team for L3 escalation |
| `rca_generated` | `Boolean` | True if closure Root Cause Analysis has been compiled |
| `rca_content` | `String` (TEXT) | JSON content representing the LLM-compiled RCA details |
| `rca_generated_at` | `DateTime` | Timestamp when the RCA was generated |
| `rca_pdf_url` | `String` | Azure Blob Storage URL/Blob reference of the compiled PDF report |

---

## 3. Data Access Layer

*   **Repository Operations**: Managed by database methods within [incident_repository.py](file:///d:/TicketingPlatform/backend/database/incident_repository.py).
    *   `db_get_incident`: Retrieves an incident by ID, detached from the session.
    *   `get_all_incidents`: Retrieves all incidents sorted by creation date.
    *   `update_status`: Updates status, operational timestamps, and resolution metrics (including `sla_breached`).
    *   `update_overrides`: Updates operational overrides.
    *   `update_sla_pause_log`: Persists the updated JSON string representing hold and resume events.
    *   `update_l3_escalation`: Persists L3 escalation risk evaluation results (risk, recommended flag, team, reasons list).
    *   `update_rca`: Persists LLM closure RCA summaries and references to Azure Blob report URLs.
*   **Module Decoupling**: Frontend components interact with database records through the frontend-facing [incident_repository.py](file:///d:/TicketingPlatform/backend/incident/incident_repository.py) layer. This converts relational objects to dictionary representations and implements fallback handlers.
*   **Assigned Team Fallback**: If an incident's `assigned_team` database column is empty or null, it falls back to displaying `ai_predicted_team` in read-only and input form layouts.

---

## 4. Machine Learning and Generative Agents

### A. Prediction Pipeline ([predict_incident.py](file:///d:/TicketingPlatform/backend/ml/predict_incident.py))
Triggers on incident logging to pre-assign metrics:
*   *Team Recommendation*: Predicts the routing group using TF-IDF text features and a Random Forest Classifier (`team_model.pkl`).
*   *Priority Recommendation*: Combines text features, application name, environment, and user impact scale through a Random Forest Classifier (`priority_model.pkl`).
*   *Resolution Time Estimation*: Estimates resolution duration in minutes via a Ridge Regression model (`resolution_model.pkl`).
*   *Heuristic Fallback Systems*: If the cloud model downloads fail or local `.pkl` files are missing (e.g., during offline setups or credential outages), the pipeline automatically and gracefully falls back to rule-based routing:
    *   *Team Fallback*: Scans keywords (e.g., `"db"`, `"sql"` &rarr; `"Database"`, `"vpn"`, `"network"` &rarr; `"Network"`, etc.).
    *   *Priority Fallback*: Dynamically assigns priority based on user counts and impact scope (e.g., enterprise or &ge;1000 users &rarr; `"P1"`).
    *   *Resolution Fallback*: Assigns priority-based resolution duration SLAs (P1 &rarr; 30 mins, P2 &rarr; 60 mins, P3 &rarr; 180 mins, P4 &rarr; 360 mins).

### B. Cloud Model Registry & Bootstrapping ([model_registry.py](file:///d:/TicketingPlatform/backend/ml/model_registry.py))
*   **Decoupled Source Control**: Keeps heavy ML model pickles (hundreds of MBs) out of the git repository.
*   **Lazy Loading**: Binaries are downloaded from the `"models"` container on Azure Blob Storage to `models/` directory dynamically at startup only if they are missing locally.
*   **Training Hook**: Model training scripts (`train_priority.py`, etc.) automatically upload trained `.pkl` artifacts to the Azure models registry container upon completion.

### C. Similarity Matching ([similar_incidents.py](file:///d:/TicketingPlatform/backend/ml/similar_incidents.py))
*   Loads active live incidents dynamically.
*   **Text Cleaning & Synonym Normalization**: Preprocesses queries and database descriptions through a `clean_text` normalizer. It standardizes synonyms (e.g. `"login"`, `"log in"`, `"logon"`, `"log into"` &rarr; `"log"`; `"db"`, `"database"` &rarr; `"database"`; `"cant"`, `"cannot"` &rarr; `"cannot"`) and resolves verb/noun inflections.
*   **TF-Only Cosine Similarity**: Sets `use_idf=False` in `TfidfVectorizer` to use pure term-frequency cosine similarity. This prevents IDF weights from artificially penalizing common words in short incident descriptions, keeping similarities robust and linear.
*   Finds matching incidents above the **80% similarity threshold** to trigger the duplicate incident warning dialog before ticket submission.
*   For historical lookups, searches the synthetic tickets dataset (`data/synthetic_tickets.csv`) to locate the top 5 closest historical resolutions. Used to populate reference models for root cause investigations.

### C. OpenRouter Root Cause Agent ([root_cause_agent.py](file:///d:/TicketingPlatform/backend/ml/root_cause_agent.py))
*   **API Configuration**: Configured to call the OpenRouter API endpoint. It defaults to using the `google/gemma-4-26b-a4b-it:free` model.
*   **Prompt design**: Formulates a detailed contextual template combining current ticket symptoms (affected users, application, description) and historical similarity data (similar descriptions, verified root causes, resolution durations).
*   **JSON-Constrained Generation**: Uses system instructions to enforce valid JSON generation, filtering out markdown selectors and code fences.
*   **Key Normalizer**: Contains a `normalize_keys` helper. If the model outputs keys matching camelCase or alternate terms, they are mapped to the standard output dictionary:
    *   `root_cause`: Prediction string.
    *   `confidence`: Integer probability (0 to 100).
    *   `explanation`: Text details.
    *   `investigation_steps`: String array.

### D. L3 Escalation Advisor ([l3_escalation_advisor.py](file:///d:/TicketingPlatform/backend/ml/l3_escalation_advisor.py))
*   **Objective**: Determines whether an active incident should be escalated to L3 support based on SLA risk, severity, impact scope, historical similarity, and root cause outcomes.
*   **LLM Analyzer**: Submits ticket parameters and similarity structures to OpenRouter using the `google/gemma-4-26b-a4b-it:free` model, enforcing a structured JSON schema response.
*   **Key Normalizer**: Normalizes keys to standard elements: `risk_score`, `escalate`, `recommended_team`, and `reasons`.
*   **Rule-based Fallback**: Executes heuristic evaluations if the API is unavailable or fails:
    *   Increases risk if priority is P1 (plus 40 percent) or P2 (plus 25 percent).
    *   Increases risk if affected user count exceeds 1000 (plus 25 percent).
    *   Increases risk if impact scope is enterprise (plus 20 percent).
    *   Increases risk if predicted resolution time exceeds 240 minutes (plus 15 percent).
    *   Recommends escalation if total risk score is 50 percent or higher.

---

## 5. Deployment and Containerization

The backend service is fully containerized and ready for cloud-native orchestration.

### A. Docker Architecture
- **Base Image:** `python:3.11-slim` ensures a minimal, secure container footprint.
- **Working Directory:** `/app` serves as the container root.
- **Dependency Caching:** `requirements.txt` is copied and packages are installed using `--no-cache-dir` prior to copying the rest of the application code to optimize image layer caching.
- **Exposed Port:** Port `8501` is exposed to handle HTTP traffic for Streamlit dashboard rendering.
- **Startup Command:** Runs Streamlit binding to all interfaces (`0.0.0.0`) inside the container.

### B. Kubernetes Orchestration
- **Deployment Manifest (`deployment.yaml`):**
  - Defines `replicas: 1` (scalable to support high-availability needs).
  - Uses label selection `app: ticketing-platform` to link pods to the controller.
  - Pulls image `ticketing-platform:v1` locally using `imagePullPolicy: IfNotPresent` to reduce deployment network overhead.
- **Service Manifest (`service.yaml`):**
  - Defines a `NodePort` service named `ticketing-platform-service`.
  - Maps external requests on cluster node interfaces to target container port `8501`.
  - Easily queryable using Kubernetes port forwarding or node interface access.
