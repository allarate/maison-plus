import streamlit as st

COLORS = {
    "primary":       "#1a1a2e",
    "primary_light": "#4A90E2",
    "danger":        "#e74c3c",
    "danger_light":  "#ff6b6b",
    "success":       "#27ae60",
    "warning":       "#f39c12",
    "bg":            "#f0f2f6",
    "surface":       "#ffffff",
    "surface_alt":   "#f8f9fa",
    "text_muted":    "#666666",
    "text_faint":    "#aaaaaa",
    "text_soft":     "#444444",
}


def inject():
    st.markdown(f"""
        <style>
        :root {{
            --color-primary: {COLORS['primary']};
            --color-primary-light: {COLORS['primary_light']};
            --color-danger: {COLORS['danger']};
            --color-danger-light: {COLORS['danger_light']};
            --color-success: {COLORS['success']};
            --color-warning: {COLORS['warning']};
            --color-bg: {COLORS['bg']};
            --color-surface: {COLORS['surface']};
            --color-surface-alt: {COLORS['surface_alt']};
            --color-text-muted: {COLORS['text_muted']};
            --color-text-faint: {COLORS['text_faint']};
            --color-text-soft: {COLORS['text_soft']};
        }}
        .stApp {{ background-color: var(--color-bg); font-variant-numeric: tabular-nums; }}

        ::selection {{ background: var(--color-primary-light); color: white; }}

        *:focus-visible {{
            outline: 2px solid var(--color-primary-light) !important;
            outline-offset: 2px !important;
        }}

        ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
        ::-webkit-scrollbar-track {{ background: var(--color-bg); }}
        ::-webkit-scrollbar-thumb {{ background: #c7cbdb; border-radius: 6px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #a9aec6; }}

        div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .mp-card-marker) {{
            background: var(--color-surface);
            border: none;
            border-radius: 16px;
            padding: 0.5rem 1rem;
            box-shadow: 0 2px 16px rgba(26,26,46,0.08);
        }}

        @keyframes mpFadeInUp {{
            from {{ opacity: 0; transform: translateY(16px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
        .mp-anim-card {{
            animation: mpFadeInUp 0.5s ease both;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }}
        .mp-anim-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 10px 24px rgba(26,26,46,0.16) !important;
        }}
        @media (prefers-reduced-motion: reduce) {{
            .mp-anim-card {{ animation: none; }}
            .mp-anim-card:hover {{ transform: none; }}
        }}
        </style>
    """, unsafe_allow_html=True)


def card_marker():
    """Call as the first line inside `with st.container(border=True):` to
    style that container as a white elevated card (see inject())."""
    st.markdown('<div class="mp-card-marker"></div>', unsafe_allow_html=True)
