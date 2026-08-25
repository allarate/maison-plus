import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from layout import layout
from database import update_user_photo
from storage import upload_image
from theme import COLORS


def show():
    def content():
        st.title("Mon profil")
        nom    = st.session_state.get("nom", "")
        prenom = st.session_state.get("prenom", "")
        st.subheader(f"{prenom} {nom}")
        st.markdown("<br>", unsafe_allow_html=True)

        col_l, col_c, col_r = st.columns([1, 1, 1])
        with col_c:
            photo = st.session_state.get("photo")
            if photo:
                st.markdown(
                    f'<img src="{photo}" '
                    f'style="width:220px;height:220px;border-radius:50%;object-fit:cover;'
                    f'display:block;margin:0 auto;box-shadow:0 4px 16px rgba(0,0,0,0.15);" />',
                    unsafe_allow_html=True,
                )
            else:
                initiale = (prenom[:1] + nom[:1]).upper() or "?"
                st.markdown(
                    f'<div style="width:220px;height:220px;border-radius:50%;margin:0 auto;'
                    f'background:{COLORS["primary"]};color:white;display:flex;align-items:center;'
                    f'justify-content:center;font-size:3rem;font-weight:700;">{initiale}</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        col_l, col_c, col_r = st.columns([1, 2, 1])
        with col_c:
            nouvelle_photo = st.file_uploader("Changer ma photo de profil", type=["jpg", "jpeg", "png"])
            if nouvelle_photo and st.button("Enregistrer la photo", use_container_width=True):
                url = upload_image(nouvelle_photo.getbuffer(), folder="maisonplus/profils")
                update_user_photo(st.session_state.get("user"), url)
                st.session_state.photo = url
                st.success("Photo de profil mise à jour !")
                st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⬅ Retour à l'accueil", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()

    layout(content)
