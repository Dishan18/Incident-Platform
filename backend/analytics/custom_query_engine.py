"""
Custom SQL Query Engine Module.
Executes safe SELECT queries over the combined incidents dataset using DuckDB.
"""

import time
import pandas as pd
import duckdb
import sqlglot
from sqlglot import exp

from backend.utils.data_loader import get_all_incidents
from backend.analytics.sql_validator import validate_sql

MAX_ROWS = 10000


def execute_custom_query(sql_query: str) -> dict:
    """Validate and execute a SQL query on the combined incidents dataset.

    Parameters
    ----------
    sql_query : str
        The user-supplied SQL query.

    Returns
    -------
    dict
        Contains:
        - 'success': bool
        - 'data': pd.DataFrame (on success) or None
        - 'error': str (on failure) or None
        - 'execution_time_ms': float (time taken to execute in milliseconds)
    """
    start_time = time.perf_counter()

    # 1. SQL Validation
    is_valid, err_msg = validate_sql(sql_query)
    if not is_valid:
        return {
            "success": False,
            "data": None,
            "error": f"Validation Error: {err_msg}",
            "execution_time_ms": 0.0
        }

    # 2. Append LIMIT 10000 if no LIMIT is specified
    try:
        parsed = sqlglot.parse_one(sql_query.strip().rstrip(";").strip())
        has_limit = any(isinstance(node, exp.Limit) for node in parsed.walk())
        if not has_limit:
            sql_to_run = parsed.limit(MAX_ROWS).sql()
        else:
            sql_to_run = sql_query
    except Exception as e:
        # If parsing fails here (which is rare after validation), use the raw query
        sql_to_run = sql_query

    # 3. Load analytics dataframe
    try:
        df = get_all_incidents()
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": f"Failed to retrieve dataset: {str(e)}",
            "execution_time_ms": 0.0
        }

    # 4. Connect to duckdb, register df, and run
    con = None
    try:
        con = duckdb.connect()
        con.register("incidents", df)
        
        # Execute query
        result_df = con.execute(sql_to_run).df()
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        
        return {
            "success": True,
            "data": result_df,
            "error": None,
            "execution_time_ms": round(elapsed_ms, 2)
        }
    except Exception as e:
        # Extract clean error message
        err_str = str(e)
        clean_err = err_str
        
        # DuckDB errors often have verbose traceback headers. Clean them up for NOC operators.
        if "Binder Error:" in err_str:
            clean_err = err_str[err_str.find("Binder Error:"):]
        elif "Parser Error:" in err_str:
            clean_err = err_str[err_str.find("Parser Error:"):]
        elif "Catalog Error:" in err_str:
            clean_err = err_str[err_str.find("Catalog Error:"):]
            
        return {
            "success": False,
            "data": None,
            "error": f"Execution Error:\n{clean_err}",
            "execution_time_ms": 0.0
        }
    finally:
        if con:
            try:
                con.close()
            except Exception:
                pass


def generate_query_summary(df: pd.DataFrame) -> tuple[str, dict]:
    """Programmatically calculate summary statistics and recommended visualization details.
    No LLM/AI dependency is used here.
    """
    if df.empty:
        return "No data was returned by this query.", {"chart": "none", "title": "", "x": "", "y": ""}

    num_rows = len(df)
    bullets = []

    # 1. Total Rows
    bullets.append(f"Query returned {num_rows:,} total rows.")

    # 2. Priority Distribution
    if "priority" in df.columns:
        counts = df["priority"].value_counts()
        if not counts.empty:
            parts = [f"{count} {p}" for p, count in counts.items()]
            bullets.append(f"Priority distribution: {', '.join(parts)}.")

    # 3. SLA Breaches
    if "sla_breached" in df.columns:
        # Match boolean or numeric values
        breached_count = int((df["sla_breached"] == True).sum() + (df["sla_breached"] == 1).sum() + (df["sla_breached"].astype(str).str.lower() == "true").sum())
        compliance_pct = round(((num_rows - breached_count) / num_rows) * 100, 1) if num_rows > 0 else 100.0
        bullets.append(f"SLA Compliance rate is {compliance_pct}% ({breached_count} incidents breached target SLA).")

    # 4. Affected Users
    if "affected_users" in df.columns:
        users = pd.to_numeric(df["affected_users"], errors="coerce").dropna()
        if not users.empty:
            avg_users = int(users.mean())
            bullets.append(f"Average affected users per incident: ~{avg_users:,} (min {int(users.min()):,}, max {int(users.max()):,}).")

    # 5. Dominant Team & Top Application
    team_summary = ""
    if "teams" in df.columns:
        teams_series = df["teams"].dropna().astype(str).str.split(",")
        all_teams = []
        for t_list in teams_series:
            all_teams.extend(t.strip() for t in t_list if t.strip())
        if all_teams:
            counts = pd.Series(all_teams).value_counts()
            if not counts.empty:
                team_summary = f"Dominant team: {counts.index[0]} ({counts.values[0]} incidents)"

    app_summary = ""
    if "application" in df.columns:
        counts = df["application"].value_counts()
        if not counts.empty:
            app_summary = f"top application: {counts.index[0]} ({counts.values[0]})"

    if team_summary or app_summary:
        combined = [x for x in [team_summary, app_summary] if x]
        bullets.append(f"{'; '.join(combined)}.")

    # 6. Status distribution
    if "status" in df.columns:
        counts = df["status"].value_counts()
        if not counts.empty:
            parts = [f"{count} {s.lower()}" for s, count in counts.items()]
            bullets.append(f"Incident states: {', '.join(parts)}.")

    summary_text = "\n".join([f"- {b}" for b in bullets])

    # ── Chart Recommendation Logic ──
    chart_rec = {"chart": "none", "title": "", "x": "", "y": ""}
    if num_rows > 1:
        cols = list(df.columns)
        if "created_at" in cols:
            chart_rec = {
                "chart": "histogram",
                "title": "Incident Volume Distribution over Time",
                "x": "created_at",
                "y": ""
            }
        elif "priority" in cols:
            chart_rec = {
                "chart": "histogram",
                "title": "Incident Count by Priority",
                "x": "priority",
                "y": ""
            }
        elif "teams" in cols:
            chart_rec = {
                "chart": "histogram",
                "title": "Incident Count by Assigned Team",
                "x": "teams",
                "y": ""
            }
        elif "application" in cols:
            chart_rec = {
                "chart": "histogram",
                "title": "Incident Count by Affected Application",
                "x": "application",
                "y": ""
            }

    return summary_text, chart_rec

