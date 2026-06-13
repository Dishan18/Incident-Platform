# Backend Architecture Documentation

The backend is built around a relational **SQLite** database, an **SQLAlchemy ORM** layer, operational lifecycle workflows, and a dual-tier ML model (TF-IDF Cosine Similarity + Gemini-2.5-flash agent).

---

## 1. Directory Structure

The backend code resides in the `/backend` directory:

```text
backend/
├── __init__.py
├── database/
│   ├── __init__.py
│   ├── db.py                 # SQLite engine & SQLAlchemy SessionLocal
│   ├── models.py             # SQLAlchemy Incident database schema definition
│   └── incident_repository.py# SQLAlchemy operations (CRUD, updates, overrides)
├── incident/
│   ├── __init__.py
│   ├── create_incident.py    # Sequential ID generation, ML triage, inserts
│   ├── update_incident.py    # Transition rules, state updates, metric logging
│   ├── incident_repository.py# Grouping and data mapping helpers for frontend
│   └── test_create_incident.py# Basic backend workflow verification script
├── ml/
│   ├── __init__.py
│   ├── predict_incident.py   # Heuristic prediction model (Fallback)
│   ├── predict_priority.py   # Random Forest priority prediction model
│   ├── predict_resolution.py # Logistic Regression resolution time estimation
│   ├── predict_team.py       # Random Forest team assignment model
│   ├── similar_incidents.py  # TF-IDF & Cosine Similarity search
│   ├── explain_prediction.py # Statistical matching for ML model
│   ├── root_cause_agent.py   # Gemini API integration & key normalization
│   ├── test_root_cause.py    # Root cause analysis CLI runner
│   ├── train_priority.py     # Priority classifier training script
│   ├── train_resolution.py   # Resolution model training script
│   └── train_team.py         # Team routing classifier training script
└── utils/
    ├── __init__.py
    └── data_loader.py        # Loading databases & legacy CSV data mapping
```

---

## 2. Database Schema & ORM Model

Mapped to table `live_incidents` in `incident.db` via SQLAlchemy ([models.py](file:///d:/TicketingPlatform/backend/database/models.py)):

| Column Name | SQLAlchemy Type | Purpose |
| :--- | :--- | :--- |
| `incident_id` | `String` (PK) | Unique sequential ID (e.g. `INC-2026-00001`) |
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

---

## 3. Data Access Layer

*   **Repository Operations**: Managed by `db_get_incident`, `db_get_all_incidents`, `update_overrides`, and `update_status` within `database/incident_repository.py`.
*   **Module Decoupling**: Frontend components communicate with database tables through `backend/incident/incident_repository.py` which formats relational records into dictionary collections and applies robust fallbacks.
*   **Assigned Team Fallback**: If an incident's `assigned_team` database column is empty or null, it falls back to displaying `ai_predicted_team` on read-only views and form inputs.

---

## 4. Machine Learning & Generative Agents

### A. Prediction Pipeline ([predict_incident.py](file:///d:/TicketingPlatform/backend/ml/predict_incident.py))
Triggers on incident logging to pre-assign metrics:
*   *Team Recommendation*: Predicts the routing group using TF-IDF text features and a Random Forest Classifier (`team_model.pkl`).
*   *Priority Recommendation*: Combines text features, application name, environment, and user impact scale through a Random Forest Classifier (`priority_model.pkl`).
*   *Resolution Time Estimation*: Estimates resolution duration in minutes via a Ridge Regression model (`resolution_model.pkl`).

### B. Similarity Matching ([similar_incidents.py](file:///d:/TicketingPlatform/backend/ml/similar_incidents.py))
*   Loads historical synthetic tickets dataset (`data/synthetic_tickets.csv`).
*   Runs `TfidfVectorizer` (with stop words removed) to represent symptoms.
*   Uses `cosine_similarity` to identify the top 5 closest historical matches.

### C. Gemini Root Cause Agent ([root_cause_agent.py](file:///d:/TicketingPlatform/backend/ml/root_cause_agent.py))
*   **Prompt design**: Formulates a detailed contextual template combining current ticket symptoms (affected users, application, description) and historical similarity data (similar descriptions, verified root causes, resolution durations).
*   **JSON-Constrained Generation**: Configured via `generation_config={"response_mime_type": "application/json"}` to call `gemini-2.5-flash` for high-speed analysis.
*   **Key Normalizer**: Contains a `normalize_keys` helper. If the model outputs keys matching camelCase or alternate terms, they are mapped to the standard output dictionary:
    *   `root_cause`: Prediction string.
    *   `confidence`: Integer probability (0-100).
    *   `explanation`: Text details.
    *   `investigation_steps`: String array.
