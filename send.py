import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()
MAIL_PWD = os.getenv('MAIL_PWD')
MAIL_FORM = os.getenv('MAIL_FORM')
MAIL_TO = os.getenv('MAIL_TO')
SMTP_SERVER = os.getenv('SMTP_SERVER')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PORT = os.getenv('MAIL_PORT')

# Créer un nouvel objet email
email = EmailMessage()

# Configurer les en-têtes de l'email
email['From'] = MAIL_FORM
email['To'] = MAIL_TO
email['Subject'] = 'Mail send by python'

# Ajouter le contenu HTML
html_content = """
<html>
  <body>
    <h1>Hi!</h1>
    <p>send <b>email</b> with <i>Python</i>.</p>
  </body>
</html>
"""
email.add_alternative(html_content, subtype='html')

# Connexion et envoi comme précédemment
smtp_server = SMTP_SERVER
port = MAIL_PORT
username = MAIL_USERNAME
password = MAIL_PWD

try:
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(email)
except Exception as e:
    print(f"error : {e}")