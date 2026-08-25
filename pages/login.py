import streamlit as st
import sys, os, secrets
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import login
from database import create_session_token
from phone import phone_input
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
            st.subheader("Connexion")
            st.markdown("<br>", unsafe_allow_html=True)

            telephone = phone_input("login", label="Téléphone")
            password  = st.text_input("Mot de passe", type="password")
            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("Se connecter", use_container_width=True):
                if not telephone:
                    st.error("Veuillez entrer votre numéro de téléphone")
                else:
                    success, role, nom, prenom, photo = login(telephone, password)
                    if success:
                        token = secrets.token_urlsafe(24)
                        create_session_token(token, telephone)
                        st.query_params["token"] = token

                        st.session_state.user   = telephone
                        st.session_state.role   = role
                        st.session_state.nom    = nom
                        st.session_state.prenom = prenom
                        st.session_state.photo  = photo
                        st.session_state.page   = "home"
                        st.rerun()
                    else:
                        st.error("Téléphone ou mot de passe incorrect")

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Pas de compte ? S'inscrire", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()
        with col2:
            if st.button("Mot de passe oublié ?", use_container_width=True):
                st.session_state.page = "mot_de_passe_oublie"
                st.rerun()
