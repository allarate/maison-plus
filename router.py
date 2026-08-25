import streamlit as st

def run():
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "user" not in st.session_state:
        st.session_state.user = None
    if "role" not in st.session_state:
        st.session_state.role = None

    page = st.session_state.page

    if page == "login":
        from pages.login import show
        show()
    elif page == "register":
        from pages.register import show
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
    elif page == "admin":
        if st.session_state.role == "admin":
            from pages.admin import show
            show()
        else:
            st.error("Accès refusé")
            st.session_state.page = "home"
            st.rerun()
