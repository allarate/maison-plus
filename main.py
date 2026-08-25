import streamlit as st
from database import get_session_user, get_user_by_phone

VALID_PAGES = {
    "home", "recherche", "mise_en_location", "mes_annonces",
    "ia", "profil", "admin",
}

def run():
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "user" not in st.session_state:
        st.session_state.user = None
    if "role" not in st.session_state:
        st.session_state.role = None
    if "nom" not in st.session_state:
        st.session_state.nom = None
    if "prenom" not in st.session_state:
        st.session_state.prenom = None
    if "photo" not in st.session_state:
        st.session_state.photo = None

    # Reconnexion automatique après une actualisation de page, via le jeton
    # de session conservé dans l'URL (st.session_state est perdu au reload).
    if not st.session_state.user:
        token = st.query_params.get("token")
        if token:
            telephone = get_session_user(token)
            user = get_user_by_phone(telephone) if telephone else None
            if user:
                st.session_state.user   = user["telephone"]
                st.session_state.role   = user["role"]
                st.session_state.nom    = user["nom"]
                st.session_state.prenom = user["prenom"]
                st.session_state.photo  = user["photo"]

                restored_page = st.query_params.get("page")
                st.session_state.page = restored_page if restored_page in VALID_PAGES else "home"
            else:
                st.query_params.clear()

    page = st.session_state.page

    if page == "login":
        from pages.login import show
        show()
    elif page == "register":
        from pages.register import show
        show()
    elif page == "mot_de_passe_oublie":
        from pages.mot_de_passe_oublie import show
        show()
    elif page == "home":
        from pages.home import show
        show()
    elif page == "recherche":
        from pages.recherche import show
        show()
    elif page == "mise_en_location":
        from pages.mise_en_location import show
        show()
    elif page == "ia":
        from pages.ia import show
        show()
    elif page == "mes_annonces":
        from pages.mes_annonces import show
        show()
    elif page == "profil":
        from pages.profil import show
        show()
    elif page == "admin":
        if st.session_state.role == "admin":
            from pages.admin import show
            show()
        else:
            st.error("Accès refusé")
            st.session_state.page = "home"
            st.rerun()
