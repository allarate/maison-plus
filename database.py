import os
import certifi
os.environ.setdefault("SSL_CERT_FILE", certifi.where())

import libsql_client
import streamlit as st


def get_conn():
    t = st.secrets["turso"]
    url = t["url"].replace("libsql://", "https://", 1)
    return libsql_client.create_client_sync(url=url, auth_token=t["auth_token"])


def _rows(result):
    return [row.asdict() for row in result.rows]


def _row(result):
    rows = result.rows
    return rows[0].asdict() if rows else None


def init_db():
    conn = get_conn()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            telephone TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            photo TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS annonces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            type_bien TEXT NOT NULL,
            ville TEXT NOT NULL,
            quartier TEXT,
            chambres TEXT NOT NULL,
            prix INTEGER NOT NULL,
            contact TEXT NOT NULL,
            description TEXT,
            photos TEXT,
            proprietaire TEXT NOT NULL,
            statut TEXT NOT NULL DEFAULT 'en_attente',
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_validation TIMESTAMP,
            valide_par TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS interets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            annonce_id INTEGER NOT NULL,
            user_email TEXT NOT NULL,
            user_nom TEXT,
            user_prenom TEXT,
            telephone TEXT,
            date_demande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(annonce_id, user_email)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            telephone TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    if not conn.execute("SELECT * FROM users WHERE telephone = '+23500000000'").rows:
        conn.execute(
            "INSERT INTO users (nom, prenom, telephone, password, role) VALUES (?, ?, ?, ?, ?)",
            ["Admin", "Maison++", "+23500000000", "admin123", "admin"]
        )

    for stmt in [
        "ALTER TABLE annonces ADD COLUMN statut_occupation TEXT DEFAULT 'disponible'",
        "ALTER TABLE annonces ADD COLUMN valide_par TEXT",
        "ALTER TABLE users ADD COLUMN photo TEXT",
    ]:
        try:
            conn.execute(stmt)
        except Exception:
            pass

    conn.close()

# ===== USERS =====

def create_user(nom, prenom, telephone, password, role="user"):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (nom, prenom, telephone, password, role) VALUES (?, ?, ?, ?, ?)",
            [nom, prenom, telephone, password, role]
        )
        return True, "Inscription réussie"
    except libsql_client.LibsqlError:
        return False, "Ce numéro de téléphone est déjà utilisé"
    finally:
        conn.close()

def get_user_by_phone(telephone):
    conn = get_conn()
    user = _row(conn.execute("SELECT * FROM users WHERE telephone = ?", [telephone]))
    conn.close()
    return user

def get_all_users():
    conn = get_conn()
    users = _rows(conn.execute("SELECT id, nom, prenom, telephone, role FROM users ORDER BY id"))
    conn.close()
    return users

def update_user_photo(telephone, photo_filename):
    conn = get_conn()
    conn.execute("UPDATE users SET photo = ? WHERE telephone = ?", [photo_filename, telephone])
    conn.close()

def update_user_password(telephone, new_password):
    conn = get_conn()
    conn.execute("UPDATE users SET password = ? WHERE telephone = ?", [new_password, telephone])
    conn.close()

def update_user_role(telephone, role):
    conn = get_conn()
    conn.execute("UPDATE users SET role = ? WHERE telephone = ?", [role, telephone])
    conn.close()

def delete_user(telephone):
    conn = get_conn()
    conn.batch([
        ("DELETE FROM sessions WHERE telephone = ?", [telephone]),
        ("DELETE FROM users WHERE telephone = ?", [telephone]),
    ])
    conn.close()

# ===== SESSIONS (connexion persistante après actualisation) =====

def create_session_token(token, telephone):
    conn = get_conn()
    conn.execute("INSERT OR REPLACE INTO sessions (token, telephone) VALUES (?, ?)", [token, telephone])
    conn.close()

def get_session_user(token):
    conn = get_conn()
    row = _row(conn.execute("SELECT telephone FROM sessions WHERE token = ?", [token]))
    conn.close()
    return row["telephone"] if row else None

def delete_session_token(token):
    conn = get_conn()
    conn.execute("DELETE FROM sessions WHERE token = ?", [token])
    conn.close()

# ===== ANNONCES =====

def create_annonce(data):
    conn = get_conn()
    conn.execute("""
        INSERT INTO annonces
        (titre, type_bien, ville, quartier, chambres, prix, contact, description, photos, proprietaire)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        data["titre"], data["type_bien"], data["ville"], data.get("quartier", ""),
        data["chambres"], data["prix"], data["contact"],
        data.get("description", ""), data.get("photos", ""), data["proprietaire"]
    ])
    conn.close()

def delete_annonce(annonce_id):
    conn = get_conn()
    conn.batch([
        ("DELETE FROM interets WHERE annonce_id = ?", [annonce_id]),
        ("DELETE FROM annonces WHERE id = ?", [annonce_id]),
    ])
    conn.close()

def update_annonce(annonce_id, data):
    conn = get_conn()
    if data.get("photos") is not None:
        conn.execute("""
            UPDATE annonces
            SET titre=?, type_bien=?, ville=?, quartier=?, chambres=?, prix=?, contact=?, description=?, photos=?
            WHERE id=?
        """, [
            data["titre"], data["type_bien"], data["ville"], data.get("quartier", ""),
            data["chambres"], data["prix"], data["contact"],
            data.get("description", ""), data["photos"], annonce_id
        ])
    else:
        conn.execute("""
            UPDATE annonces
            SET titre=?, type_bien=?, ville=?, quartier=?, chambres=?, prix=?, contact=?, description=?
            WHERE id=?
        """, [
            data["titre"], data["type_bien"], data["ville"], data.get("quartier", ""),
            data["chambres"], data["prix"], data["contact"],
            data.get("description", ""), annonce_id
        ])
    conn.close()

def get_annonces_validees(ville=None, type_bien=None, chambres=None, prix_max=None, quartier=None):
    conn = get_conn()
    query = "SELECT * FROM annonces WHERE statut = 'validée' AND (statut_occupation IS NULL OR statut_occupation = 'disponible')"
    params = []
    if ville:
        query += " AND LOWER(ville) LIKE ?"
        params.append(f"%{ville.lower()}%")
    if quartier:
        query += " AND LOWER(quartier) LIKE ?"
        params.append(f"%{quartier.lower()}%")
    if type_bien:
        query += " AND type_bien = ?"
        params.append(type_bien)
    if chambres:
        query += " AND chambres = ?"
        params.append(chambres)
    if prix_max:
        query += " AND prix <= ?"
        params.append(prix_max)
    query += " ORDER BY date_validation DESC"
    annonces = _rows(conn.execute(query, params))
    conn.close()
    return annonces

def get_price_stats(ville=None, type_bien=None, quartier=None):
    conn = get_conn()
    query = "SELECT prix FROM annonces WHERE statut = 'validée'"
    params = []
    if ville:
        query += " AND LOWER(ville) LIKE ?"
        params.append(f"%{ville.lower()}%")
    if quartier:
        query += " AND LOWER(quartier) LIKE ?"
        params.append(f"%{quartier.lower()}%")
    if type_bien:
        query += " AND type_bien = ?"
        params.append(type_bien)
    prices = sorted(row[0] for row in conn.execute(query, params).rows)
    conn.close()

    if not prices:
        return {"count": 0}
    n = len(prices)
    mediane = prices[n // 2] if n % 2 else (prices[n // 2 - 1] + prices[n // 2]) / 2
    return {
        "count": n,
        "moyenne": round(sum(prices) / n),
        "mediane": round(mediane),
        "min": min(prices),
        "max": max(prices),
    }

def get_annonces_par_statut(statut):
    conn = get_conn()
    annonces = _rows(conn.execute(
        "SELECT * FROM annonces WHERE statut = ? ORDER BY date_creation DESC", [statut]
    ))
    conn.close()
    return annonces

def get_annonces_proprietaire(email):
    conn = get_conn()
    annonces = _rows(conn.execute(
        "SELECT * FROM annonces WHERE proprietaire = ? ORDER BY date_creation DESC", [email]
    ))
    conn.close()
    return annonces

def valider_annonce(annonce_id, admin_email):
    conn = get_conn()
    conn.execute("""
        UPDATE annonces SET statut = 'validée', valide_par = ?,
        date_validation = CURRENT_TIMESTAMP, statut_occupation = 'disponible'
        WHERE id = ?
    """, [admin_email, annonce_id])
    conn.close()

def rejeter_annonce(annonce_id, admin_email):
    conn = get_conn()
    conn.execute("""
        UPDATE annonces SET statut = 'rejetée', valide_par = ?
        WHERE id = ?
    """, [admin_email, annonce_id])
    conn.close()

def marquer_occupe(annonce_id):
    conn = get_conn()
    conn.execute("UPDATE annonces SET statut_occupation = 'occupé' WHERE id = ?", [annonce_id])
    conn.close()

def marquer_disponible(annonce_id):
    conn = get_conn()
    conn.execute("UPDATE annonces SET statut_occupation = 'disponible' WHERE id = ?", [annonce_id])
    conn.close()

def get_stats():
    conn = get_conn()
    stats = {
        "total":      conn.execute("SELECT COUNT(*) FROM annonces").rows[0][0],
        "en_attente": conn.execute("SELECT COUNT(*) FROM annonces WHERE statut='en_attente'").rows[0][0],
        "validées":   conn.execute("SELECT COUNT(*) FROM annonces WHERE statut='validée'").rows[0][0],
        "rejetées":   conn.execute("SELECT COUNT(*) FROM annonces WHERE statut='rejetée'").rows[0][0],
        "users":      conn.execute("SELECT COUNT(*) FROM users").rows[0][0],
        "occupées":   conn.execute("SELECT COUNT(*) FROM annonces WHERE statut_occupation='occupé'").rows[0][0],
    }
    conn.close()
    return stats

# ===== INTERETS =====

def add_interet(annonce_id, user_email, user_nom, user_prenom, telephone):
    conn = get_conn()
    try:
        conn.execute("""
            INSERT INTO interets (annonce_id, user_email, user_nom, user_prenom, telephone)
            VALUES (?, ?, ?, ?, ?)
        """, [annonce_id, user_email, user_nom, user_prenom, telephone])
        return True, "✅ Votre demande a été enregistrée ! Le service vous contactera."
    except libsql_client.LibsqlError:
        return False, "⚠️ Vous avez déjà manifesté votre intérêt pour cette annonce."
    finally:
        conn.close()

def get_interets_par_annonce(annonce_id):
    conn = get_conn()
    interets = _rows(conn.execute(
        "SELECT * FROM interets WHERE annonce_id = ? ORDER BY date_demande DESC",
        [annonce_id]
    ))
    conn.close()
    return interets

def get_all_interets():
    conn = get_conn()
    interets = _rows(conn.execute("""
        SELECT i.*, a.titre, a.ville, a.quartier, a.type_bien, a.chambres, a.prix
        FROM interets i
        JOIN annonces a ON i.annonce_id = a.id
        ORDER BY a.id, i.date_demande DESC
    """))
    conn.close()
    return interets

def count_interets(annonce_id):
    conn = get_conn()
    count = conn.execute(
        "SELECT COUNT(*) FROM interets WHERE annonce_id = ?", [annonce_id]
    ).rows[0][0]
    conn.close()
    return count

init_db()
