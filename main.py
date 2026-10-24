import asyncio
import os
import secrets
import smtplib
import sqlite3
from email.message import EmailMessage

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MAIL_PWD = os.getenv('MAIL_PWD')
MAIL_FORM = os.getenv('MAIL_FORM')
SMTP_SERVER = os.getenv('SMTP_SERVER')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PORT = int(os.getenv('MAIL_PORT'))

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

DB_PATH = "db.db"
ROLE_ID = 1562441324555149424


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
        db.execute(
            "INSERT OR IGNORE INTO users (prenom, nom, mail) VALUES (?, ?, ?)",
            ("Jean", "Daniel", "jean@gmail.com"),
        )


def mail_existe(mail: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT 1 FROM users WHERE mail = ? LIMIT 1",
            (mail,)
        )
        return cur.fetchone() is not None


def send_code(mail):
    code = f"{secrets.randbelow(1000000):06d}"

    with sqlite3.connect(DB_PATH) as db:
        cur = db.execute("UPDATE users SET code = ? WHERE mail = ?", (code, mail))
        if cur.rowcount == 0:
            raise ValueError(f"Aucun utilisateur avec le mail {mail}")

    email = EmailMessage()
    email['From'] = MAIL_FORM
    email['To'] = mail
    email['Subject'] = 'Verification code'
    email.add_alternative(f"""
    <html>
      <body>
        <h1>Hi!</h1>
        <p>This is your <b>code</b> for <i>connect</i>.</p>
        <p><b>code:</b> {code}</p>
      </body>
    </html>
    """, subtype='html')

    with smtplib.SMTP(SMTP_SERVER, MAIL_PORT) as server:
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PWD)
        server.send_message(email)


def verify_code(mail, saisi):
    with sqlite3.connect(DB_PATH) as db:
        row = db.execute("SELECT code FROM users WHERE mail = ?", (mail,)).fetchone()

        if row and row[0] is not None and secrets.compare_digest(row[0], saisi):
            db.execute("UPDATE users SET code = NULL WHERE mail = ?", (mail,))
            return True
        return False


@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong !")


@bot.tree.command(name="login", description="Receive a code by mail")
async def login(interaction: discord.Interaction, mail: str):
    if not mail_existe(mail):
        await interaction.response.send_message("Sorry but your mail is not on list", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    try:
        await asyncio.to_thread(send_code, mail)
    except Exception as e:
        print(f"Error send mail: {e}")
        await interaction.followup.send("Error while sending the mail", ephemeral=True)
        return

    await interaction.followup.send("A code has been sent to your mailbox", ephemeral=True)


@bot.tree.command(name="verify", description="Enter the code received by mail")
async def verify(interaction: discord.Interaction, mail: str, saisi: str):
    if verify_code(mail, saisi):
        role = interaction.guild.get_role(ROLE_ID)
        await interaction.user.add_roles(role)
        await interaction.response.send_message("Welcome, login successful!", ephemeral=True)
    else:
        await interaction.response.send_message("Wrong code", ephemeral=True)


@bot.event
async def on_ready():
    activity = discord.CustomActivity(name="I verify !", emoji="â")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f'connect into {bot.user}')
    synced = await bot.tree.sync()
    print(f"{len(synced)} command(s) loaded")


init_db()
bot.run(DISCORD_TOKEN)