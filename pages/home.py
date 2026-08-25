import streamlit as st
import sys, os, json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from layout import layout
from database import get_annonces_validees
from theme import COLORS
from interet_widget import interest_button


def _first_photo_url(photos_json):
    try:
        photos = json.loads(photos_json) if photos_json else []
    except Exception:
        photos = []
    return photos[0] if photos else None


def show():
    def content():
        st.markdown("""
            <style>
            h1 { text-align: center; color: var(--color-primary); font-size: 2rem; }

            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(18px); }
                to   { opacity: 1; transform: translateY(0); }
            }
            .house-card {
                background: var(--color-surface);
                border-radius: 14px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                animation: fadeInUp 0.6s ease both;
                transition: box-shadow 0.25s ease;
                margin-bottom: 0.8rem;
            }
            .house-card:hover {
                box-shadow: 0 14px 28px rgba(0,0,0,0.18);
            }
            .house-card .photo {
                width: 100%;
                height: 170px;
                object-fit: cover;
                display: block;
                transition: transform 0.4s ease;
            }
            .house-card:hover .photo { transform: scale(1.06); }
            .house-card .photo-placeholder {
                width: 100%;
                height: 170px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2.5rem;
                background: linear-gradient(135deg, #e9ecf5, #dfe3f0);
            }
            .house-card .info { padding: 0.9rem 1rem; }
            .house-card h4 { margin: 0 0 0.3rem 0; color: var(--color-primary); font-size: 1rem; }
            .house-card .meta { margin: 0; color: var(--color-text-muted); font-size: 0.82rem; }
            .house-card .price { margin: 0.4rem 0 0 0; color: var(--color-primary-light); font-weight: 700; }
            </style>
        """, unsafe_allow_html=True)

        col_l, col_c, col_r = st.columns([1, 4, 1])
        with col_c:
            st.title("Accueil")
            role = st.session_state.get("role", "user")
            if role == "admin":
                st.markdown("🔴 **Compte Administrateur**")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Maisons disponibles")

            annonces = get_annonces_validees()[:6]

            if not annonces:
                st.info("Aucune annonce disponible pour le moment.")
            else:
                for row_start in range(0, len(annonces), 3):
                    row = annonces[row_start:row_start + 3]
                    row_cols = st.columns(3)
                    for i, a in enumerate(row):
                        with row_cols[i]:
                            url = _first_photo_url(a["photos"])
                            if url:
                                media = f'<img class="photo" src="{url}" alt="Photo de {a["titre"]}" />'
                            else:
                                media = '<div class="photo-placeholder"></div>'
                            quartier_txt = f' — {a["quartier"]}' if a["quartier"] else ''
                            st.markdown(
                                f'<div class="house-card" style="animation-delay:{(row_start + i) * 0.08:.2f}s">'
                                f'{media}'
                                f'<div class="info">'
                                f'<h4>{a["titre"]}</h4>'
                                f'<p class="meta">📍 {a["ville"]}{quartier_txt} &nbsp;|&nbsp; {a["chambres"]} ch.</p>'
                                f'<p class="price">{int(a["prix"]):,} FCFA / mois</p>'
                                f'</div></div>',
                                unsafe_allow_html=True,
                            )
                            interest_button(a["id"], "home")

                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("Voir toutes les annonces", use_container_width=True):
                        st.session_state.page = "recherche"
                        st.rerun()

    layout(content)
