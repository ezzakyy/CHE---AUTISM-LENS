# database.py

import sqlite3
from config import DATABASE_NAME, USERS_TABLE, CONVERSATIONS_TABLE

def get_db_connection():
    #Etablir la connection
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    #Initialiser la base de donnees et creer les tables si elles n'existent pas.
    #Ajoute egalement la colonne email et l'index unique si necessaire.
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table des utilisateurs (creation si absente)
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {USERS_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Verifier si la colonne email existe, sinon l'ajouter 
    cursor.execute(f"PRAGMA table_info({USERS_TABLE})")
    columns = [col[1] for col in cursor.fetchall()]
    if 'email' not in columns:
        cursor.execute(f"ALTER TABLE {USERS_TABLE} ADD COLUMN email TEXT")
        print(" Colonne 'email' ajoutee a la table users.")

    # Creer un index unique sur email (permet NULLs multiples)
    cursor.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON {USERS_TABLE}(email)")

    # Table des conversations 
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {CONVERSATIONS_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            user_message TEXT,
            bot_response TEXT,
            prediction_score REAL,
            prediction_result TEXT,
            user_data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES {USERS_TABLE}(id)
        )
    ''')

    conn.commit()
    conn.close()
    print(" Base de donnees initialisee avec succes (email integre).")

def add_user(username, password, email):
    #Ajouter un nouvel utilisateur a la base de donnees avec email.
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"INSERT INTO {USERS_TABLE} (username, password, email) VALUES (?, ?, ?)",
            (username, password, email)
        )
        conn.commit()
        user_id = cursor.lastrowid
        print(f" Utilisateur {username} ajoute avec succes (email: {email}).")
        return user_id
    except sqlite3.IntegrityError as e:
        # Verifier si l'erreur est due a l'email ou au nom d'utilisateur
        if "email" in str(e):
            print(f" L'adresse email {email} est deja utilisee.")
        elif "username" in str(e):
            print(f" Le nom d'utilisateur {username} existe deja.")
        else:
            print(f" Erreur d'integrite : {e}")
        return None
    finally:
        conn.close()

def get_user(username, password):
    #Verifier les informations d'identification de l'utilisateur et retourner son ID
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT id FROM {USERS_TABLE} WHERE username = ? AND password = ?",
        (username, password)
    )
    user = cursor.fetchone()
    conn.close()
    return user['id'] if user else None

def get_user_by_email(email):
    #email verification si deja exist
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM {USERS_TABLE} WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def save_conversation(user_id, user_message, bot_response, prediction_score=None, prediction_result=None, user_data=None):
    #enregistrement un echange en conversation
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        INSERT INTO {CONVERSATIONS_TABLE}
        (user_id, user_message, bot_response, prediction_score, prediction_result, user_data)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, user_message, bot_response, prediction_score, prediction_result, user_data))
    conn.commit()
    conn.close()
    print(f"Conversation sauvegardee pour l'utilisateur {user_id}.")

if __name__ == "__main__":
    init_db()