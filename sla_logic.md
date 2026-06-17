# SLA Hold / Resume (Pause SLA Clock)

Allow operators to pause the SLA clock when an incident is forwarded to a third party, and resume it when work continues. The SLA deadline effectively shifts forward by the total paused duration.

## Design Decisions

### How to store pause events

Rather than adding a separate `sla_pauses` table (which requires foreign keys and joins), we'll store a **JSON log** in a single `TEXT` column on the incident:

```json
[
  {"action": "hold",   "at": "2026-06-16 14:00:00"},
  {"action": "resume", "at": "2026-06-16 15:30:00"}
]
```

This keeps things simple — one column, one migration, no new tables. Each hold/resume pair represents one pause window.

### SLA calculation adjustment

```
effective_elapsed = wall_clock_elapsed − total_paused_seconds
```

The SLA deadline displayed in the UI becomes:

```
adjusted_deadline = created_at + SLA_HOURS[priority] + total_paused_duration
```

---

## Proposed Changes

### Database & Migration

#### [MODIFY] [models.py](file:///d:/TicketingPlatform/backend/database/models.py)

Add one column:

```python
sla_pause_log = Column(String, default="[]")  # JSON array of hold/resume events
```

#### [NEW] [add_sla_pause_log_column.py](file:///d:/TicketingPlatform/scripts/add_sla_pause_log_column.py)

SQLite migration script following the pattern in [add_sla_breached_column.py](file:///d:/TicketingPlatform/scripts/add_sla_breached_column.py):

```sql
ALTER TABLE live_incidents ADD COLUMN sla_pause_log TEXT DEFAULT '[]'
```

---

### Backend Logic

#### [MODIFY] [update_incident.py](file:///d:/TicketingPlatform/backend/incident/update_incident.py)

- Add two new functions: `hold_incident_sla(incident_id)` and `resume_incident_sla(incident_id)`.
- Each appends a `{"action": "hold"/"resume", "at": "<timestamp>"}` entry to the `sla_pause_log` JSON.
- Guards: can only hold when status is "In Progress" and not already on hold; can only resume when currently on hold.
- Update the SLA breach calculation in `update_incident_status()` to subtract total paused seconds before comparing against the deadline.

#### [MODIFY] [incident_repository.py (database)](file:///d:/TicketingPlatform/backend/database/incident_repository.py)

- Add `update_sla_pause_log(incident_id, pause_log_json)` function to persist the updated JSON string.

#### [MODIFY] [incident_repository.py (frontend)](file:///d:/TicketingPlatform/backend/incident/incident_repository.py)

- Include `sla_pause_log` in the `get_incident_by_id()` dict serialization.

---

### Frontend UI

#### [MODIFY] [tables.py](file:///d:/TicketingPlatform/frontend/components/tables.py)

1. **Hold/Resume toggle button**: Displayed below the SLA Status section when the incident status is `In Progress`. Shows:
   - **"⏸ Hold SLA"** button (amber) when SLA is running.
   - **"▶ Resume SLA"** button (green) when SLA is paused.

2. **SLA display adjustments**: The `render_live_sla_counter` fragment will:
   - Parse `sla_pause_log` to compute `total_paused_seconds`.
   - Shift the deadline forward by `total_paused_seconds`.
   - Show a **"⏸ SLA Paused"** badge (amber) instead of "On Track" / "SLA Breached" when currently on hold.
   - Display "Paused for: HH:MM:SS" as a live counter showing how long the current pause has lasted.

---

## Verification Plan

### Manual Verification

1. Create or pick an "In Progress" incident.
2. Click **"⏸ Hold SLA"** → verify badge changes to "SLA Paused", countdown stops, paused duration counter starts.
3. Click **"▶ Resume SLA"** → verify countdown resumes from adjusted position (deadline shifted).
4. Resolve the incident → verify SLA breach calculation correctly subtracts paused time.
