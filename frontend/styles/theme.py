"""
Design system tokens and theme configuration.
Inspired by Linear, Notion, and Stripe Dashboard aesthetics.
All colors, spacing, typography, and Plotly templates are defined here.
"""

import streamlit as st


# ──────────────────────────────────────────────────────
# Color Palette
# ──────────────────────────────────────────────────────

BG = "#F8F9FA"
CARD_BG = "#FFFFFF"
BORDER = "#E2E8F0"
ACCENT = "#2563EB"
TEXT = "#0F172A"
MUTED = "#64748B"
HOVER = "#F1F5F9"

STATUS_COLORS: dict[str, str] = {
    "Open": "#2563EB",
    "Assigned": "#7C3AED",
    "In Progress": "#D97706",
    "Resolved": "#059669",
    "Closed": "#475569",
    "Cancelled": "#DC2626",
}

PRIORITY_COLORS: dict[str, str] = {
    "P1": "#DC2626",
    "P2": "#D97706",
    "P3": "#2563EB",
    "P4": "#059669",
}

CHART_COLORS: list[str] = [
    "#2563EB",
    "#7C3AED",
    "#059669",
    "#DC2626",
    "#D97706",
    "#0891B2",
    "#EA580C",
    "#475569",
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

def update_theme_variables() -> None:
    """Read theme state from st.session_state and dynamically update palette variables."""
    global BG, CARD_BG, BORDER, ACCENT, TEXT, MUTED, HOVER, PRIORITY_COLORS, STATUS_COLORS, CHART_COLORS
    theme_name = st.session_state.get("theme", "light")
    if theme_name == "dark":
        BG = "#080A10"
        CARD_BG = "#0F121E"
        BORDER = "#1B223C"
        ACCENT = "#2563EB"
        TEXT = "#F3F4F6"
        MUTED = "#94A3B8"
        HOVER = "#1E293B"

        STATUS_COLORS["Open"] = "#2563EB"
        STATUS_COLORS["Assigned"] = "#7C3AED"
        STATUS_COLORS["In Progress"] = "#D97706"
        STATUS_COLORS["Resolved"] = "#059669"
        STATUS_COLORS["Closed"] = "#94A3B8"
        STATUS_COLORS["Cancelled"] = "#DC2626"

        PRIORITY_COLORS["P1"] = "#DC2626"
        PRIORITY_COLORS["P2"] = "#D97706"
        PRIORITY_COLORS["P3"] = "#2563EB"
        PRIORITY_COLORS["P4"] = "#059669"
    else:
        BG = "#F8F9FA"
        CARD_BG = "#FFFFFF"
        BORDER = "#E2E8F0"
        ACCENT = "#2563EB"
        TEXT = "#0F172A"
        MUTED = "#64748B"
        HOVER = "#F1F5F9"

        STATUS_COLORS["Open"] = "#2563EB"
        STATUS_COLORS["Assigned"] = "#7C3AED"
        STATUS_COLORS["In Progress"] = "#D97706"
        STATUS_COLORS["Resolved"] = "#059669"
        STATUS_COLORS["Closed"] = "#475569"
        STATUS_COLORS["Cancelled"] = "#DC2626"

        PRIORITY_COLORS["P1"] = "#DC2626"
        PRIORITY_COLORS["P2"] = "#D97706"
        PRIORITY_COLORS["P3"] = "#2563EB"
        PRIORITY_COLORS["P4"] = "#059669"


def get_plotly_template() -> dict:
    """Return a Plotly layout dict for consistent chart styling across all pages."""
    update_theme_variables()
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
    update_theme_variables()
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* CSS Custom Properties for Portal Dropdowns */
        :root {{
            --bg: {BG};
            --card-bg: {CARD_BG};
            --border: {BORDER};
            --accent: {ACCENT};
            --text: {TEXT};
            --muted: {MUTED};
            --hover: {HOVER};
        }}

        /* Dropdown Overlay Portals */
        div[data-baseweb="popover"],
        div[data-baseweb="menu"],
        div[role="listbox"],
        [data-testid="stVirtualDropdown"] {{
            background-color: {CARD_BG} !important;
            border: 1px solid {BORDER} !important;
        }}
        
        /* Dropdown Option Items */
        [role="option"],
        [role="option"] p,
        [role="option"] span {{
            background-color: {CARD_BG} !important;
            color: {TEXT} !important;
        }}

        /* Simple and minimal hover state */
        [role="option"]:hover,
        [role="option"]:hover p,
        [role="option"]:hover span,
        [role="option"][aria-selected="true"],
        [role="option"][aria-selected="true"] p,
        [role="option"][aria-selected="true"] span {{
            background-color: {HOVER} !important;
            color: {TEXT} !important;
            cursor: pointer !important;
        }}

        /* Calendar overlays */
        div[role="dialog"] {{
            background-color: {CARD_BG} !important;
            color: {TEXT} !important;
        }}
        /* Selected Multiselect Tags */
        [data-baseweb="tag"] {{
            background-color: rgba(37, 99, 235, 0.1) !important;
            color: {ACCENT} !important;
            border: 1px solid rgba(37, 99, 235, 0.2) !important;
        }}
        [data-baseweb="tag"] span {{
            color: {ACCENT} !important;
        }}

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

        /* Hide the radio button circular selectors */
        section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {{
            display: none !important;
        }}

        section[data-testid="stSidebar"] div[role="radiogroup"] label {{
            background-color: transparent !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
            margin-bottom: 4px !important;
            cursor: pointer !important;
            border: none !important;
            display: flex !important;
            align-items: center !important;
            transition: all 0.2s ease !important;
            box-shadow: none !important;
            width: 100% !important;
        }}

        section[data-testid="stSidebar"] div[role="radiogroup"] label [data-testid="stMarkdownContainer"] p {{
            color: {MUTED} !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            margin: 0 !important;
            transition: all 0.2s ease !important;
        }}

        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {{
            background-color: {HOVER} !important;
        }}

        section[data-testid="stSidebar"] div[role="radiogroup"] label:hover [data-testid="stMarkdownContainer"] p {{
            color: {TEXT} !important;
        }}

        section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {{
            background-color: rgba(37, 99, 235, 0.08) !important;
        }}

        section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] [data-testid="stMarkdownContainer"] p {{
            color: {ACCENT} !important;
            font-weight: 600 !important;
        }}

        /* ── Buttons ── */
        .stButton > button,
        .stDownloadButton > button {{
            border-radius: 8px !important;
            padding: 8px 20px !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}

        /* Secondary Button (Default) */
        .stButton > button,
        .stButton > button[kind="secondary"],
        .stButton > button:not([kind="primary"]),
        .stDownloadButton > button,
        .stDownloadButton > button[kind="secondary"],
        .stDownloadButton > button:not([kind="primary"]) {{
            background-color: {CARD_BG} !important;
            color: {TEXT} !important;
            border: 1px solid {BORDER} !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
        }}

        .stButton > button:hover,
        .stButton > button[kind="secondary"]:hover,
        .stButton > button:not([kind="primary"]):hover,
        .stDownloadButton > button:hover,
        .stDownloadButton > button[kind="secondary"]:hover,
        .stDownloadButton > button:not([kind="primary"]):hover {{
            background-color: {HOVER} !important;
            border-color: {MUTED} !important;
            color: {TEXT} !important;
        }}

        .stButton > button:active,
        .stButton > button[kind="secondary"]:active,
        .stButton > button:not([kind="primary"]):active,
        .stDownloadButton > button:active,
        .stDownloadButton > button[kind="secondary"]:active,
        .stDownloadButton > button:not([kind="primary"]):active {{
            background-color: {BORDER} !important;
        }}

        /* Primary Button */
        .stButton > button[kind="primary"],
        .stDownloadButton > button[kind="primary"] {{
            background-color: {ACCENT} !important;
            color: white !important;
            border: 1px solid {ACCENT} !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
        }}

        .stButton > button[kind="primary"]:hover,
        .stDownloadButton > button[kind="primary"]:hover {{
            background-color: #1D4ED8 !important;
            border-color: #1D4ED8 !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15) !important;
            color: white !important;
        }}

        .stButton > button[kind="primary"]:active,
        .stDownloadButton > button[kind="primary"]:active {{
            background-color: #1E40AF !important;
            border-color: #1E40AF !important;
            color: white !important;
        }}

        /* ── Inputs ── */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stNumberInput > div > div > input,
        .stDateInput > div > div > input {{
            background-color: {CARD_BG} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 8px !important;
            color: {TEXT} !important;
            font-size: 14px !important;
            transition: all 0.2s ease;
        }}

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stDateInput > div > div > input:focus {{
            border-color: {ACCENT} !important;
            box-shadow: 0 0 0 1px {ACCENT} !important;
        }}

        .stSelectbox > div > div,
        .stMultiSelect > div > div,
        .stSelectbox [data-baseweb="select"] > div,
        .stMultiSelect [data-baseweb="select"] > div,
        div[data-testid="stDateInput"] > div > div,
        .stDateInput [data-baseweb="input"] {{
            background-color: {CARD_BG} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 8px !important;
            color: {TEXT} !important;
        }}

        /* Text and placeholder selectors inside dropdown and multiselect inputs */
        .stSelectbox [data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
        .stMultiSelect [data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
        .stSelectbox [data-baseweb="select"] div,
        .stMultiSelect [data-baseweb="select"] div,
        .stSelectbox span,
        .stMultiSelect span,
        .stDateInput input {{
            color: {TEXT} !important;
        }}
        
        /* Dropdown placeholder text contrast */
        div[data-baseweb="select"] div[class*="-placeholder"],
        div[aria-hidden="true"],
        [placeholder],
        ::placeholder {{
            color: {MUTED} !important;
            opacity: 0.8 !important;
        }}

        /* Dynamic Theme Toggle Button Styling */
        div.st-key-theme_toggle_btn > button {{
            width: 38px !important;
            height: 38px !important;
            min-width: 38px !important;
            padding: 0 !important;
            border-radius: 50% !important;
            font-size: 16px !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            background-color: {CARD_BG} !important;
            border: 1px solid {BORDER} !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05) !important;
            transition: all 0.2s ease !important;
        }}
        div.st-key-theme_toggle_btn > button:hover {{
            background-color: {HOVER} !important;
            border-color: {MUTED} !important;
            transform: scale(1.05);
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
            transition: all 0.2s ease;
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
            background-color: {CARD_BG};
        }}

        /* ── Divider ── */
        hr {{
            border-color: {BORDER} !important;
        }}

        /* ── Dialog ── */
        div[data-testid="stModal"] > div {{
            background-color: {CARD_BG} !important;
            border: 1px solid {BORDER} !important;
            border-radius: {BORDER_RADIUS_LG} !important;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
        }}
        div[data-testid="stModal"] h1,
        div[data-testid="stModal"] h2,
        div[data-testid="stModal"] h3,
        div[data-testid="stModal"] h4,
        div[data-testid="stModal"] h5,
        div[data-testid="stModal"] h6,
        div[data-testid="stModal"] p,
        div[data-testid="stModal"] span,
        div[data-testid="stModal"] label,
        div[data-testid="stModal"] [data-testid="stMarkdownContainer"] p {{
            color: {TEXT} !important;
        }}

        /* ── Plotly Chart Container ── */
        .stPlotlyChart {{
            border: 1px solid {BORDER};
            border-radius: {BORDER_RADIUS};
            padding: 8px;
            background-color: {CARD_BG};
            box-shadow: 0 1px 3px rgba(0,0,0,0.02), 0 1px 2px rgba(0,0,0,0.01);
        }}

        /* ── Metric ── */
        [data-testid="stMetric"] {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: {BORDER_RADIUS};
            padding: {CARD_PADDING};
            box-shadow: 0 1px 3px rgba(0,0,0,0.02), 0 1px 2px rgba(0,0,0,0.01);
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
            box-shadow: 0 1px 3px rgba(0,0,0,0.02), 0 1px 2px rgba(0,0,0,0.01);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .metric-card:hover {{
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
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
        .badge-p1 {{ background-color: rgba(220, 38, 38, 0.1); color: #DC2626; }}
        .badge-p2 {{ background-color: rgba(217, 119, 6, 0.1); color: #D97706; }}
        .badge-p3 {{ background-color: rgba(37, 99, 235, 0.1); color: #2563EB; }}
        .badge-p4 {{ background-color: rgba(5, 150, 105, 0.1); color: #059669; }}

        .status-open {{ background-color: rgba(37, 99, 235, 0.1); color: #2563EB; }}
        .status-assigned {{ background-color: rgba(124, 58, 237, 0.1); color: #7C3AED; }}
        .status-inprogress {{ background-color: rgba(217, 119, 6, 0.1); color: #D97706; }}
        .status-resolved {{ background-color: rgba(5, 150, 105, 0.1); color: #059669; }}
        .status-closed {{ background-color: rgba(71, 85, 105, 0.1); color: #475569; }}
        .status-cancelled {{ background-color: rgba(220, 38, 38, 0.1); color: #DC2626; }}

        /* ── Custom: Incident Card ── */
        .incident-card {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: {BORDER_RADIUS};
            padding: 16px 20px;
            margin-bottom: 8px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02);
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .incident-card:hover {{
            border-color: {ACCENT};
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            cursor: pointer;
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
            flex-wrap: wrap;
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
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
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
            align-items: center;
            gap: 12px;
            padding: 8px 0;
            position: relative;
            height: 24px;
        }}
        .timeline-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
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
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
        }}
        .timeline-step-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
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
            font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
        }}

        /* ── Custom: Prediction Card ── */
        .prediction-card {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: {BORDER_RADIUS};
            padding: {CARD_PADDING};
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
            transition: all 0.2s ease;
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
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
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
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
            transition: all 0.2s ease;
        }}
        .incident-card-info:hover {{
            border-color: {ACCENT};
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}

        /* ── New Utility Classes for Light Theme Polish ── */
        .rca-details-box {{
            background-color: {BG};
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 12px;
            margin-top: 12px;
        }}
        .sla-header-label {{
            font-weight: 500;
            font-size: 13px;
            color: {TEXT};
        }}
        .duplicate-warning-box {{
            background-color: {BG};
            border: 1px solid {BORDER};
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 20px;
        }}
        .duplicate-warning-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        .duplicate-warning-id {{
            font-weight: 700;
            font-size: 1.1em;
            color: {TEXT};
        }}
        .duplicate-warning-desc {{
            font-size: 0.95em;
            color: {TEXT};
            margin-bottom: 10px;
        }}
        .duplicate-warning-meta {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            font-size: 0.85em;
            color: {MUTED};
        }}
        .escalation-rec-box {{
            padding: 24px;
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 12px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        }}
        .reason-bullet-item {{
            margin-left: 12px;
            margin-bottom: 6px;
            font-size: 13px;
            color: {MUTED};
        }}
        .prediction-highlight {{
            font-size: 16px;
            font-weight: 600;
            color: {ACCENT};
        }}
        .sla-container {{
            margin-bottom: 16px;
        }}
        .sla-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        .detail-value-mono {{
            font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 13px;
            color: {TEXT};
            margin-bottom: 12px;
        }}
        .detail-value-mono-large {{
            font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 16px;
            font-weight: 600;
        }}

        /* ── Responsiveness and Smooth Media Adjustments ── */
        @media (max-width: 768px) {{
            .top-nav {{
                flex-direction: column;
                align-items: flex-start;
                gap: 12px;
            }}
            .top-nav .nav-stats {{
                width: 100%;
                justify-content: space-between;
            }}
            .metric-card .value {{
                font-size: 24px;
            }}
            .duplicate-warning-meta {{
                grid-template-columns: 1fr;
            }}
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
