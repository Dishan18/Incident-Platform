# Frontend Architecture Documentation

The frontend is built on **Streamlit** using a premium custom dark enterprise design system. It is structured around modular components, page views, and global themes.

---

## 1. Directory Structure

The frontend code resides in the `/frontend` directory:

```text
frontend/
├── __init__.py
├── components/
│   ├── __init__.py
│   ├── cards.py       # Reusable UI cards, priority/status badges
│   ├── filters.py     # Analytics page search & multiselect filter logic
│   ├── sidebar.py     # Platform navigation & sidebar branding
│   ├── tables.py      # Detail view drawer (Read-only / Edit modes)
│   └── timeline.py    # Date-grouped timeline incident cards
├── pages/
│   ├── __init__.py
│   ├── overview.py    # KPI metrics dashboard & active summary
│   ├── incidents.py   # Incident workflow, creation dialog, timeline layout
│   ├── analytics.py   # Plotly charting dashboard (workload & trends)
│   └── predictions.py # ML prediction explainability & Gemini root cause agent
└── styles/
    └── theme.py       # Global CSS injection, palette tokens, Plotly styling
```

---

## 2. Design System & Theming ([theme.py](file:///d:/TicketingPlatform/frontend/styles/theme.py))

The theme implements a high-end SOC/NOC command center look with the following tokens:
*   **Colors**: Custom dark scheme (Background `BG = "#080A10"`, Cards `CARD_BG = "#0F121E"`, Borders `BORDER = "#1B223C"`, Accent Blue `ACCENT = "#4B6BF5"`, Text `TEXT = "#F3F4F6"`, Muted Text `MUTED = "#94A3B8"`, Hover state `HOVER = "#1E293B"`).
*   **Typography**: Injects `Inter` from Google Fonts.
*   **CSS Injection**: Injects overrides into Streamlit to hide default branding, style sidebars, dialogs, scrollbars, input fields, tabs, and custom UI elements.
*   **Plotly Template**: Exports `get_plotly_template()` to apply identical dark-theme parameters, margins, colors, and fonts to all data charts.

---

## 3. UI Component Guide

### A. Detail Drawer ([tables.py](file:///d:/TicketingPlatform/frontend/components/tables.py))
Renders the side drawer on the **Incidents** page:
*   **Dual-Mode Render**:
    *   *Read-Only View*: Displays complete metadata, application routing, current assigned team, and a vertical lifecycle timeline (Created $\rightarrow$ Assigned $\rightarrow$ In Progress $\rightarrow$ Resolved $\rightarrow$ Cancelled/Closed).
    *   *Edit View*: Injects editable controls (multiselect team selector, priority selectbox, root cause textarea, resolution time input). Saving updates toggles database override markers (`team_overridden` / `priority_overridden`).
*   **Clean Status Transitions**: Implements status buttons utilizing Streamlit `on_click` callbacks with python arguments (`args=(inc_id, next_status)`). Clicking buttons executes database modifications and refreshes cleanly.
*   **Layout Shift Prevention**: The timeline step styles(`.timeline-step`) are locked to a fixed height (`24px`). Label text and timestamps are aligned side-by-side using flex spacing. When no timestamp is available, a transparent placeholder `<div class="timeline-step-time" style="color: transparent; user-select: none;">0000-00-00 00:00:00</div>` is rendered to keep the height completely static.

### B. Timeline Layout ([timeline.py](file:///d:/TicketingPlatform/frontend/components/timeline.py))
Renders incidents grouped by creation date (Today, Yesterday, Date):
*   Displays incident cards with priority badges, status, title, application, and affected users count.
*   Includes a centered **View** button that sets the selected session state ID, showing the detail drawer on the right.

### C. Sidebar Navigation ([sidebar.py](file:///d:/TicketingPlatform/frontend/components/sidebar.py))
*   Renders a custom radio button list configured to act as navigation tabs.
*   Shows NOC-themed branding with the logo, title, and current running mode indicators.

---

## 4. Pages

### A. Overview Page ([overview.py](file:///d:/TicketingPlatform/frontend/pages/overview.py))
*   Renders high-level KPI blocks (Active, Unassigned, Priority distribution) using custom HTML metrics cards.
*   Provides status overview charts showing unassigned incident workload.

### B. Incidents Page ([incidents.py](file:///d:/TicketingPlatform/frontend/pages/incidents.py))
*   **Creation Modal**: Includes an `st.dialog` modal form to log new incidents (Description, Application, Scope, Users, Environment).
*   **Filter Panel**: A 5-column filter bar allowing search by Status, Priority, Application, Date Range, and **Teams** (supporting multi-selection and intersection checks).

### C. Analytics Page ([analytics.py](file:///d:/TicketingPlatform/frontend/pages/analytics.py))
Contains a Plotly-backed dashboard grouped in tabs:
*   *Volume & Trends*: Incident count by application, month-by-month priority trends, donut chart.
*   *Workload*: Heatmap of team assignments versus incident priority levels.
*   *Performance*: Box plots of resolution times by priority, and bar distribution of root causes.

### D. Predictions Page ([predictions.py](file:///d:/TicketingPlatform/frontend/pages/predictions.py))
*   **Triage Selector**: Left-hand filtered incident selector.
*   **AI Root Cause Agent**: Calls `analyze_root_cause()` to show Gemini-predicted root causes, confidence percentages, explanations, and investigation steps. Includes a **Re-analyze** button to clear session cache and re-run Gemini.
*   **Explainability**: Displays matching statistics from similar historical tickets (most common teams, common priority, avg resolution time).
