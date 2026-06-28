"""
Analytics page -- Advanced operational analytics with interactive filters.

Sections: Root Cause, Resolution Time, Application, Priority, and Team.
Charts: Treemap, Box Plot, Heatmap, Stacked Bar, Trend lines.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from backend.analytics.metrics import get_resolution_time_trend
from backend.analytics.rootcause import (
    get_resolution_by_priority,
    get_root_cause_by_team,
    get_root_cause_distribution,
)
from backend.analytics.trends import (
    get_priority_distribution,
    get_priority_trend,
)
from backend.analytics.workload import (
    get_team_priority_heatmap,
    get_team_workload,
    get_top_applications,
)
from backend.utils.data_loader import get_all_incidents
from frontend.components.filters import apply_filters, render_filters
import frontend.styles.theme as theme


def render_analytics() -> None:
    """Render the Analytics page with filterable operational charts."""
    # Resolve variables dynamically on every rerun
    ACCENT = theme.ACCENT
    CARD_BG = theme.CARD_BG
    CHART_COLORS = theme.CHART_COLORS
    PRIORITY_COLORS = theme.PRIORITY_COLORS
    TEXT = theme.TEXT

    # ── Page Header ──
    theme.render_page_header(
        "Analytics",
        "Advanced operational analytics and insights",
    )

    # ── Data + Filters ──
    df = get_all_incidents()
    filters = render_filters(df)
    df = apply_filters(df, filters)
    template = get_plotly_template()

    if df.empty:
        st.info("No data matches the selected filters.")
        return

    # ── SLA calculations ──
    def calculate_compliance(sub_df: pd.DataFrame) -> float:
        completed = sub_df[sub_df["status"].isin(["Resolved", "Closed"])]
        if completed.empty:
            return 100.0
        met_count = (completed["sla_breached"] == False).sum()
        return round(float(met_count / len(completed) * 100), 1)

    overall_compliance = calculate_compliance(df)
    p1_compliance = calculate_compliance(df[df["priority"] == "P1"])
    p2_compliance = calculate_compliance(df[df["priority"] == "P2"])
    p3_compliance = calculate_compliance(df[df["priority"] == "P3"])
    p4_compliance = calculate_compliance(df[df["priority"] == "P4"])
    total_breaches = int((df["sla_breached"] == True).sum())

    # Calculate SLA compliance by team to identify Best and Worst performing teams
    df_with_team = df.copy()
    df_with_team["teams"] = df_with_team["teams"].fillna("").astype(str)
    df_with_team["primary_team"] = df_with_team["teams"].apply(
        lambda x: x.split(",")[0].strip() if x.strip() else "Unknown"
    )
    
    teams_list = ["Network", "Database", "Middleware", "Unix/Linux", "Wintel", "Batch"]
    team_compliance = {}
    for t in teams_list:
        team_df = df_with_team[df_with_team["primary_team"] == t]
        completed_team = team_df[team_df["status"].isin(["Resolved", "Closed"])]
        if not completed_team.empty:
            team_compliance[t] = calculate_compliance(team_df)
        else:
            team_compliance[t] = 100.0

    best_team = max(team_compliance, key=team_compliance.get) if team_compliance else "N/A"
    worst_team = min(team_compliance, key=team_compliance.get) if team_compliance else "N/A"
    best_val = team_compliance.get(best_team, 100.0)
    worst_val = team_compliance.get(worst_team, 100.0)

    # ── SLA KPI Cards ──
    c_sla1, c_sla2, c_sla3 = st.columns(3)
    with c_sla1:
        st.markdown(
            f"""
            <div class="metric-card" style="min-height: 120px;">
                <div class="label">SLA Compliance</div>
                <div class="value">{overall_compliance}%</div>
                <div class="subtitle">P1: {p1_compliance}% | P2: {p2_compliance}% | P3: {p3_compliance}% | P4: {p4_compliance}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_sla2:
        st.markdown(
            f"""
            <div class="metric-card" style="min-height: 120px; display: flex; flex-direction: column; justify-content: center;">
                <div class="label">SLA Breaches</div>
                <div class="value" style="color: #EF4444;">{total_breaches:,}</div>
                <div class="subtitle">Total breached incidents across active & resolved tickets</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c_sla3:
        st.markdown(
            f"""
            <div class="metric-card" style="min-height: 120px;">
                <div class="label">Operational Performance</div>
                <div class="value" style="font-size: 16px; font-weight: 600; margin-top: 8px;">
                    Best: <span style="color: #10B981;">{best_team} ({best_val}%)</span>
                </div>
                <div class="value" style="font-size: 16px; font-weight: 600; margin-top: 4px;">
                    Worst: <span style="color: #EF4444;">{worst_team} ({worst_val}%)</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    vertical_spacer(24)

    # ── Organizing Charts into Tabs (No Emojis) ──
    tab_trends, tab_workload, tab_performance = st.tabs([
        "Volume & Trends",
        "Team Workload",
        "Performance",
    ])

    # ──────────────────────────────────────────────
    # Tab 1: Volume & Trends
    # ──────────────────────────────────────────────
    with tab_trends:
        vertical_spacer(16)

        # Top Applications (Full Width)
        apps = get_top_applications(df, n=15)
        if not apps.empty:
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=apps["application"],
                        y=apps["count"],
                        marker=dict(color=CHART_COLORS[1]),
                    )
                ]
            )
            fig.update_layout(
                **template,
                title=dict(
                    text="Top Applications by Incident Volume",
                    font=dict(size=14, color=TEXT),
                ),
                xaxis_title="",
                yaxis_title="Count",
                showlegend=False,
                height=340,
            )
            st.plotly_chart(
                fig, use_container_width=True, key="analytics_apps"
            )

        vertical_spacer(32)

        # Priority Trend & Priority Distribution side-by-side
        col1, col2 = st.columns(2)

        with col1:
            ptrend = get_priority_trend(df)
            if not ptrend.empty:
                fig = px.bar(
                    ptrend,
                    x="month",
                    y="count",
                    color="priority",
                    color_discrete_map=PRIORITY_COLORS,
                    category_orders={"priority": ["P1", "P2", "P3", "P4"]},
                )
                fig.update_layout(
                    **template,
                    title=dict(
                        text="Priority Trend (Stacked)",
                        font=dict(size=14, color=TEXT),
                    ),
                    barmode="stack",
                    xaxis_title="",
                    yaxis_title="Count",
                    height=400,
                )
                st.plotly_chart(
                    fig, use_container_width=True, key="analytics_pri_trend"
                )

        with col2:
            pri_dist = get_priority_distribution(df)
            if not pri_dist.empty:
                colors = [
                    PRIORITY_COLORS.get(p, ACCENT) for p in pri_dist["priority"]
                ]
                fig = go.Figure(
                    data=[
                        go.Pie(
                            labels=pri_dist["priority"],
                            values=pri_dist["count"],
                            hole=0.55,
                            marker=dict(colors=colors),
                            textfont=dict(color=TEXT),
                        )
                    ]
                )
                fig.update_layout(
                    **template,
                    title=dict(
                        text="Priority Distribution",
                        font=dict(size=14, color=TEXT),
                    ),
                    height=400,
                )
                st.plotly_chart(
                    fig, use_container_width=True, key="analytics_pri_donut"
                )

    # ──────────────────────────────────────────────
    # Tab 2: Team Workload & Root Causes
    # ──────────────────────────────────────────────
    with tab_workload:
        vertical_spacer(16)

        col1, col2 = st.columns(2)

        with col1:
            wl = get_team_workload(df)
            if not wl.empty:
                fig = go.Figure(
                    data=[
                        go.Bar(
                            x=wl["count"],
                            y=wl["team"],
                            orientation="h",
                            marker=dict(color=ACCENT),
                        )
                    ]
                )
                fig.update_layout(
                    **template,
                    title=dict(
                        text="Team Workload",
                        font=dict(size=14, color=TEXT),
                    ),
                    xaxis_title="Incident Count",
                    showlegend=False,
                    height=400,
                )
                st.plotly_chart(
                    fig, use_container_width=True, key="analytics_wl"
                )

        with col2:
            heatmap = get_team_priority_heatmap(df)
            if not heatmap.empty:
                fig = go.Figure(
                    data=go.Heatmap(
                        z=heatmap.values,
                        x=heatmap.columns.tolist(),
                        y=heatmap.index.tolist(),
                        colorscale=[[0, CARD_BG], [1, ACCENT]],
                        texttemplate="%{z:.0f}",
                        textfont=dict(color=TEXT, size=12),
                        showscale=False,
                    )
                )
                fig.update_layout(
                    **template,
                    title=dict(
                        text="Team vs Priority Heatmap",
                        font=dict(size=14, color=TEXT),
                    ),
                    height=400,
                )
                st.plotly_chart(
                    fig, use_container_width=True, key="analytics_heatmap"
                )

        vertical_spacer(32)

        # Root Causes by Team (Full Width)
        rc_team = get_root_cause_by_team(df)
        if not rc_team.empty:
            fig = px.treemap(
                rc_team,
                path=["team", "root_cause"],
                values="count",
                color_discrete_sequence=CHART_COLORS,
            )
            fig.update_layout(
                **template,
                title=dict(
                    text="Root Causes by Team",
                    font=dict(size=14, color=TEXT),
                ),
                height=450,
            )
            fig.update_traces(
                textfont=dict(color=TEXT),
                marker=dict(cornerradius=4),
            )
            st.plotly_chart(
                fig, use_container_width=True, key="analytics_rc_tree"
            )

    # ──────────────────────────────────────────────
    # Tab 3: Performance & Root Causes
    # ──────────────────────────────────────────────
    with tab_performance:
        vertical_spacer(16)

        col1, col2 = st.columns(2)

        with col1:
            team_compliance_data = []
            for t in teams_list:
                team_compliance_data.append({
                    "team": t,
                    "compliance": team_compliance.get(t, 100.0)
                })
            team_compliance_df = pd.DataFrame(team_compliance_data)
            
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=team_compliance_df["team"],
                        y=team_compliance_df["compliance"],
                        marker=dict(color=ACCENT),
                        text=[f"{val}%" for val in team_compliance_df["compliance"]],
                        textposition="auto",
                    )
                ]
            )
            fig.update_layout(
                **template,
                title=dict(
                    text="SLA Compliance by Team",
                    font=dict(size=14, color=TEXT),
                ),
                xaxis_title="",
                yaxis_title="Compliance Percentage",
                height=400,
            )
            fig.update_yaxes(range=[0, 110])
            st.plotly_chart(
                fig, use_container_width=True, key="analytics_sla_by_team"
            )

        with col2:
            rc_dist = get_root_cause_distribution(df)
            if not rc_dist.empty:
                fig = go.Figure(
                    data=[
                        go.Bar(
                            x=rc_dist["count"],
                            y=rc_dist["root_cause"],
                            orientation="h",
                            marker=dict(color=CHART_COLORS[0]),
                        )
                    ]
                )
                fig.update_layout(
                    **template,
                    title=dict(
                        text="Root Cause Distribution",
                        font=dict(size=14, color=TEXT),
                    ),
                    height=400,
                )
                fig.update_yaxes(autorange="reversed")
                st.plotly_chart(
                    fig, use_container_width=True, key="analytics_rc_bar"
                )
