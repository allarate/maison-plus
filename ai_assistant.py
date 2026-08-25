import anthropic
import streamlit as st
from anthropic import beta_tool
from database import get_annonces_validees, get_price_stats
from layout import CONTACT_SERVICE

# Changer ici pour réduire les coûts : "claude-sonnet-5" (bon compromis)
# ou "claude-haiku-4-5" (le moins cher). Voir la doc Anthropic pour les tarifs.
MODEL = "claude-opus-5"

SYSTEM_PROMPT = """Tu es l'assistant immobilier de Maison++, une application de location de \
maisons au Tchad. Les villes principales couvertes sont Moundou, N'Djamena et Abéché, mais \
d'autres villes peuvent aussi être présentes dans la base.

Réponds toujours en français, de façon concise et utile.

- Pour toute question sur les prix (moyenne, médiane, budget typique), utilise l'outil `stats_prix`.
- Pour recommander des logements ou répondre à "trouve-moi une maison...", utilise l'outil `rechercher_annonces`.
- Ne fabrique jamais de prix ou d'annonces : base-toi uniquement sur les résultats retournés par \
les outils. Si un outil ne retourne aucun résultat, dis-le clairement plutôt que d'inventer une réponse.
- Quand tu présentes des annonces recommandées, affiche-les sous forme de tableau avec une dernière \
colonne "Contact" contenant le numéro de service fourni par l'outil, pour que l'utilisateur sache \
qui appeler.
- Si la question ne concerne ni les prix ni la recherche de logement, réponds normalement sans \
outil, en restant dans le contexte de la location immobilière au Tchad."""


@beta_tool
def stats_prix(ville: str = "", type_bien: str = "", quartier: str = "") -> str:
    """Calcule les statistiques de prix (moyenne, médiane, min, max) des annonces validées.

    Args:
        ville: Filtrer par ville (ex: Moundou, N'Djamena, Abéché). Laisser vide pour toutes les villes.
        type_bien: Filtrer par type (Appartement, Villa, Studio, Duplex, Chambre). Laisser vide pour tous les types.
        quartier: Filtrer par quartier. Laisser vide pour tous les quartiers.
    """
    stats = get_price_stats(ville=ville or None, type_bien=type_bien or None, quartier=quartier or None)
    if stats["count"] == 0:
        return "Aucune annonce validée ne correspond à ces critères."
    return (
        f"{stats['count']} annonce(s) trouvée(s). "
        f"Prix moyen : {stats['moyenne']:,} FCFA/mois. "
        f"Prix médian : {stats['mediane']:,} FCFA/mois. "
        f"Minimum : {stats['min']:,} FCFA. Maximum : {stats['max']:,} FCFA."
    )


@beta_tool
def rechercher_annonces(ville: str = "", budget_max: int = 0, chambres: str = "", type_bien: str = "") -> str:
    """Recherche des annonces de maisons disponibles à louer, pour faire des recommandations.

    Args:
        ville: Ville souhaitée (ex: Moundou, N'Djamena, Abéché). Laisser vide pour toutes.
        budget_max: Budget maximum en FCFA par mois. 0 pour aucune limite.
        chambres: Nombre de chambres souhaité (1, 2, 3, 4, 5, 6+). Laisser vide pour tous.
        type_bien: Type de bien (Appartement, Villa, Studio, Duplex, Chambre). Laisser vide pour tous.
    """
    annonces = get_annonces_validees(
        ville=ville or None,
        prix_max=budget_max or None,
        chambres=chambres or None,
        type_bien=type_bien or None,
    )
    if not annonces:
        return "Aucune annonce disponible ne correspond à ces critères."
    lignes = [f"Numéro de service à afficher dans la colonne Contact : {CONTACT_SERVICE}"]
    for a in annonces[:8]:
        quartier_txt = f" ({a['quartier']})" if a["quartier"] else ""
        lignes.append(
            f"- {a['titre']} | {a['ville']}{quartier_txt} | {a['type_bien']} | "
            f"{a['chambres']} chambre(s) | {int(a['prix']):,} FCFA/mois | Contact: {CONTACT_SERVICE}"
        )
    return "\n".join(lignes)


def ask(question, history):
    """Envoie une question à Claude avec accès aux outils prix/recherche.
    `history` est la liste des messages précédents au format
    [{"role": "user"|"assistant", "content": str}, ...].
    Retourne (reponse_texte, erreur) — l'un des deux est toujours None.
    """
    try:
        api_key = st.secrets["anthropic"]["api_key"]
    except Exception:
        return None, (
            "Configuration IA manquante : renseigne .streamlit/secrets.toml "
            "(section [anthropic], clé api_key) pour activer l'assistant."
        )

    client = anthropic.Anthropic(api_key=api_key)
    messages = history + [{"role": "user", "content": question}]

    try:
        runner = client.beta.messages.tool_runner(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=[stats_prix, rechercher_annonces],
            messages=messages,
        )
        final = None
        for message in runner:
            final = message
        if final is None:
            return None, "Aucune réponse reçue de l'assistant."
        texte = next((b.text for b in final.content if b.type == "text"), "").strip()
        return (texte or "Je n'ai pas pu formuler de réponse."), None
    except anthropic.AuthenticationError:
        return None, "Clé API Anthropic invalide ou expirée."
    except anthropic.RateLimitError:
        return None, "Trop de requêtes en ce moment, réessayez dans un instant."
    except anthropic.APIConnectionError:
        return None, "Impossible de contacter le service IA (problème réseau)."
    except anthropic.APIStatusError as e:
        return None, f"Erreur du service IA : {e.message}"
