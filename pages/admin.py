import streamlit as st
import sys, os, json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from layout import layout
from database import (get_annonces_par_statut, valider_annonce, rejeter_annonce,
                      get_stats, get_all_users, update_user_role, delete_user,
                      get_interets_par_annonce, marquer_occupe, marquer_disponible,
                      delete_annonce, update_annonce, update_user_password)
from theme import COLORS
from storage import upload_image
import theme

def get_images_html(photos_json, titre="annonce"):
    try:
        photos = json.loads(photos_json) if photos_json else []
    except:
        photos = []
    images_html = ""
    for url in photos:
        images_html += (
            '<img src="' + url + '" '
            'alt="Photo de ' + titre + '" '
            'style="width:250px;height:167px;object-fit:cover;'
            'border-radius:8px;margin-right:8px;margin-bottom:8px;" />'
        )
    return images_html

def _confirm_delete(key, label, on_confirm):
    """Renders a 🗑️ button; first click asks for confirmation, second click deletes."""
    confirm_key = f"confirm_{key}"
    if not st.session_state.get(confirm_key):
        if st.button(f"🗑️ {label}", key=f"del_{key}", use_container_width=True):
            st.session_state[confirm_key] = True
            st.rerun()
    else:
        st.warning("Suppression définitive et irréversible. Confirmer ?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Oui, supprimer", key=f"delyes_{key}", use_container_width=True):
                on_confirm()
                st.session_state[confirm_key] = False
                st.rerun()
        with c2:
            if st.button("Annuler", key=f"delno_{key}", use_container_width=True):
                st.session_state[confirm_key] = False
                st.rerun()

def _render_edit_form(a):
    with st.form(f"form_edit_{a['id']}"):
        col1, col2 = st.columns(2)
        with col1:
            titre    = st.text_input("Titre", value=a['titre'], key=f"edit_titre_{a['id']}")
            ville    = st.text_input("Ville", value=a['ville'], key=f"edit_ville_{a['id']}")
            quartier = st.text_input("Quartier", value=a['quartier'] or "", key=f"edit_quartier_{a['id']}")
            prix     = st.number_input("Prix mensuel (FCFA)", min_value=0, step=5000,
                                        value=int(a['prix']), key=f"edit_prix_{a['id']}")
        with col2:
            chambres_options = ["1", "2", "3", "4", "5", "6+"]
            chambres_idx = chambres_options.index(a['chambres']) if a['chambres'] in chambres_options else 0
            chambres = st.selectbox("Nombre de chambres", chambres_options, index=chambres_idx,
                                     key=f"edit_chambres_{a['id']}")
            type_options = ["Appartement", "Villa", "Studio", "Duplex", "Chambre"]
            type_idx = type_options.index(a['type_bien']) if a['type_bien'] in type_options else 0
            type_bien = st.selectbox("Type de bien", type_options, index=type_idx, key=f"edit_type_{a['id']}")
            contact = st.text_input("Contact (avec indicatif, ex: +237612345678)",
                                     value=a['contact'], key=f"edit_contact_{a['id']}")

        description = st.text_area("Description", value=a['description'] or "", key=f"edit_desc_{a['id']}")

        nouvelles_photos = st.file_uploader(
            "Changer les photos (remplace les photos actuelles — laisser vide pour les garder)",
            accept_multiple_files=True, type=["jpg", "jpeg", "png"], key=f"edit_photos_{a['id']}"
        )

        c1, c2 = st.columns(2)
        with c1:
            save = st.form_submit_button("💾 Enregistrer", use_container_width=True)
        with c2:
            cancel = st.form_submit_button("Annuler", use_container_width=True)

    if save:
        if not titre or not ville or not quartier or not contact:
            st.error("Veuillez remplir tous les champs obligatoires")
        else:
            photos_json = None
            if nouvelles_photos:
                photo_urls = [upload_image(photo.getbuffer()) for photo in nouvelles_photos]
                photos_json = json.dumps(photo_urls)

            update_annonce(a['id'], {
                "titre": titre, "type_bien": type_bien, "ville": ville, "quartier": quartier,
                "chambres": chambres, "prix": prix, "contact": contact, "description": description,
                "photos": photos_json,
            })
            st.session_state[f"editing_{a['id']}"] = False
            st.success("Annonce mise à jour !")
            st.rerun()
    if cancel:
        st.session_state[f"editing_{a['id']}"] = False
        st.rerun()

def _edit_button(a):
    edit_key = f"editing_{a['id']}"
    if st.button("✏️ Modifier", key=f"editbtn_{a['id']}", use_container_width=True):
        st.session_state[edit_key] = not st.session_state.get(edit_key, False)
        st.rerun()
    if st.session_state.get(edit_key):
        _render_edit_form(a)

def _render_annonce_validee(a):
    interets = get_interets_par_annonce(a['id'])

    occupe      = a['statut_occupation'] == 'occupé' if a['statut_occupation'] else False
    color       = COLORS["danger"] if occupe else COLORS["success"]
    label       = "🔒 OCCUPÉE" if occupe else "✅ DISPONIBLE"
    images_html = get_images_html(a['photos'], a['titre'])

    st.markdown(
        '<div class="mp-anim-card" style="background:white;border-radius:12px;padding:1.2rem;'
        'margin-bottom:0.5rem;box-shadow:0 2px 8px rgba(0,0,0,0.08);'
        'border-left:5px solid ' + color + ';">'
        '<div style="display:flex;justify-content:space-between;align-items:center;">'
        '<h3 style="color:' + COLORS['primary'] + ';margin:0;">' + a['titre'] +
        ' — 📍 ' + a['ville'] + (' — ' + a['quartier'] if a['quartier'] else '') + '</h3>'
        '<span style="background:' + color + '20;color:' + color + ';padding:4px 12px;'
        'border-radius:20px;font-size:0.85rem;font-weight:600;">' + label + '</span>'
        '</div>'
        + ('<div style="margin:0.8rem 0;text-align:center;">' + images_html + '</div>' if images_html else '')
        + '<p style="color:' + COLORS['text_muted'] + ';margin:0.3rem 0;">'
        + a['type_bien'] + ' | 🛏 ' + a['chambres'] + ' ch.'
        ' | 💰 <strong>' + f"{int(a['prix']):,}" + ' FCFA/mois</strong></p>'
        '<p style="color:' + COLORS['danger'] + ';font-weight:600;">❤️ ' + str(len(interets)) + ' demande(s)</p>'
        '</div>',
        unsafe_allow_html=True
    )

    # Boutons occupée / en location / modifier / suppression
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        if not occupe:
            if st.button("🔒 Occupée", key=f"occ_{a['id']}", use_container_width=True):
                marquer_occupe(a['id'])
                st.rerun()
        else:
            if st.button("🟢 En location", key=f"lib_{a['id']}", use_container_width=True):
                marquer_disponible(a['id'])
                st.rerun()
    with col2:
        _edit_button(a)
    with col3:
        _confirm_delete(f"annonce_{a['id']}", "Supprimer",
                         lambda aid=a['id']: delete_annonce(aid))

    # Liste des demandeurs
    st.markdown("<br>", unsafe_allow_html=True)
    if not interets:
        st.caption("Aucune demande d'intérêt pour cette annonce.")
    for i in interets:
        st.markdown(
            '<div style="background:' + COLORS['surface_alt'] + ';border-radius:8px;padding:0.8rem 1.2rem;'
            'margin-bottom:0.4rem;border-left:4px solid ' + COLORS['danger'] + ';">'
            '<p style="margin:0;color:' + COLORS['primary'] + ';">👤 <strong>' + str(i['user_prenom']) + ' ' + str(i['user_nom']) + '</strong>'
            ' &nbsp;|&nbsp; 🆔 ' + str(i['user_email']) +
            ' &nbsp;|&nbsp; 📞 <strong style="color:' + COLORS['danger'] + ';font-size:1.1rem;">' + str(i['telephone']) + '</strong></p>'
            '<p style="margin:0;color:' + COLORS['text_faint'] + ';font-size:0.8rem;">🕐 ' + str(i['date_demande'])[:16] + '</p>'
            '</div>',
            unsafe_allow_html=True
        )
    st.markdown("<br>", unsafe_allow_html=True)

def show():
    def content():
        st.title("⚙️ Administration Maison++")
        admin = st.session_state.get("user")

        # ===== STATS =====
        stats = get_stats()
        with st.container(border=True):
            theme.card_marker()
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("📋 Total",        stats["total"])
            c2.metric("🟡 En attente",   stats["en_attente"])
            c3.metric("🟢 Validées",     stats["validées"])
            c4.metric("🔴 Rejetées",     stats["rejetées"])
            c5.metric("🔒 Occupées",     stats["occupées"])
            c6.metric("👥 Utilisateurs", stats["users"])
        st.markdown("<br>", unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs([
            "🟡 En attente",
            "Annonces validées",
            "👥 Utilisateurs"
        ])

        # ===== TAB 1 : En attente =====
        with tab1:
            annonces = get_annonces_par_statut("en_attente")
            if not annonces:
                st.success("✅ Aucune annonce en attente.")
            else:
                st.markdown(f"**{len(annonces)} annonce(s) à valider**")
                for i, a in enumerate(annonces):
                    images_html = get_images_html(a['photos'], a['titre'])
                    st.markdown(
                        '<div class="mp-anim-card" style="animation-delay:' + f"{i * 0.08:.2f}" + 's;'
                        'background:white;border-radius:12px;padding:1.2rem;'
                        'margin-bottom:0.5rem;box-shadow:0 2px 8px rgba(0,0,0,0.08);'
                        'border-left:5px solid ' + COLORS['warning'] + ';">'
                        + ('<div style="margin-bottom:0.8rem;text-align:center;">' + images_html + '</div>' if images_html else '')
                        + '<h3 style="color:' + COLORS['primary'] + ';margin:0;">' + a['titre'] + '</h3>'
                        '<p style="color:' + COLORS['text_muted'] + ';margin:0.3rem 0;">'
                        '📍 ' + a['ville'] + (' — ' + a['quartier'] if a['quartier'] else '') +
                        ' | ' + a['type_bien'] + ' | 🛏 ' + a['chambres'] + ' ch.'
                        ' | 💰 <strong>' + f"{int(a['prix']):,}" + ' FCFA/mois</strong></p>'
                        '<p style="color:' + COLORS['text_soft'] + ';">' + (a['description'] or '') + '</p>'
                        '<p style="color:' + COLORS['text_faint'] + ';font-size:0.8rem;">Soumis par <strong>' + a['proprietaire'] + '</strong> le ' + a['date_creation'][:10] + '</p>'
                        '</div>',
                        unsafe_allow_html=True
                    )
                    col_v, col_r, col_e, col_d = st.columns([2, 2, 2, 2])
                    with col_v:
                        if st.button("✅ Valider", key=f"val_{a['id']}", use_container_width=True):
                            valider_annonce(a["id"], admin)
                            st.success(f"Annonce '{a['titre']}' validée !")
                            st.rerun()
                    with col_r:
                        if st.button("❌ Rejeter", key=f"rej_{a['id']}", use_container_width=True):
                            rejeter_annonce(a["id"], admin)
                            st.warning(f"Annonce '{a['titre']}' rejetée.")
                            st.rerun()
                    with col_e:
                        _edit_button(a)
                    with col_d:
                        _confirm_delete(f"annonce_{a['id']}", "Supprimer",
                                         lambda aid=a['id']: delete_annonce(aid))
                    st.markdown("---")

        # ===== TAB 2 : Annonces validées (statut, demandes d'intérêt, suppression) =====
        with tab2:
            annonces_val = get_annonces_par_statut("validée")
            disponibles = [a for a in annonces_val if a['statut_occupation'] != 'occupé']
            occupees    = [a for a in annonces_val if a['statut_occupation'] == 'occupé']

            sous_tab_dispo, sous_tab_occ = st.tabs([
                f"✅ Disponibles ({len(disponibles)})",
                f"🔒 Occupées ({len(occupees)})",
            ])
            with sous_tab_dispo:
                if not disponibles:
                    st.info("Aucune annonce disponible pour le moment.")
                for a in disponibles:
                    _render_annonce_validee(a)
            with sous_tab_occ:
                if not occupees:
                    st.info("Aucune annonce occupée pour le moment.")
                for a in occupees:
                    _render_annonce_validee(a)

        # ===== TAB 3 : Utilisateurs =====
        with tab3:
            st.markdown("**Gestion des rôles utilisateurs**")
            users = get_all_users()
            for u in users:
                col_u, col_r2, col_p, col_d2 = st.columns([3, 2, 2, 2])
                with col_u:
                    role_icon = "🔴 Admin" if u["role"] == "admin" else "👤 User"
                    st.markdown(f"**{u['prenom']} {u['nom']}** ({u['telephone']}) — {role_icon}")
                with col_r2:
                    if u["telephone"] != admin:
                        nouveau_role = "user" if u["role"] == "admin" else "admin"
                        label_btn = "👤 Rétrograder" if u["role"] == "admin" else "🔴 Promouvoir admin"
                        if st.button(label_btn, key=f"role_{u['id']}", use_container_width=True):
                            update_user_role(u["telephone"], nouveau_role)
                            st.rerun()
                    else:
                        st.markdown("*(vous-même)*")
                with col_p:
                    reset_key = f"reset_{u['id']}"
                    if st.button("🔑 Réinitialiser mdp", key=f"resetbtn_{u['id']}", use_container_width=True):
                        st.session_state[reset_key] = not st.session_state.get(reset_key, False)
                        st.rerun()
                with col_d2:
                    if u["telephone"] != admin:
                        _confirm_delete(f"user_{u['id']}", "Supprimer",
                                         lambda tel=u['telephone']: delete_user(tel))

                if st.session_state.get(f"reset_{u['id']}"):
                    with st.form(f"form_reset_{u['id']}"):
                        nouveau_mdp = st.text_input(
                            f"Nouveau mot de passe pour {u['prenom']} {u['nom']}",
                            key=f"newpwd_{u['id']}"
                        )
                        if st.form_submit_button("Valider"):
                            if nouveau_mdp:
                                update_user_password(u["telephone"], nouveau_mdp)
                                st.session_state[f"reset_{u['id']}"] = False
                                st.success("Mot de passe réinitialisé.")
                                st.rerun()
                            else:
                                st.error("Veuillez entrer un mot de passe.")

                st.markdown("---")

        if st.button("⬅ Retour à l'accueil", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

    layout(content)