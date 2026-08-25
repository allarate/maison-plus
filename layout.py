import streamlit as st
import os
import base64
from datetime import datetime
import theme
from database import delete_session_token

NAV_ITEMS = [
    ("home", "Accueil"),
    ("recherche", "Rechercher"),
    ("mise_en_location", "Louer"),
    ("mes_annonces", "Mes annonces"),
    ("ia", "AI Recommendation"),
]

CONTACT_SERVICE = "+23560856572"


def _go(target):
    st.session_state.page = target
    st.rerun()


def layout(content_fn):
    theme.inject()

    # Garde l'URL synchronisée avec la page courante, pour qu'une actualisation
    # (reload complet, session_state perdu) rouvre la même page via main.py.
    if st.session_state.get("page") and st.query_params.get("page") != st.session_state.page:
        st.query_params["page"] = st.session_state.page

    nom    = st.session_state.get("nom") or ""
    prenom = st.session_state.get("prenom") or ""
    display = (prenom + " " + nom).strip() or st.session_state.get("user") or ""
    current_page = st.session_state.get("page")
    is_admin = st.session_state.get("role") == "admin"

    logo_html = ""
    image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages", "a4.png")
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        logo_html = '<img src="data:image/png;base64,' + b64 + '" style="height:36px;width:auto;object-fit:contain;" />'

    items = list(NAV_ITEMS) + ([("admin", "Administration")] if is_admin else [])

    marker = "header-bar-marker"
    st.markdown(f"""
        <div id="{marker}"></div>
        <style>
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        [data-testid="stHeader"] {{ display: none !important; }}
        [data-testid="stToolbar"] {{ display: none !important; }}
        .block-container {{ padding-top: 1.5rem !important; }}
        div[data-testid="stElementContainer"]:has(#{marker}) + div [data-testid="stHorizontalBlock"] {{
            position: fixed;
            top: 0; left: 0; right: 0;
            height: 60px;
            background-color: var(--color-primary);
            display: flex;
            align-items: center;
            flex-wrap: nowrap;
            overflow-x: auto;
            padding: 0 1.5rem;
            z-index: 9999;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            gap: 0.3rem;
        }}
        div[data-testid="stElementContainer"]:has(#{marker}) + div [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {{
            width: fit-content !important;
            flex: 0 0 auto !important;
            min-width: 0 !important;
        }}
        div[data-testid="stElementContainer"]:has(#{marker}) + div [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:has(.st-key-nav_avatar) {{
            margin-left: auto !important;
        }}
        div[data-testid="stElementContainer"]:has(#{marker}) + div [data-testid="stHorizontalBlock"] div[data-testid="stButton"] button {{
            background-color: transparent;
            color: #cfd2e6;
            border: none;
            font-size: 0.82rem;
            font-weight: 600;
            padding: 6px 12px;
            white-space: nowrap;
        }}
        div[data-testid="stElementContainer"]:has(#{marker}) + div [data-testid="stHorizontalBlock"] div[data-testid="stButton"] button:hover {{
            background-color: rgba(255,255,255,0.1);
            color: white;
        }}
        div[data-testid="stElementContainer"]:has(#{marker}) + div [data-testid="stHorizontalBlock"] div[data-testid="stButton"] button[kind="primary"] {{
            background-color: var(--color-primary-light);
            color: white;
        }}
        div[data-testid="stElementContainer"]:has(#{marker}) + div [data-testid="stHorizontalBlock"] .st-key-nav_logout button {{
            border: 1.5px solid var(--color-danger-light) !important;
            color: var(--color-danger-light) !important;
        }}
        div[data-testid="stElementContainer"]:has(#{marker}) + div [data-testid="stHorizontalBlock"] .st-key-nav_logout button:hover {{
            background-color: var(--color-danger-light) !important;
            color: var(--color-primary) !important;
        }}
        .mp-header-spacer {{ height: 40px; }}
        @media (max-width: 640px) {{
            div[data-testid="stElementContainer"]:has(#{marker}) + div [data-testid="stHorizontalBlock"] {{
                position: static;
                height: auto;
                flex-wrap: wrap;
                justify-content: center;
                overflow-x: visible;
                padding: 0.5rem 0.75rem;
                gap: 0.3rem 0.2rem;
            }}
            div[data-testid="stElementContainer"]:has(#{marker}) + div [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:has(.st-key-nav_avatar) {{
                margin-left: 0 !important;
            }}
            div[data-testid="stElementContainer"]:has(#{marker}) + div [data-testid="stHorizontalBlock"] div[data-testid="stButton"] button {{
                font-size: 0.72rem;
                padding: 5px 9px;
            }}
            .mp-header-spacer {{ display: none; }}
            .block-container {{ padding-top: 0.5rem !important; }}
        }}
        .custom-footer {{
            position: fixed;
            bottom: 0; left: 0; right: 0;
            min-height: 50px;
            background-color: var(--color-primary);
            color: #aaa;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            gap: 0.2rem;
            padding: 0.4rem 1rem;
            font-size: 0.85rem;
            z-index: 9999;
        }}
        </style>
    """, unsafe_allow_html=True)

    cols = st.columns([0.6] + [1] * len(items) + [1.4, 0.8])
    with cols[0]:
        st.markdown(logo_html, unsafe_allow_html=True)
    for i, (target, label) in enumerate(items):
        with cols[i + 1]:
            btn_type = "primary" if target == current_page else "secondary"
            if st.button(label, key=f"nav_{target}", type=btn_type):
                _go(target)
    with cols[-2]:
        photo = st.session_state.get("photo")
        if photo:
            st.markdown(
                f'<style>.st-key-nav_avatar button::before {{'
                f'content: ""; display: inline-block; width: 20px; height: 20px; border-radius: 50%;'
                f'background-image: url({photo}); background-size: cover;'
                f'vertical-align: middle; margin-right: 6px;'
                f'}}</style>',
                unsafe_allow_html=True,
            )
            icon = None
        else:
            icon = "👤"
        if st.button(display, key="nav_avatar", icon=icon,
                     type="primary" if current_page == "profil" else "secondary"):
            _go("profil")
    with cols[-1]:
        if st.button("🚪 Quitter", key="nav_logout"):
            token = st.query_params.get("token")
            if token:
                delete_session_token(token)
            st.query_params.clear()
            for key in ["user", "role", "nom", "prenom", "photo"]:
                st.session_state[key] = None
            _go("login")

    st.markdown('<div class="mp-header-spacer"></div>', unsafe_allow_html=True)

    content_fn()

    date_jour = datetime.now().strftime("%d/%m/%Y")
    st.markdown(f"""
        <div class="custom-footer">
            <span>&copy; Maison++ &mdash; {date_jour}</span>
            <span>&#128222; Contacter le service : {CONTACT_SERVICE}</span>
        </div>
    """, unsafe_allow_html=True)
