"""
Custom Analytics Component.
Renders the conversational BI AI interface for query generation, editing, execution, and export.
"""

import time
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from backend.analytics.custom_query_engine import execute_custom_query, generate_query_summary
from backend.analytics.llm_sql_generator import generate_sql
from backend.analytics.report_exporter import export_to_csv, export_to_excel, export_to_pdf
import frontend.styles.theme as theme


def get_df_hash(df: pd.DataFrame) -> str:
    """Generate a lightweight hash based on dataframe shape to validate caching."""
    return f"{df.shape[0]}_{df.shape[1]}"


@st.cache_data(ttl=120)
def cached_execute_query(sql_query: str, df_hash: str) -> dict:
    """Executes SQL query with a 2-minute cache based on query and dataset hash."""
    return execute_custom_query(sql_query)


def render_custom_analytics(df: pd.DataFrame) -> None:
    """Renders the AI Custom Analytics query interface."""
    # ── Initialize session state ──
    if "nl_prompt" not in st.session_state:
        st.session_state["nl_prompt"] = ""
    if "sql_query" not in st.session_state:
        st.session_state["sql_query"] = ""
    if "query_results" not in st.session_state:
        st.session_state["query_results"] = None
    if "query_history" not in st.session_state:
        st.session_state["query_history"] = []

    df_hash = get_df_hash(df)

    st.markdown('<div class="custom-analytics-container">', unsafe_allow_html=True)
    st.subheader("AI Custom Analytics Command Center")
    st.markdown(
        "Describe what query or metric breakdown you need in natural language below to let the AI "
        "model write SQL for you. You can run the query, refine the SQL manually, and export reports directly."
    )

    # ── Render query history in sidebar ──
    if st.session_state["query_history"]:
        with st.sidebar:
            st.write("---")
            st.subheader("Recent Queries")
            for idx, hist in enumerate(st.session_state["query_history"]):
                hist_title = hist.get("prompt")
                if len(hist_title) > 30:
                    hist_title = hist_title[:27] + "..."
                if st.button(hist_title, key=f"hist_btn_{idx}", use_container_width=True):
                    st.session_state["nl_prompt"] = hist.get("prompt")
                    st.session_state["sql_query"] = hist.get("sql")
                    st.session_state["query_results"] = None
                    st.rerun()

    # ── Natural Language prompt block ──
    prompt_input = st.text_area(
        "Natural Language Request",
        placeholder="e.g. Show all P1 Wintel incidents resolved after 240 minutes during June.",
        key="nl_prompt"
    )

    col_gen, _ = st.columns([0.25, 0.75])
    with col_gen:
        if st.button("Generate SQL", type="primary", use_container_width=True):
            if not st.session_state["nl_prompt"].strip():
                st.warning("Please enter a natural language request first.")
            else:
                with st.spinner("Generating SQL query..."):
                    try:
                        generated = generate_sql(st.session_state["nl_prompt"])
                        st.session_state["sql_query"] = generated
                        st.session_state["query_results"] = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to generate SQL: {str(e)}")

    # ── SQL editor block ──
    sql_editor = st.text_area(
        "Generated SQL Query (Editable)",
        height=180,
        placeholder="SELECT * FROM incidents LIMIT 10;",
        key="sql_query"
    )

    col_run, col_info = st.columns([0.25, 0.75])
    with col_run:
        if st.button("Run Query", type="secondary", use_container_width=True):
            if not st.session_state["sql_query"].strip():
                st.warning("Please provide or generate a SQL query first.")
            else:
                with st.spinner("Executing query..."):
                    # Execute query
                    res = cached_execute_query(st.session_state["sql_query"], df_hash)
                    
                    if res["success"]:
                        res_df = res["data"]
                        # Generate programmatic summary and chart recommendation (no AI dependency)
                        summary_text, chart_rec = generate_query_summary(res_df)
                        res["summary_text"] = summary_text
                        res["chart_rec"] = chart_rec

                        # Save to history list (deduplicated)
                        history_entry = {
                            "prompt": st.session_state["nl_prompt"] or f"SQL: {st.session_state['sql_query'][:25]}...",
                            "sql": st.session_state["sql_query"]
                        }
                        if history_entry not in st.session_state["query_history"]:
                            st.session_state["query_history"].insert(0, history_entry)
                            # Limit to top 8 entries
                            st.session_state["query_history"] = st.session_state["query_history"][:8]
                    
                    st.session_state["query_results"] = res
                    st.rerun()
    with col_info:
        st.markdown(
            '<div style="color: var(--text-muted); font-size: 0.85em; margin-top: 8px;">'
            '⚡ <em>Read-only SELECT queries. Output is programmatically capped at a maximum of 10,000 rows.</em>'
            '</div>',
            unsafe_allow_html=True
        )

    # ── Display Query Results ──
    results = st.session_state["query_results"]
    if results:
        theme.vertical_spacer(16)
        if not results["success"]:
            st.error(results["error"])
        else:
            res_df = results["data"]
            exec_time = results["execution_time_ms"]
            summary_text = results.get("summary_text", "")
            chart_rec = results.get("chart_rec", None)

            # Metadata bar
            st.markdown(
                f'<div style="background-color: var(--card-bg); padding: 8px 16px; border-radius: 4px; border: 1px solid var(--border); font-size: 0.9em; color: var(--text-muted); margin-bottom: 12px;">'
                f'Returned: <strong>{len(res_df):,} rows</strong> | Execution Time: <strong>{exec_time} ms</strong>'
                f'</div>',
                unsafe_allow_html=True
            )

            # Render summary text
            if summary_text:
                st.markdown(
                    f'<div style="background-color: #0F172A; border-left: 4px solid var(--accent); padding: 12px 16px; border-radius: 4px; margin-bottom: 20px; font-size: 0.95em; color: #E2E8F0;">'
                    f'<h4 style="margin: 0 0 8px 0; font-size: 1.1em; color: #F8FAFC;">Query Results Summary</h4>'
                    f'{summary_text}'
                    f'</div>',
                    unsafe_allow_html=True
                )

            # Render recommended Plotly chart
            if chart_rec and chart_rec.get("chart") not in [None, "none"]:
                chart_type = chart_rec["chart"]
                title = chart_rec.get("title", "Result Analysis")
                x_col = chart_rec.get("x")
                y_col = chart_rec.get("y")

                # Verify column name mappings exist in df
                if x_col in res_df.columns and (chart_type == "histogram" or y_col in res_df.columns):
                    st.markdown("---")
                    st.subheader("Recommended Visualization")
                    
                    fig = None
                    plotly_template = theme.get_plotly_template()
                    
                    try:
                        if chart_type == "bar":
                            fig = px.bar(
                                res_df, x=x_col, y=y_col, title=title,
                                color_discrete_sequence=[theme.ACCENT]
                            )
                        elif chart_type == "line":
                            fig = px.line(
                                res_df, x=x_col, y=y_col, title=title,
                                color_discrete_sequence=[theme.ACCENT]
                            )
                        elif chart_type == "pie":
                            fig = px.pie(
                                res_df, names=x_col, values=y_col, title=title,
                                color_discrete_sequence=theme.CHART_COLORS
                            )
                        elif chart_type == "histogram":
                            fig = px.histogram(
                                res_df, x=x_col, title=title,
                                color_discrete_sequence=[theme.ACCENT]
                            )
                        
                        if fig:
                            fig.update_layout(**plotly_template, height=360)
                            st.plotly_chart(fig, use_container_width=True, key="custom_analytics_chart")
                    except Exception as e:
                        st.info(f"Could not render recommended chart: {e}")
                    
                    st.markdown("---")

            # Download Export Block
            st.subheader("Data Export")
            
            # Pre-compile files for download
            csv_bytes = export_to_csv(res_df)
            
            # Excel export
            excel_bytes = export_to_excel(
                st.session_state["nl_prompt"] or st.session_state["sql_query"],
                st.session_state["sql_query"],
                summary_text,
                res_df
            )
            
            # PDF export
            pdf_bytes = export_to_pdf(
                st.session_state["nl_prompt"] or st.session_state["sql_query"],
                st.session_state["sql_query"],
                summary_text,
                chart_rec,
                res_df
            )

            col_csv, col_xlsx, col_pdf, _ = st.columns([0.18, 0.18, 0.18, 0.46])
            
            with col_csv:
                st.download_button(
                    "📄 Download CSV",
                    csv_bytes,
                    file_name="custom_analytics_report.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col_xlsx:
                st.download_button(
                    "📊 Download Excel",
                    excel_bytes,
                    file_name="custom_analytics_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            with col_pdf:
                st.download_button(
                    "📕 Download PDF",
                    pdf_bytes,
                    file_name="custom_analytics_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            theme.vertical_spacer(16)
            st.subheader("Results Table")
            st.dataframe(res_df, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
