"""
Design system tokens and theme configuration.
Inspired by Linear, Notion, and Stripe Dashboard aesthetics.
All colors, spacing, typography, and Plotly templates are defined here.
"""

import streamlit as st


# ──────────────────────────────────────────────────────
# Color Palette
# ──────────────────────────────────────────────────────

BG = "#080A10"
CARD_BG = "#0F121E"
BORDER = "#1B223C"
ACCENT = "#4B6BF5"
TEXT = "#F3F4F6"
MUTED = "#94A3B8"
HOVER = "#1E293B"

STATUS_COLORS: dict[str, str] = {
    "Open": "#4B6BF5",
    "Assigned": "#8B5CF6",
    "In Progress": "#F59E0B",
    "Resolved": "#10B981",
    "Closed": "#64748B",
    "Cancelled": "#EF4444",
}

PRIORITY_COLORS: dict[str, str] = {
    "P1": "#EF4444",
    "P2": "#F59E0B",
    "P3": "#3B82F6",
    "P4": "#10B981",
}

CHART_COLORS: list[str] = [
    "#4B6BF5",
    "#8B5CF6",
    "#10B981",
    "#EF4444",
    "#F59E0B",
    "#06B6D4",
    "#F97316",
    "#64748B",
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
            background-color: #3C59D4 !important;
            border: none !important;
            color: white !important;
            box-shadow: 0 4px 12px rgba(75, 107, 245, 0.2);
        }}

        .stButton > button:active {{
            background-color: #2F4AB2 !important;
            border: none !important;
            color: white !important;
        }}
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
        .badge-p1 {{ background-color: rgba(239, 68, 68, 0.15); color: #EF4444; }}
        .badge-p2 {{ background-color: rgba(245, 158, 11, 0.15); color: #F59E0B; }}
        .badge-p3 {{ background-color: rgba(59, 130, 246, 0.15); color: #3B82F6; }}
        .badge-p4 {{ background-color: rgba(16, 185, 129, 0.15); color: #10B981; }}

        .status-open {{ background-color: rgba(75, 107, 245, 0.15); color: #4B6BF5; }}
        .status-assigned {{ background-color: rgba(139, 92, 246, 0.15); color: #8B5CF6; }}
        .status-inprogress {{ background-color: rgba(245, 158, 11, 0.15); color: #F59E0B; }}
        .status-resolved {{ background-color: rgba(16, 185, 129, 0.15); color: #10B981; }}
        .status-closed {{ background-color: rgba(100, 116, 139, 0.15); color: #64748B; }}
        .status-cancelled {{ background-color: rgba(239, 68, 68, 0.15); color: #EF4444; }}

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

        /* ── Sidebar Branding ── */
        .sidebar-brand {{
            padding: 0 16px 24px 16px;
        }}
        .sidebar-brand .brand-title {{
            font-size: 18px;
            font-weight: 700;
            color: {TEXT};
            letter-spacing: -0.02em;
        }}
        .sidebar-brand .brand-subtitle {{
            font-size: 12px;
            color: {MUTED};
            margin-top: 4px;
        }}

        /* ── Custom: Page Header ── */
        .page-header-container {{
            padding: 0 0 16px 0;
            margin-bottom: 24px;
            border-bottom: 1px solid {BORDER};
        }}
        .page-header-title {{
            color: {TEXT};
            font-size: 20px;
            font-weight: 600;
        }}
        .page-header-subtitle {{
            color: {MUTED};
            font-size: 14px;
            margin-top: 4px;
        }}

        /* ── Spacers ── */
        .spacer-8 {{ height: 8px; }}
        .spacer-12 {{ height: 12px; }}
        .spacer-16 {{ height: 16px; }}
        .spacer-20 {{ height: 20px; }}
        .spacer-24 {{ height: 24px; }}
        .spacer-32 {{ height: 32px; }}
        .spacer-48 {{ height: 48px; }}

        /* ── Incident Detail Timeline & Headers ── */
        .detail-header-id {{
            font-size: 16px;
            font-weight: 600;
            color: {TEXT};
            margin-bottom: 12px;
            font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
        }}
        .detail-section-title {{
            color: {TEXT};
            font-size: 14px;
            font-weight: 600;
            margin-top: 24px;
            margin-bottom: 12px;
        }}
        
        /* ── Incident Card Timeline Info ── */
        .incident-card-info {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: {BORDER_RADIUS};
            padding: 16px;
            transition: border-color 0.15s ease;
        }}
        .incident-card-info:hover {{
            border-color: {ACCENT};
        }}
    </style>
    """


def render_page_header(title: str, subtitle: str) -> None:
    """Render a consistent page title block at the top of a page."""
    st.markdown(
        f"""
        <div class="page-header-container">
            <div class="page-header-title">{title}</div>
            <div class="page-header-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def vertical_spacer(height_px: int) -> None:
    """Render a clean vertical spacer of the specified height in pixels."""
    supported_heights = {8, 12, 16, 20, 24, 32, 48}
    if height_px in supported_heights:
        st.markdown(
            f'<div class="spacer-{height_px}"></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="height:{height_px}px;"></div>',
            unsafe_allow_html=True,
        )
