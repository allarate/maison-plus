import streamlit as st
import sys, os, re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import register
from database import get_user_by_phone
from phone import phone_input, is_valid_phone
import theme


def show():
    theme.inject()
    st.markdown("""
        <style>
        h1 { text-align: center; color: var(--color-primary); }
        .stButton button {
            background-color: var(--color-primary);
            color: white;
            border-radius: 8px;
            padding: 10px;
            font-size: 15px;
            font-weight: 600;
            width: 100%;
            border: none;
            transition: all 0.3s;
        }
        .stButton button:hover { background-color: var(--color-primary-light); }
        </style>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.title("Maison++")

        with st.container(border=True):
            theme.card_marker()
            st.subheader("Créer un compte")
            st.markdown("<br>", unsafe_allow_html=True)

            with st.form("form_inscription"):
                col1, col2 = st.columns(2)
                with col1:
                    nom = st.text_input("Nom *")
                with col2:
                    prenom = st.text_input("Prénom *")

                st.markdown("<br>", unsafe_allow_html=True)
                telephone = phone_input("register", label="Téléphone *")

                st.markdown("<br>", unsafe_allow_html=True)
                password  = st.text_input("Mot de passe *", type="password")
                password2 = st.text_input("Confirmer le mot de passe *", type="password")

                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("S'inscrire", use_container_width=True)

            if submitted:
                if not nom or not prenom or not password or not password2:
                    st.error("Veuillez remplir tous les champs obligatoires (*)")
                elif not telephone or not is_valid_phone(telephone):
                    st.error("Veuillez entrer un numéro de téléphone valide pour l'indicatif choisi")
                elif password != password2:
                    st.error("Les mots de passe ne correspondent pas")
                elif re.sub(r"\D", "", password) in (
                    re.sub(r"\D", "", telephone),
                    re.sub(r"\D", "", st.session_state.get("register_numero", "")),
                ):
                    st.error("Le mot de passe ne peut pas être identique à votre numéro de téléphone")
                elif get_user_by_phone(telephone):
                    st.error("Ce numéro de téléphone est déjà utilisé")
                else:
                    success, msg = register(nom, prenom, telephone, password)
                    if success:
                        st.success("Compte créé avec succès ! Connectez-vous.")
                        st.session_state.page = "login"
                        st.rerun()
                    else:
                        st.error(msg)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Déjà un compte ? Se connecter", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()
