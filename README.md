# AI-Powered Incident Management & Decision Support Platform

## Overview

This project is an AI-powered Incident Management and Decision Support Platform designed to assist IT Operations, NOC, Infrastructure, Middleware, Database, and Support teams in handling operational incidents more efficiently.

The platform combines traditional incident management workflows with Machine Learning-based recommendations to:

* Predict the most appropriate support team for an incident
* Predict incident priority
* Estimate resolution time
* Retrieve similar historical incidents
* Explain prediction decisions using historical evidence
* Track incident lifecycle through a modern operational dashboard

The goal is not to replace human operators but to accelerate triage, routing, and decision-making during incident handling.

---

# Problem Statement

In large organizations, thousands of incidents are raised every month.

Incident assignment is often:

* Manual
* Slow
* Dependent on operator experience
* Prone to incorrect routing
* Difficult during major outages

Incorrect routing can increase Mean Time To Resolution (MTTR), delay business recovery, and overload support teams.

This platform uses historical incident data and machine learning models to recommend the best course of action immediately when an incident is raised.

---

# Project Objectives

The system aims to:

### Intelligent Incident Routing

Automatically predict which team should receive the incident.

Examples:

* Database
* Network
* Wintel
* Unix/Linux
* Middleware
* Batch

---

### Priority Prediction

Estimate incident severity:

* P1 (Critical)
* P2 (High)
* P3 (Medium)
* P4 (Low)

---

### Resolution Time Prediction

Estimate expected resolution duration using historical incident patterns.

---

### Similar Incident Retrieval

Search historical incidents and surface the most relevant matches.

This helps operators answer:

* Have we seen this before?
* How was it resolved?
* Which team handled it?
* What was the root cause?

---

### Explainable AI

Provide evidence behind recommendations rather than acting as a black box.

Examples:

* Similar incidents were routed to Network
* Most common root cause was VPN Tunnel Failure
* Average resolution time was 320 minutes

---

### Incident Lifecycle Management

Track incidents through their operational workflow:

Open

↓

Assigned

↓

In Progress

↓

Resolved

↓

Closed

---

# Architecture

## High-Level Flow

User Raises Incident

↓

Prediction Engine

↓

Team Prediction

Priority Prediction

Resolution Prediction

↓

Similar Incident Retrieval

↓

Explanation Layer

↓

Operator Review

↓

Incident Lifecycle Tracking

---

# Technology Stack

## Frontend

* Streamlit
* Custom Dark Theme
* Responsive Dashboard UI

## Backend

* Python
* Pandas
* NumPy

## Machine Learning

* Scikit-learn
* TF-IDF Vectorization
* Random Forest
* Logistic Regression
* Similarity Search

## Data Generation

* Faker
* Synthetic Enterprise Incident Generator

---

# Project Structure

```text
TicketingPlatform/

├── app.py

├── backend/
│   ├── incident/
│   │   ├── create_incident.py
│   │   ├── update_incident.py
│   │   ├── incident_repository.py
│   │
│   ├── ml/
│   │   ├── predict_team.py
│   │   ├── predict_priority.py
│   │   ├── predict_resolution.py
│   │   ├── predict_incident.py
│   │   ├── similar_incidents.py
│   │   ├── explain_prediction.py
│   │
│   └── utils/
│       └── data_loader.py

├── frontend/
│   ├── pages/
│   │   ├── overview.py
│   │   ├── incidents.py
│   │   ├── analytics.py
│   │   └── predictions.py
│   │
│   ├── components/
│   └── styles/

├── data/
│   ├── synthetic_tickets.csv
│   ├── live_incidents.csv
│   └── notebooks/

├── models/
│   ├── team_model.pkl
│   ├── priority_model.pkl
│   └── resolution_model.pkl

└── README.md
```

---

# Dataset

A synthetic enterprise incident dataset containing approximately:

* 20,000 historical incidents

Generated attributes include:

* Description
* Application
* Team
* Priority
* Resolution Time
* Environment
* Category
* Root Cause
* Affected Users
* Impact Scope
* Created Timestamp
* Resolved Timestamp

The dataset simulates real-world IT operations environments.

---

# Machine Learning Models

## Team Prediction Model

Input:

* Incident Description

Output:

* Support Team

Example:

```text
VPN connection failed for multiple users

→ Network
```

Performance:

```text
Micro F1 ≈ 0.85
```

---

## Priority Prediction Model

Inputs:

* Application
* Affected Users
* Impact Scope

Output:

* P1 / P2 / P3 / P4

Performance:

```text
Accuracy ≈ 0.79
```

---

## Resolution Time Prediction Model

Inputs:

* Application
* Priority
* Team
* Impact

Output:

* Estimated Resolution Time

Performance:

```text
MAE ≈ 48 minutes
R² ≈ 0.71
```

---

# Features

## Dashboard Overview

Provides:

* Total Incidents
* Open Incidents
* Resolved Incidents
* Priority Distribution
* Team Workload
* Trend Analysis

---

## Incident Management

Create incidents manually.

Track lifecycle progression.

Update statuses:

* Open
* Assigned
* In Progress
* Resolved
* Closed
* Cancelled

---

## Analytics

Provides:

* Incident Trends
* Root Cause Analysis
* Team Distribution
* Application Distribution
* Resolution Time Analysis
* Priority Heatmaps

---

## Prediction Center

Given a new incident:

The system predicts:

* Recommended Team
* Priority
* Estimated Resolution Time

The platform also:

* Finds similar incidents
* Explains recommendations
* Displays historical evidence

---

# Example Workflow

Operator enters:

```text
VPN connection failed for multiple users across the enterprise.
```

System predicts:

```text
Recommended Team:
Network

Predicted Priority:
P1

Estimated Resolution Time:
371 minutes
```

Historical Matches:

```text
VPN connection failed affecting multiple users

Firewall blocking traffic

Network latency exceeds threshold
```

Explanation:

```text
4 of 5 similar incidents were routed to Network.

Most common root cause:
VPN Tunnel Failure

Average resolution time:
318 minutes
```

---

# Future Enhancements

## Semantic Search

Replace TF-IDF retrieval with:

* Sentence Transformers
* Embedding-based retrieval

For more accurate historical incident matching.

---

## Confidence Scores

Display prediction probabilities for:

* Team Assignment
* Priority Classification

---

## Root Cause Prediction

Predict likely root cause directly from incident descriptions.

---

## Automated Resolution Suggestions

Recommend potential fixes based on historical incidents.

---

## LLM Integration

Integrate a Large Language Model to:

* Summarize incidents
* Generate investigation steps
* Draft incident reports
* Recommend troubleshooting actions

---

## Multi-Agent Operations Center

Future vision:

* Incident Triage Agent
* Routing Agent
* Root Cause Agent
* Resolution Recommendation Agent

Working together as an AI-powered IT Operations Copilot.

---

# Running the Project

Install dependencies:

```bash
pip install -r requirements.txt
```

Run Streamlit:

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

---

# Project Status

Current Stage:

```text
Phase 1 — Data Generation              ✅
Phase 2 — EDA & Validation             ✅
Phase 3 — Dashboard Development        ✅
Phase 4 — ML Model Training            ✅
Phase 5 — Similar Incident Retrieval   ✅
Phase 6 — Explainable AI               ✅
Phase 7 — Advanced AI Features         🚧
```

This project demonstrates the complete pipeline from incident data generation and analytics to AI-assisted incident routing and operational decision support.
