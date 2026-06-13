# AI-Powered Incident Management & Decision Support Platform

Welcome to the **Incident Intelligence & NOC Command Center Platform**. This is an AI-powered system designed to assist IT Operations, NOC, Infrastructure, Middleware, Database, and support groups in analyzing, triaging, and managing operational incidents.

The platform combines machine learning predictions, database overrides, date-grouped timeline tracking, and generative AI agent root cause analyses in a unified dashboard.

---

## 🚀 Key Features

*   **Intelligent Incident Routing**: Automatically predicts the target assignment group (Unix/Linux, Wintel, Batch, Middleware, Network, Database) based on incident descriptions using a Random Forest Classifier.
*   **Priority & MTTR Severity Prediction**: Classifies incident severity from P1 (Critical) to P4 (Low) and estimates expected resolution durations.
*   **Cognitive AI Root Cause Analysis**: Utilizes `gemini-2.5-flash` to query current incidents against similar historical resolutions, outputting root causes, confidence levels, explanations, and action items.
*   **Static Layout Status Transitions**: Provides ITSM status controls (Open &rarr; Assigned &rarr; In Progress &rarr; Resolved &rarr; Closed/Cancelled) with zero layout shifting or text jumps.
*   **Multi-Team Assignments & Intersection Filters**: Supports assigning multiple comma-separated teams to an incident and filtering using intersection search (matches if any filter team is assigned).

---

## 📂 Project Structure

```text
TicketingPlatform/
├── app.py                  # Main application dashboard entry point
├── backend/
│   ├── database/           # SQLite relational schemas & SQLAlchemy ORM mapping
│   ├── incident/           # ITSM state machines, creators, status changers
│   └── ml/                 # Classifiers, TF-IDF similarities, Gemini Agent
├── frontend/
│   ├── components/         # Status controls, timeline lists, custom cards
│   ├── pages/              # Overview stats, Incidents tracker, predictions tabs
│   └── styles/             # Global premium dark NOC dashboard styles
├── data/                   # Historical training datasets & notebooks
├── models/                 # Serialized scikit-learn training models (.pkl)
├── frontend.md             # Detailed Frontend Technical Docs
├── backend.md              # Detailed Backend Technical Docs
├── guide.html              # Interactive System Setup & Improvements Guide
└── README.md               # Main repository file (This file)
```

---

## 🛠️ Quick Start & Setup

### 1. Configure API Key
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 2. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Initialize Relational DB
```bash
# Setup schemas & database
python -m scripts.init_db

# Populate database with historical telemetry
python -m scripts.migrate_csv_to_db
```

### 4. Start Dashboard App
```bash
streamlit run app.py --server.port 8501 --server.address 127.0.0.1
```
Open **[http://127.0.0.1:8501](http://127.0.0.1:8501)** in your browser to access the dashboard command center.

---

## 📖 Deep-Dive Documentation

For detailed technical specifications and guides, refer to:
- 🎨 **Frontend Specs**: [frontend.md](file:///d:/TicketingPlatform/frontend.md)
- ⚙️ **Backend Specs**: [backend.md](file:///d:/TicketingPlatform/backend.md)
- 🖥️ **Interactive Interactive Guide**: Open the local [guide.html](file:///d:/TicketingPlatform/guide.html) in your browser.
