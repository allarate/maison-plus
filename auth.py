from database import get_user_by_phone, create_user
from phone import is_valid_phone

def login(telephone, password):
    user = get_user_by_phone(telephone)
    if user and user["password"] == password:
        return True, user["role"], user["nom"], user["prenom"], user["photo"]
    return False, None, None, None, None

def register(nom, prenom, telephone, password):
    if not is_valid_phone(telephone):
        return False, "Numéro de téléphone invalide"
    return create_user(nom, prenom, telephone, password, role="user")
