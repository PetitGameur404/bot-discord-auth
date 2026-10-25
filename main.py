import asyncio
import os
import secrets
import smtplib
import sqlite3
from email.message import EmailMessage

import discord
from discord.ext import commands
from discord import ui
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MAIL_PWD = os.getenv('MAIL_PWD')
MAIL_FORM = os.getenv('MAIL_FORM')
SMTP_SERVER = os.getenv('SMTP_SERVER')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PORT = int(os.getenv('MAIL_PORT'))
SETUP_CHANNEL = int(os.getenv('SETUP_CHANNEL'))

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
            raise ValueError(f"Any user with this mail {mail}")

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

def create_account(prenom, nom, mail):
    try:
        with sqlite3.connect(DB_PATH) as db:
            db.execute(
                "INSERT INTO users (prenom, nom, mail) VALUES (?, ?, ?)",
                (prenom, nom, mail),
            )
        return True
    except sqlite3.IntegrityError:
        return False


# class create_modal(ui.Modal, title="Create account"):
#     prenom = ui.Label(text='Name', component)

class Register_modal(ui.Modal, title='Questionnaire Response',):
    prenom = ui.Label(text='Name', component=ui.TextInput(placeholder = "Name"))
    nom = ui.Label(text='Lastname', component=ui.TextInput(placeholder = "Lastname"))
    mail = ui.Label(text='Mail', component=ui.TextInput(placeholder = "Mail"))


    async def on_submit(self, interaction: discord.Interaction):
        prenom = self.prenom.component.value
        nom = self.nom.component.value
        mail = self.mail.component.value

        if create_account(prenom, nom, mail):
            await interaction.response.send_message(f'Welcome, {self.prenom.component.value}! account create with succes use /login now', ephemeral=True)
        else:
            await interaction.response.send_message("Account already exists, use /login", ephemeral=True)


@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong ! Bot latency: **{round(bot.latency * 1000)}ms**")

@bot.tree.command(name="help", description="How to use bot")
async def help(interaction: discord.Interaction):
    embed=discord.Embed(title="YOU NEED HELP ! (this link of the official documentation)", url="https://tdoc-documentation.netlify.app/", description="dont stress i'm ready to help you", color=0xff79c6)
    embed.set_author(name="PetitGameur404", url="https://lucahallet.com", icon_url="https://media.discordapp.net/attachments/1318216081160015974/1563886806615855214/discord-avatar-petitgameur1.png?ex=6adf4296&is=6addf116&hm=e54d8ed43d4f41fd54b12e275c83829d1cea5226314114c9b4b62f55376b17cc&=&format=webp&quality=lossless")
    embed.add_field(name="/help", value="helps you understand what each command is used for", inline=True)
    embed.add_field(name="/ping", value="check the bot's ping and see if it's working", inline=True)
    embed.add_field(name="/setup", value="allows for sending an embed with a button that opens the account creation modal", inline=True)
    embed.add_field(name="/login", value="allows users to log in to their account", inline=True)
    embed.add_field(name="/verify", value="allows the user to enter the code sent via email for added security", inline=True)
    embed.add_field(name="/register", value="allows for account creation without using the modal, by doing it manually instead", inline=True)
    embed.set_image(url="https://images-ext-1.discordapp.net/external/JBXaMUJbwNe7xy-Lm_WmVSU5C32KHxu3VOzKoqLlDZE/https/i.pinimg.com/736x/97/62/ae/9762ae972a93213643d599e5cf76910a.jpg?format=webp")
    embed.set_footer(text="thank's for reading")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="login", description="Receive a code by mail")
async def login(interaction: discord.Interaction, mail: str):
    if not mail_existe(mail):
        await interaction.response.send_message("Sorry but your mail is not on list", ephemeral=Trktue)
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

@bot.tree.command(name="register", description="Create account")
async def register(interaction: discord.Interaction, prenom: str, nom: str, mail: str):
    if create_account(prenom, nom, mail):
        await interaction.response.send_message("Your account is create with succes ! use /login for login with your account", ephemeral=True)
    else:
        await interaction.response.send_message("Account already existe use /login", ephemeral=True)

@bot.hybrid_command(name="setup", description="Embed to open modal for register")
async def setup(ctx: commands.Context):
          button = discord.ui.Button(
              style = discord.ButtonStyle.primary,
              label = "create account !",
              emoji="➕",
              custom_id="create_account" 
              )

          async def button_callback(interaction: discord.Interaction):
              await interaction.response.send_modal(Register_modal())

          button.callback = button_callback

          view = discord.ui.View(timeout=None)
          view.add_item(button)
          
          embed=discord.Embed(title="Open an account now !", description="Welcom click on button to create your first account", color=0xff0000)
          embed.add_field(name="1", value="step 1: register", inline=False)
          embed.add_field(name="2", value="step 2: login", inline=False)
          embed.add_field(name="3", value="step 3: verify by code send to your mailbox", inline=False)
          channelSetup = bot.get_channel(SETUP_CHANNEL)
          await channelSetup.send(embed=embed, view=view)

          await ctx.send("Setup channel sent!", ephemeral=True)

# @bot.tree.command(name="modal", description="modal test")
# async def modal(interaction: discord.Interaction):
#     await interaction.response.send_modal(Questionnaire())


@bot.event
async def on_ready():
    activity = discord.CustomActivity(name="I verify !", emoji="â")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f'connect into {bot.user}')
    synced = await bot.tree.sync()
    print(f"{len(synced)} command(s) loaded")


init_db()
bot.run(DISCORD_TOKEN)