import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_user_by_phone, update_user_password
from phone import phone_input
import theme


def show():
    theme.inject()

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.title("Mot de passe oublié")

        verified_phone = st.session_state.get("mdp_oublie_telephone")
        reset_done = st.session_state.get("mdp_oublie_termine")

        with st.container(border=True):
            theme.card_marker()

            if reset_done:
                st.success("Mot de passe réinitialisé avec succès. Vous pouvez maintenant vous connecter.")
            elif not verified_phone:
                st.markdown("Entrez votre numéro de téléphone pour réinitialiser votre mot de passe.")
                st.markdown("<br>", unsafe_allow_html=True)

                telephone = phone_input("mdp_oublie", label="Téléphone")

                if st.button("Vérifier", use_container_width=True):
                    if not telephone:
                        st.error("Veuillez entrer votre numéro de téléphone")
                    elif get_user_by_phone(telephone):
                        st.session_state.mdp_oublie_telephone = telephone
                        st.rerun()
                    else:
                        st.error("Aucun compte n'est associé à ce numéro de téléphone.")
            else:
                st.success("Compte trouvé. Choisissez un nouveau mot de passe.")
                st.markdown("<br>", unsafe_allow_html=True)

                nouveau_mdp = st.text_input("Nouveau mot de passe", type="password")
                confirmation = st.text_input("Confirmer le mot de passe", type="password")

                if st.button("Réinitialiser le mot de passe", use_container_width=True):
                    if not nouveau_mdp:
                        st.error("Veuillez entrer un nouveau mot de passe.")
                    elif nouveau_mdp != confirmation:
                        st.error("Les mots de passe ne correspondent pas.")
                    else:
                        update_user_password(verified_phone, nouveau_mdp)
                        del st.session_state["mdp_oublie_telephone"]
                        st.session_state["mdp_oublie_termine"] = True
                        st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬅ Retour à la connexion", use_container_width=True):
            st.session_state.pop("mdp_oublie_telephone", None)
            st.session_state.pop("mdp_oublie_termine", None)
            st.session_state.page = "login"
            st.rerun()
