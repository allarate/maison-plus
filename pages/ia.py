import streamlit as st
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from layout import layout
from theme import COLORS
from ai_assistant import ask
import theme

def show():
    def content():
        st.markdown("""
            <style>
            [data-testid="stChatMessage"] { border-radius: 14px; }
            </style>
        """, unsafe_allow_html=True)

        st.title("Assistant IA Maison++")
        st.caption("Posez vos questions sur la location immobilière")
        st.markdown("<br>", unsafe_allow_html=True)

        if "messages" not in st.session_state:
            st.session_state.messages = []

        with st.container(border=True):
            theme.card_marker()
            if not st.session_state.messages:
                st.markdown(
                    f'<div style="text-align:center;padding:2rem 1rem;color:{COLORS["text_muted"]};">'
                    f'<div style="font-size:2.5rem;">💬</div>'
                    f'<p style="margin:0.5rem 0 0 0;">Essayez : <em>« Quel est le prix moyen à Moundou ? »</em> '
                    f'ou <em>« Trouve-moi une maison à N\'Djamena pour moins de 100 000 FCFA »</em></p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

            if prompt := st.chat_input("Ex: Quel est le prix moyen d'un appartement à Moundou ?"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.write(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("L'assistant réfléchit..."):
                        reponse, erreur = ask(prompt, st.session_state.messages[:-1])
                    if erreur:
                        st.error(erreur)
                        rep = None
                    else:
                        st.write(reponse)
                        rep = reponse

                if rep:
                    st.session_state.messages.append({"role": "assistant", "content": rep})

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑 Effacer la conversation", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        with col2:
            if st.button("⬅ Retour à l'accueil", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()

    layout(content)
