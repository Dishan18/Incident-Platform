import sys
import os
# Add root path D:\TicketingPlatform
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.incident.incident_repository import get_live_incidents
import pandas as pd

live_df = get_live_incidents()
preferred_order = ["Unix/Linux", "Wintel", "Batch", "Middleware", "Network", "Database"]
all_teams = set()
if not live_df.empty:
    for teams_str in live_df["teams"].dropna():
        for t in str(teams_str).split(","):
            if t.strip():
                all_teams.add(t.strip())
print("Active teams in DB:", all_teams)
all_teams_union = all_teams.union(preferred_order)
print("Union with preferred order:", all_teams_union)
teams_list = [t for t in preferred_order if t in all_teams_union] + sorted(list(all_teams_union - set(preferred_order)))
print("Final teams list:", teams_list)
