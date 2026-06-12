"""
Design system tokens and theme configuration.
Inspired by Linear, Notion, and Stripe Dashboard aesthetics.
All colors, spacing, typography, and Plotly templates are defined here.
"""


# ──────────────────────────────────────────────────────
# Color Palette
# ──────────────────────────────────────────────────────

BG = "#0F1117"
CARD_BG = "#161B22"
BORDER = "#262C36"
ACCENT = "#5B8CFF"
TEXT = "#F3F4F6"
MUTED = "#9CA3AF"
HOVER = "#1C2333"

STATUS_COLORS: dict[str, str] = {
    "Open": "#5B8CFF",
    "Assigned": "#7C6BFF",
    "In Progress": "#FFAB00",
    "Resolved": "#36B37E",
    "Closed": "#9CA3AF",
    "Cancelled": "#FF6B6B",
}

PRIORITY_COLORS: dict[str, str] = {
    "P1": "#FF6B6B",
    "P2": "#FFAB00",
    "P3": "#5B8CFF",
    "P4": "#36B37E",
}

CHART_COLORS: list[str] = [
    "#5B8CFF",
    "#7C6BFF",
    "#36B37E",
    "#FF6B6B",
    "#FFAB00",
    "#00B8D9",
    "#FF8B4A",
    "#B4B4B4",
]


# ──────────────────────────────────────────────────────
# Typography
# ──────────────────────────────────────────────────────

FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"


# ──────────────────────────────────────────────────────
# Layout Tokens
# ──────────────────────────────────────────────────────

BORDER_RADIUS = "12px"
BORDER_RADIUS_LG = "16px"
CARD_PADDING = "24px"


# ──────────────────────────────────────────────────────
# Plotly Template
# ──────────────────────────────────────────────────────

def get_plotly_template() -> dict:
    """Return a Plotly layout dict for consistent chart styling across all pages."""
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family=FONT_FAMILY,
            color=TEXT,
            size=13,
        ),
        xaxis=dict(
            gridcolor=BORDER,
            linecolor=BORDER,
            zerolinecolor=BORDER,
            tickfont=dict(color=MUTED, size=11),
            title_font=dict(color=MUTED, size=12),
        ),
        yaxis=dict(
            gridcolor=BORDER,
            linecolor=BORDER,
            zerolinecolor=BORDER,
            tickfont=dict(color=MUTED, size=11),
            title_font=dict(color=MUTED, size=12),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=MUTED, size=11),
        ),
        margin=dict(l=48, r=24, t=40, b=48),
        colorway=CHART_COLORS,
        hoverlabel=dict(
            bgcolor=CARD_BG,
            font_size=12,
            font_family=FONT_FAMILY,
            bordercolor=BORDER,
        ),
    )


# ──────────────────────────────────────────────────────
# Global CSS
# ──────────────────────────────────────────────────────

def get_global_css() -> str:
    """Return the global CSS string for Streamlit injection via st.markdown."""
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* ── Global ── */
        html, body, .stApp {{
            font-family: {FONT_FAMILY};
            background-color: {BG};
            color: {TEXT};
        }}

        /* ── Hide Streamlit chrome ── */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header[data-testid="stHeader"] {{
            background-color: {BG};
            border-bottom: 1px solid {BORDER};
        }}

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {{
            background-color: {CARD_BG};
            border-right: 1px solid {BORDER};
            padding-top: 1.5rem;
            min-width: 240px;
            max-width: 280px;
        }}

        section[data-testid="stSidebar"] .stRadio > label {{
            display: none;
        }}

        section[data-testid="stSidebar"] .stRadio > div {{
            gap: 2px;
        }}

        section[data-testid="stSidebar"] .stRadio > div > label {{
            background-color: transparent;
            border-radius: 8px;
            padding: 10px 16px;
            margin: 0;
            color: {MUTED};
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s ease;
            border: none;
        }}

        section[data-testid="stSidebar"] .stRadio > div > label:hover {{
            background-color: {HOVER};
            color: {TEXT};
        }}

        section[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"] {{
            background-color: rgba(91, 140, 255, 0.1);
            color: {ACCENT};
        }}

        /* ── Buttons ── */
        .stButton > button {{
            background-color: {ACCENT};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 20px;
            font-weight: 500;
            font-size: 14px;
            transition: all 0.15s ease;
        }}

        .stButton > button:hover {{
            background-color: #4A7AEE;
            border: none;
            color: white;
        }}

        .stButton > button:active {{
            background-color: #3D6BD9;
            border: none;
            color: white;
        }}

        /* ── Inputs ── */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stNumberInput > div > div > input {{
            background-color: {CARD_BG} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 8px !important;
            color: {TEXT} !important;
            font-size: 14px !important;
        }}

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {{
            border-color: {ACCENT} !important;
            box-shadow: 0 0 0 1px {ACCENT} !important;
        }}

        .stSelectbox > div > div,
        .stMultiSelect > div > div {{
            background-color: {CARD_BG} !important;
            border-color: {BORDER} !important;
            border-radius: 8px !important;
        }}

        /* ── Labels ── */
        .stTextInput > label,
        .stTextArea > label,
        .stSelectbox > label,
        .stMultiSelect > label,
        .stNumberInput > label,
        .stDateInput > label {{
            color: {MUTED} !important;
            font-size: 13px !important;
            font-weight: 500 !important;
        }}

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0;
            border-bottom: 1px solid {BORDER};
        }}

        .stTabs [data-baseweb="tab"] {{
            color: {MUTED};
            font-weight: 500;
            padding: 12px 20px;
            border-bottom: 2px solid transparent;
        }}

        .stTabs [aria-selected="true"] {{
            color: {TEXT} !important;
            border-bottom-color: {ACCENT} !important;
        }}

        /* ── Dataframe ── */
        [data-testid="stDataFrame"] {{
            border: 1px solid {BORDER};
            border-radius: {BORDER_RADIUS};
            overflow: hidden;
        }}

        /* ── Divider ── */
        hr {{
            border-color: {BORDER} !important;
        }}

        /* ── Dialog ── */
        div[data-testid="stModal"] > div {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: {BORDER_RADIUS_LG};
        }}

        /* ── Plotly Chart Container ── */
        .stPlotlyChart {{
            border: 1px solid {BORDER};
            border-radius: {BORDER_RADIUS};
            padding: 8px;
            background-color: {CARD_BG};
        }}

        /* ── Metric ── */
        [data-testid="stMetric"] {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: {BORDER_RADIUS};
            padding: {CARD_PADDING};
        }}

        [data-testid="stMetricValue"] {{
            color: {TEXT};
            font-weight: 600;
        }}

        [data-testid="stMetricLabel"] {{
            color: {MUTED} !important;
            font-size: 13px !important;
        }}

        /* ── Scrollbar ── */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        ::-webkit-scrollbar-track {{
            background: {BG};
        }}
        ::-webkit-scrollbar-thumb {{
            background: {BORDER};
            border-radius: 3px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: {MUTED};
        }}

        /* ── Custom: Metric Card ── */
        .metric-card {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: {BORDER_RADIUS};
            padding: {CARD_PADDING};
        }}
        .metric-card .label {{
            color: {MUTED};
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 8px;
        }}
        .metric-card .value {{
            color: {TEXT};
            font-size: 28px;
            font-weight: 600;
            line-height: 1.2;
        }}
        .metric-card .subtitle {{
            color: {MUTED};
            font-size: 12px;
            margin-top: 4px;
        }}

        /* ── Custom: Section Titles ── */
        .section-title {{
            color: {TEXT};
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 16px;
            margin-top: 32px;
        }}

        /* ── Custom: Badges ── */
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            line-height: 1.6;
        }}
        .badge-p1 {{ background-color: rgba(255, 107, 107, 0.15); color: #FF6B6B; }}
        .badge-p2 {{ background-color: rgba(255, 171, 0, 0.15); color: #FFAB00; }}
        .badge-p3 {{ background-color: rgba(91, 140, 255, 0.15); color: #5B8CFF; }}
        .badge-p4 {{ background-color: rgba(54, 179, 126, 0.15); color: #36B37E; }}

        .status-open {{ background-color: rgba(91, 140, 255, 0.15); color: #5B8CFF; }}
        .status-assigned {{ background-color: rgba(124, 107, 255, 0.15); color: #7C6BFF; }}
        .status-inprogress {{ background-color: rgba(255, 171, 0, 0.15); color: #FFAB00; }}
        .status-resolved {{ background-color: rgba(54, 179, 126, 0.15); color: #36B37E; }}
        .status-closed {{ background-color: rgba(156, 163, 175, 0.15); color: #9CA3AF; }}
        .status-cancelled {{ background-color: rgba(255, 107, 107, 0.15); color: #FF6B6B; }}

        /* ── Custom: Incident Card ── */
        .incident-card {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: {BORDER_RADIUS};
            padding: 16px 20px;
            margin-bottom: 8px;
            transition: border-color 0.15s ease;
        }}
        .incident-card:hover {{
            border-color: {ACCENT};
        }}
        .incident-card .incident-id {{
            color: {MUTED};
            font-size: 12px;
            font-weight: 500;
            font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
        }}
        .incident-card .incident-desc {{
            color: {TEXT};
            font-size: 14px;
            font-weight: 500;
            margin-top: 4px;
        }}
        .incident-card .incident-meta {{
            color: {MUTED};
            font-size: 12px;
            margin-top: 8px;
            display: flex;
            gap: 12px;
        }}

        /* ── Custom: Date Group Header ── */
        .date-header {{
            color: {MUTED};
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 24px;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 1px solid {BORDER};
        }}

        /* ── Custom: Detail Panel ── */
        .detail-panel {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: {BORDER_RADIUS};
            padding: {CARD_PADDING};
        }}
        .detail-label {{
            color: {MUTED};
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 4px;
        }}
        .detail-value {{
            color: {TEXT};
            font-size: 14px;
            margin-bottom: 16px;
        }}

        /* ── Custom: Timeline Steps ── */
        .timeline-step {{
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 8px 0;
            position: relative;
        }}
        .timeline-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-top: 4px;
            flex-shrink: 0;
        }}
        .timeline-dot.completed {{
            background-color: {ACCENT};
        }}
        .timeline-dot.pending {{
            background-color: {BORDER};
        }}
        .timeline-dot.active {{
            background-color: {ACCENT};
            box-shadow: 0 0 0 3px rgba(91, 140, 255, 0.2);
        }}
        .timeline-step-label {{
            font-size: 13px;
            color: {TEXT};
        }}
        .timeline-step-label.pending {{
            color: {MUTED};
        }}
        .timeline-step-time {{
            font-size: 11px;
            color: {MUTED};
            margin-top: 2px;
        }}

        /* ── Custom: Prediction Card ── */
        .prediction-card {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: {BORDER_RADIUS};
            padding: {CARD_PADDING};
            text-align: center;
        }}
        .prediction-card .pred-label {{
            color: {MUTED};
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 12px;
        }}
        .prediction-card .pred-value {{
            color: {TEXT};
            font-size: 24px;
            font-weight: 600;
        }}
        .prediction-card .pred-confidence {{
            color: {MUTED};
            font-size: 12px;
            margin-top: 8px;
        }}

        /* ── Custom: Top Nav ── */
        .top-nav {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 0 16px 0;
            margin-bottom: 24px;
            border-bottom: 1px solid {BORDER};
        }}
        .top-nav .nav-title {{
            color: {TEXT};
            font-size: 20px;
            font-weight: 600;
        }}
        .top-nav .nav-date {{
            color: {MUTED};
            font-size: 13px;
            margin-top: 2px;
        }}
        .top-nav .nav-stats {{
            display: flex;
            gap: 24px;
        }}
        .top-nav .nav-stat {{
            color: {MUTED};
            font-size: 13px;
        }}
        .top-nav .nav-stat .stat-value {{
            color: {TEXT};
            font-weight: 600;
            margin-left: 4px;
        }}

        /* ── Custom: Empty State ── */
        .empty-state {{
            text-align: center;
            color: {MUTED};
            padding: 64px 0;
            font-size: 14px;
        }}

        /* ── Custom: Filter Bar ── */
        .filter-bar {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: {BORDER_RADIUS};
            padding: 16px 20px;
            margin-bottom: 24px;
        }}
    </style>
    """
