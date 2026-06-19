# Frontend Architecture Documentation

The frontend is built on Streamlit using a premium custom dark enterprise design system. It is structured around modular components, page views, and global themes.

---

## 1. Directory Structure

The frontend code resides in the `/frontend` directory:

```text
frontend/
├── __init__.py
├── components/
│   ├── __init__.py
│   ├── cards.py       # Reusable UI cards, priority/status badges
│   ├── filters.py     # Analytics page search and multiselect filter logic
│   ├── sidebar.py     # Platform navigation and sidebar branding
│   ├── tables.py      # Detail view drawer (Read-only / Edit modes, SLA tracking)
│   └── timeline.py    # Date-grouped timeline incident cards
├── pages/
│   ├── __init__.py
│   ├── overview.py    # KPI metrics dashboard and active summary
│   ├── incidents.py   # Incident workflow, creation dialog, timeline layout
│   ├── analytics.py   # Plotly charting dashboard (workload and trends)
│   └── predictions.py # ML prediction explainability, LLM root cause agent, and L3 Advisor
└── styles/
    └── theme.py       # Global CSS injection, palette tokens, Plotly styling
```

---

## 2. Design System and Theming ([theme.py](file:///d:/TicketingPlatform/frontend/styles/theme.py))

The theme implements a high-end SOC/NOC command center look with the following tokens:
*   **Colors**: Custom dark scheme (Background `BG = "#080A10"`, Cards `CARD_BG = "#0F121E"`, Borders `BORDER = "#1B223C"`, Accent Blue `ACCENT = "#4B6BF5"`, Text `TEXT = "#F3F4F6"`, Muted Text `MUTED = "#94A3B8"`, Hover state `HOVER = "#1E293B"`).
*   **Typography**: Injects `Inter` from Google Fonts.
*   **CSS Injection**: Injects overrides into Streamlit to hide default branding, style sidebars, dialogs, scrollbars, input fields, tabs, and custom UI elements.
*   **Plotly Template**: Exports `get_plotly_template()` to apply identical dark-theme parameters, margins, colors, and fonts to all data charts.

---

## 3. UI Component Guide

### A. Detail Drawer ([tables.py](file:///d:/TicketingPlatform/frontend/components/tables.py))
Renders the side drawer on the **Incidents** page using a split-column layout (55 percent timeline, 45 percent detail drawer). It supports two modes:
1.  **Read-Only View**: Displays metadata, application routing, current assigned team, and a vertical lifecycle timeline (Created to Assigned to In Progress to Resolved to Closed or Cancelled).
    *   *Layout Shift Prevention*: Timeline steps are locked to a fixed height (`24px`). When no timestamp is available, a transparent placeholder keeps the height static.
2.  **Edit View**: Injects editable controls (multiselect team selector, priority selectbox, root cause textarea, resolution time input). Saving updates toggles database override markers (`team_overridden` / `priority_overridden`).

#### SLA Status Component
Features a live, dynamic SLA status block driven by Streamlit fragments.
*   **Live Updates**: Updates every 1.0 seconds when the incident is active.
*   **Calculations**:
    *   Deadline is computed as `created_at + SLA_HOURS[priority] + total_paused_seconds`.
    *   `total_paused_seconds` is calculated by parsing the `sla_pause_log` column containing JSON records.
*   **UI States**:
    *   *Paused SLA*: Displays a yellow "SLA Paused" badge and a live counter showing how long the current pause has lasted.
    *   *Running SLA*: Shows green/orange "On Track" or red "SLA Breached" badge, alongside a countdown timer.
    *   *Completed SLA*: Renders a static "Met SLA" or "Breached SLA" status showing final MTTR metrics.
*   **Controls**: Renders a yellow "Hold SLA" button (running state) or a green "Resume SLA" button (paused state) when the status is `In Progress`.

#### L3 Escalation Advisor Component (Predictions Tab Only)
Displays escalation risk assessment and recommendations under the dedicated **Predictions** tab.
*   **Dynamic Analysis**: Retrieves L3 evaluation metrics (score, recommendation, reasons list) from the database. If missing, it dynamically runs similar incidents matching, queries the OpenRouter API (using model `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`) with a direct fallback to Google's Gemini API (`gemini-2.5-flash`), and persists the results.
*   **Risk Metric Card**: Highlights the risk percentage using colored bands: Low (green), Medium (yellow), High (orange), or Critical (red).
*   **Recommendation Card**: Shows "Escalate to L3 [Team] Team" (red) or "Continue with L2 Support" (green).
*   **Reasons Bulletin**: Outputs bulleted reason statements explaining the evaluation factors.

---

## 4. Pages

### A. Overview Page ([overview.py](file:///d:/TicketingPlatform/frontend/pages/overview.py))
*   Renders high-level KPI blocks (Active, Unassigned, Priority distribution) using custom HTML metrics cards.
*   Provides status overview charts showing unassigned incident workload.

### B. Incidents Page ([incidents.py](file:///d:/TicketingPlatform/frontend/pages/incidents.py))
*   **Creation Modal**: Includes a modal dialog (`st.dialog`) to log new incidents.
    *   *Duplicate Check Warning*: Intercepts submission. If the description matches an active incident with 80 percent or higher similarity, it pauses creation to display a warning card showing the match ID, similarity score, status, team, application, and creation timestamp.
    *   *User Choices*: Allows operators to "View Incident", "Create Anyway", or "Go Back and Edit".
*   **Filter Panel**: A 5-column filter bar allowing search by Status, Priority, Application, Date Range, and **Teams** (supporting multi-selection and intersection checks where an incident is kept if it matches any of the filtered teams).

### C. Analytics Page ([analytics.py](file:///d:/TicketingPlatform/frontend/pages/analytics.py))
Contains a Plotly-backed dashboard grouped in tabs:
*   *Volume and Trends*: Incident count by application, month-by-month priority trends, donut chart.
*   *Workload*: Heatmap of team assignments versus incident priority levels.
*   *Performance*: Box plots of resolution times by priority, and bar distribution of root causes.

### D. Predictions Page ([predictions.py](file:///d:/TicketingPlatform/frontend/pages/predictions.py))
*   **Triage Selector**: Left-hand filtered incident selector.
*   **AI Root Cause Agent and L3 Advisor**: Displays predicted root causes, confidence metrics, and investigation steps.
*   **Session Caching**: Stores generated root cause analyses in `st.session_state` keys based on the selected incident ID to avoid redundant API queries. Includes a **Re-analyze** button to purge keys and force a recalculation.
*   **Explainability**: Displays matching statistics from similar historical tickets (most common teams, common priority, average resolution time).

---

## 5. Containerized Hosting
For production or containerized deployments, the Streamlit frontend runs internally on container port `8501`. Docker containers expose this interface port externally, and Kubernetes deployments expose it via a NodePort Service or port-forwarding to make the premium dark UI dashboard accessible to operators at cluster nodes or localhost endpoints.
