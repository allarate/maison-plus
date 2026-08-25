import streamlit as st
from database import add_interet
from phone import phone_input


def interest_button(annonce_id, key_prefix):
    """Renders the 'Je suis intéressé(e)' button + phone number form for one listing."""
    show_key = f"show_form_{key_prefix}_{annonce_id}"

    if st.button("❤️ Je suis intéressé(e)", key=f"int_{key_prefix}_{annonce_id}", use_container_width=True):
        st.session_state[show_key] = True

    if st.session_state.get(show_key, False):
        with st.form(f"form_interet_{key_prefix}_{annonce_id}"):
            st.markdown("**Laissez votre numéro de téléphone**")
            telephone = phone_input(f"interet_{key_prefix}_{annonce_id}", label="Votre numéro *")
            send = st.form_submit_button("✅ Envoyer ma demande", use_container_width=True)
            if send:
                if not telephone:
                    st.error("Veuillez entrer votre numéro")
                else:
                    ok, msg = add_interet(
                        annonce_id,
                        st.session_state.get("user", ""),
                        st.session_state.get("nom", ""),
                        st.session_state.get("prenom", ""),
                        telephone,
                    )
                    if ok:
                        st.success(msg)
                        st.session_state[show_key] = False
                        st.rerun()
                    else:
                        st.warning(msg)
