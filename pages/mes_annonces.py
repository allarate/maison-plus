import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from layout import layout
from database import get_annonces_proprietaire
from theme import COLORS

STATUT_STYLE = {
    "en_attente": (COLORS["warning"], "🟡 En attente de validation"),
    "validée":    (COLORS["success"], "🟢 Validée — visible par tous"),
    "rejetée":    (COLORS["danger"],  "🔴 Rejetée par l'administrateur"),
}

def show():
    def content():
        st.title("Mes annonces")
        if st.session_state.get("flash_success"):
            st.success(st.session_state.pop("flash_success"))
        st.markdown("<br>", unsafe_allow_html=True)

        annonces = get_annonces_proprietaire(st.session_state.get("user"))

        if not annonces:
            st.info("Vous n'avez pas encore publié d'annonce.")
        else:
            for i, a in enumerate(annonces):
                color, label = STATUT_STYLE.get(a["statut"], ("#999", a["statut"]))
                st.markdown(f"""
                    <div class="mp-anim-card" style="animation-delay:{i * 0.08:.2f}s;
                                background:white;border-radius:12px;padding:1.2rem;
                                margin-bottom:1rem;box-shadow:0 2px 8px rgba(0,0,0,0.08);
                                border-left:5px solid {color};">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <h3 style="color:{COLORS['primary']};margin:0;"> {a['titre']}</h3>
                            <span style="background:{color}20;color:{color};padding:4px 12px;
                                         border-radius:20px;font-size:0.85rem;font-weight:600;">
                                {label}
                            </span>
                        </div>
                        <p style="color:{COLORS['text_muted']};margin:0.4rem 0;">
                            {a['ville']} {('— ' + a['quartier']) if a['quartier'] else ''} &nbsp;|&nbsp;
                            {a['type_bien']} &nbsp;|&nbsp; 🛏 {a['chambres']} chambre(s)
                        </p>
                        <p style="color:{COLORS['primary_light']};font-weight:700;"> {int(a['prix']):,} FCFA / mois</p>
                        <p style="color:{COLORS['text_faint']};font-size:0.8rem;">
                            Soumise le {a['date_creation'][:10]}
                            {(' — Traitée par ' + a['valide_par']) if a['valide_par'] else ''}
                        </p>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Nouvelle annonce", use_container_width=True):
                st.session_state.page = "mise_en_location"
                st.rerun()
        with col2:
            if st.button("⬅ Retour à l'accueil", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()

    layout(content)
