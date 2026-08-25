import cloudinary
import cloudinary.uploader
import streamlit as st


def upload_image(file_bytes, folder="maisonplus") -> str:
    """Upload une image vers Cloudinary (upload preset non signé) et renvoie son URL HTTPS permanente."""
    c = st.secrets["cloudinary"]
    result = cloudinary.uploader.unsigned_upload(
        file_bytes,
        c["upload_preset"],
        cloud_name=c["cloud_name"],
        folder=folder,
    )
    return result["secure_url"]
