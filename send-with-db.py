import os
import smtplib
import secrets
import sqlite3
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()
MAIL_PWD = os.getenv('MAIL_PWD')
MAIL_FORM = os.getenv('MAIL_FORM')
MAIL_TO = os.getenv('MAIL_TO')
SMTP_SERVER = os.getenv('SMTP_SERVER')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PORT = int(os.getenv('MAIL_PORT'))

DB_PATH = "db.db"


def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prenom TEXT NOT NULL,
            nom TEXT NOT NULL,
            mail TEXT UNIQUE NOT NULL,
            code TEXT,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
        """)
        # db.execute(
        #     "INSERT OR IGNORE INTO users (prenom, nom, mail) VALUES (?, ?, ?)",
        #     ("Jean", "Daniel", MAIL_TO),
        # )


def envoyer_code(mail):
    code = f"{secrets.randbelow(10000):04d}"

    email = EmailMessage()
    email['From'] = MAIL_FORM
    email['To'] = mail
    email['Subject'] = 'Ton code de vÃĐrification'
    email.add_alternative(f"""
    <html>
      <body>
        <h1>Hi!</h1>
        <p>send <b>email</b> with <i>Python</i>.</p>
        <p><b>code:</b> {code}</p>
      </body>
    </html>
    """, subtype='html')

    with smtplib.SMTP(SMTP_SERVER, MAIL_PORT) as server:
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PWD)
        server.send_message(email)

    with sqlite3.connect(DB_PATH) as db:
        cur = db.execute("UPDATE users SET code = ? WHERE mail = ?", (code, mail))
        if cur.rowcount == 0:
            raise ValueError(f"Aucun utilisateur avec le mail {mail}")


def verifier_code(mail, saisi):
    with sqlite3.connect(DB_PATH) as db:
        row = db.execute("SELECT code FROM users WHERE mail = ?", (mail,)).fetchone()

        if row and row[0] is not None and secrets.compare_digest(row[0], saisi):
            db.execute("UPDATE users SET code = NULL WHERE mail = ?", (mail,))  # usage unique
            return True
        return False


if __name__ == "__main__":
    init_db()

    try:
        envoyer_code(MAIL_TO)
    except Exception as e:
        print(f"error : {e}")
        raise SystemExit(1)

    mail = input("mail : ")
    saisi = input("code : ")

    if verifier_code(mail, saisi):
        print("bon code")
    else:
        print("retry")