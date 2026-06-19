# Azure Deployment Architecture

## Overview

The Incident Intelligence Platform is deployed entirely on Microsoft Azure using a containerized architecture.

The application runs as a Dockerized Streamlit service hosted on Azure App Service and integrates with Azure PostgreSQL and Azure Blob Storage for persistence and model management.

---

# Production Architecture

```text
Internet Users
       │
       ▼
Azure App Service (Linux Container)
       │
       ▼
Docker Container
(Streamlit Application)
       │
 ┌─────┴─────┐
 ▼           ▼
Azure      Azure
Blob       PostgreSQL
Storage    Flexible Server
```

---

# Azure Resources

## Resource Group

```text
ticketing-rg
```

Contains all cloud resources for the platform.

---

## Azure Container Registry (ACR)

### Registry

```text
ticketingacrv.azurecr.io
```

### Repository

```text
ticketing-platform
```

### Current Tag

```text
v1
```

Purpose:

* Stores Docker images
* Acts as deployment source for App Service
* Enables versioned releases

Example image:

```text
ticketingacrv.azurecr.io/ticketing-platform:v1
```

---

## Azure App Service

### Application

```text
ticketing-platform-app
```

### Runtime

```text
Linux Container
```

### Port

```text
8501
```

### Container Source

```text
ticketingacrv.azurecr.io/ticketing-platform:v1
```

Purpose:

* Hosts Streamlit dashboard
* Serves all frontend and backend functionality
* Downloads models and analytics datasets at startup

---

## Azure PostgreSQL Flexible Server

### Host

```text
ticketing-postgres.postgres.database.azure.com
```

Purpose:

* Stores all incident records
* RCA metadata
* SLA tracking
* Prediction history
* RCA PDF references

Tables:

```text
live_incidents
```

Current deployment uses PostgreSQL exclusively.

SQLite has been removed from runtime operations.

---

## Azure Blob Storage

### Storage Account

```text
ticketingplatformstorage
```

Purpose:

Persistent storage for large files and generated assets.

---

# Blob Containers

## models

Stores trained ML models.

Files:

```text
priority_model.pkl
team_model.pkl
resolution_model.pkl
```

Usage:

* Downloaded automatically during startup
* Loaded lazily when predictions are requested

---

## rca-files

Stores generated RCA PDF reports.

Example:

```text
INC-2026-00014-RCA-2026-06-18.pdf
```

Usage:

* Uploaded automatically after RCA generation
* Rebuilt and re-uploaded after RCA edits

---

## analytics-data

Stores historical analytics datasets.

Files:

```text
synthetic_tickets.csv
```

Usage:

* Downloaded during startup
* Used by dashboard analytics and reporting pages

---

# Machine Learning Pipeline

## Team Prediction

Model:

```text
team_model.pkl
```

Predicts:

```text
Database
Network
Application
Security
Infrastructure
```

Fallback:

Keyword-based routing.

---

## Priority Prediction

Model:

```text
priority_model.pkl
```

Predicts:

```text
P1
P2
P3
P4
```

Fallback:

Impact scope and affected user heuristics.

---

## Resolution Prediction

Model:

```text
resolution_model.pkl
```

Predicts:

Expected resolution time.

Fallback:

```text
P1 → 30 mins
P2 → 60 mins
P3 → 180 mins
P4 → 360 mins
```

---

# RCA Pipeline

## Trigger

Closed or resolved incident.

## Inputs

* Incident details
* Similar incidents
* SLA status
* Root Cause Agent output
* L3 Escalation recommendations
* User questionnaire responses

## LLM

OpenRouter

Model:

```text
google/gemma-4-26b-a4b-it:free
```

Outputs:

```json
{
  "summary": "",
  "root_cause": "",
  "resolution": "",
  "preventive_action": ""
}
```

---

# RCA Storage Flow

```text
Generate RCA
      │
      ▼
OpenRouter LLM
      │
      ▼
JSON RCA Output
      │
      ▼
Save to PostgreSQL
      │
      ▼
Generate PDF
      │
      ▼
Upload PDF to Blob Storage
      │
      ▼
Store PDF URL in PostgreSQL
```

---

# Startup Sequence

When App Service starts:

1. Container launches.
2. Streamlit starts.
3. Blob storage connection initializes.
4. Missing models are downloaded.
5. synthetic_tickets.csv is downloaded.
6. PostgreSQL connection initializes.
7. Dashboard becomes available.

---

# Deployment Pipeline

Development Machine

```text
Code Changes
    │
    ▼
docker build
    │
    ▼
docker tag
    │
    ▼
docker push
    │
    ▼
Azure Container Registry
    │
    ▼
Azure App Service
```

---

# Updating Production

Build:

```bash
docker build -t ticketing-platform:latest .
```

Tag:

```bash
docker tag ticketing-platform:latest ticketingacrv.azurecr.io/ticketing-platform:v2
```

Push:

```bash
docker push ticketingacrv.azurecr.io/ticketing-platform:v2
```

Update App Service container tag:

```text
v1 → v2
```

Restart App Service.

---

# Local Dependencies Required

None.

The production environment is fully cloud-hosted.

Local machine is only required for:

* Development
* Debugging
* Building Docker images
* Pushing new releases

The platform continues operating even when the developer machine is offline.

---

# Operational Checklist

Verify:

* App Service status = Running
* PostgreSQL status = Available
* Blob Storage accessible
* ACR image available
* OPENROUTER_API_KEY configured
* AZURE_STORAGE_CONNECTION_STRING configured
* PostgreSQL credentials configured

If all checks pass, the platform is fully operational.
