import streamlit as st
import sys, os, json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from layout import layout
from database import create_annonce
from phone import phone_input
from storage import upload_image
import theme

def show():
    def content():
        st.title("Mettre une maison en location")
        st.info("Votre annonce sera visible après validation par un administrateur.")
        st.markdown("<br>", unsafe_allow_html=True)

        with st.container(border=True):
            theme.card_marker()
            col1, col2 = st.columns(2)
            with col1:
                titre    = st.text_input("Titre de l'annonce *")
                ville    = st.text_input("Ville *")
                quartier = st.text_input("Quartier *")
                prix     = st.number_input("Prix mensuel (FCFA) *", min_value=0, step=5000)
            with col2:
                chambres  = st.selectbox("🛏 Nombre de chambres *", ["1", "2", "3", "4", "5", "6+"])
                type_bien = st.selectbox("Type de bien *", ["Appartement", "Villa", "Studio", "Duplex", "Chambre"])
                contact   = phone_input("mise_en_location", label="Contact *")

            description = st.text_area("Description de la maison", height=120,
                                       placeholder="Décrivez votre bien : superficie, équipements, proximité des commodités...")

            photos = st.file_uploader("📸 Photos de la maison", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

            photo_urls = []
            if photos:
                images_html = ""
                for photo in photos:
                    url = upload_image(photo.getbuffer())
                    photo_urls.append(url)
                    images_html += (
                        '<img src="' + url + '" '
                        'alt="Aperçu photo : ' + photo.name + '" '
                        'style="width:200px;height:133px;object-fit:cover;'
                        'border-radius:8px;margin-right:8px;margin-bottom:8px;" />'
                    )

                if images_html:
                    st.markdown(
                        '<div style="text-align:center;margin-top:0.5rem;">' + images_html + '</div>',
                        unsafe_allow_html=True
                    )

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("📤 Soumettre l'annonce", use_container_width=True):
                if not titre or not ville or not quartier or not contact or prix == 0:
                    st.error("Veuillez remplir tous les champs obligatoires (*)")
                else:
                    create_annonce({
                        "titre":        titre,
                        "type_bien":    type_bien,
                        "ville":        ville,
                        "quartier":     quartier,
                        "chambres":     chambres,
                        "prix":         prix,
                        "contact":      contact,
                        "description":  description,
                        "photos":       json.dumps(photo_urls),
                        "proprietaire": st.session_state.get("user")
                    })
                    st.session_state["flash_success"] = "Annonce soumise ! Elle sera visible après validation par un administrateur."
                    st.session_state.page = "mes_annonces"
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⬅ Retour à l'accueil", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

    layout(content)