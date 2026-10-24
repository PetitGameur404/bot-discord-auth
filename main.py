import discord
from discord.ext import commands
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

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

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong !")

@bot.tree.command(name="login", description="verify if your mail is on list")
async def login(interaction: discord.Interaction, mail: str):
    if mail_existe(mail):
        role = interaction.guild.get_role(ROLE_ID)
        await interaction.user.add_roles(role)
        await interaction.response.send_message("Your mail is on list", ephemeral=True)
    else:
        await interaction.response.send_message("Sorry but your mail is not on liste", ephemeral=True)

@bot.tree.command(name="verify", description="But the code is send on your mailbox")
async def verify(interaction: discord.Interaction, mail: str):
    if mail_existe(mail):
        await interaction.response.send_message("A code has been sent to your mailbox", ephemeral=True)
    else:
        await interaction.response.send_message("Sorry but your mail is not on our database", ephemeral=True)

@bot.event
async def on_ready():
    activity = discord.CustomActivity(name="I verify !", emoji="â")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f'ConnectÃĐ en tant que {bot.user}')
    synced = await bot.tree.sync()
    print(f"{len(synced)} commande(s) synchronisees")

init_db()
bot.run(DISCORD_TOKEN)