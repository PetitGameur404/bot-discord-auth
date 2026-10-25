import asyncio
import os
import secrets
import smtplib
import sqlite3
from datetime import datetime, timezone
from email.message import EmailMessage

import discord
from discord import app_commands, ui
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MAIL_PWD = os.getenv('MAIL_PWD')
MAIL_FORM = os.getenv('MAIL_FORM')
SMTP_SERVER = os.getenv('SMTP_SERVER')
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PORT = int(os.getenv('MAIL_PORT'))
SETUP_CHANNEL = int(os.getenv('SETUP_CHANNEL'))
ADMIN_CHANNEL = int(os.getenv('ADMIN_CHANNEL'))

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

DB_PATH = "db.db"
ROLE_ID = 1562441324555149424


def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            mail TEXT UNIQUE NOT NULL,
            code TEXT,
            guild_id INTEGER,
            created_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
        """)
        cols = [row[1] for row in db.execute("PRAGMA table_info(users)")]
        if "guild_id" not in cols:
            db.execute("ALTER TABLE users ADD COLUMN guild_id INTEGER")


def mail_existe(mail: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("SELECT 1 FROM users WHERE mail = ? LIMIT 1", (mail,))
        return cur.fetchone() is not None


def send_code(mail: str):
    code = f"{secrets.randbelow(1000000):06d}"

    with sqlite3.connect(DB_PATH) as db:
        cur = db.execute("UPDATE users SET code = ? WHERE mail = ?", (code, mail))
        if cur.rowcount == 0:
            raise ValueError(f"No user with this mail: {mail}")

    email = EmailMessage()
    email['From'] = MAIL_FORM
    email['To'] = mail
    email['Subject'] = 'Verification code'
    email.set_content(f"Your verification code is: {code}")
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


def verify_code(mail: str, saisi: str) -> bool:
    with sqlite3.connect(DB_PATH) as db:
        row = db.execute("SELECT code FROM users WHERE mail = ?", (mail,)).fetchone()

        if row and row[0] is not None and secrets.compare_digest(row[0], saisi):
            db.execute("UPDATE users SET code = NULL WHERE mail = ?", (mail,))
            return True
        return False

def create_account(name: str, last_name: str, mail: str, guild_id: int) -> bool:
    try:
        with sqlite3.connect(DB_PATH) as db:
            db.execute(
                "INSERT INTO users (name, last_name, mail, guild_id) VALUES (?, ?, ?, ?)",
                (name, last_name, mail, guild_id),
            )
        return True
    except sqlite3.IntegrityError:
        return False

def delete_account(mail: str, guild_id: int) -> bool:
    with sqlite3.connect(DB_PATH) as db:
        cur = db.execute(
            "DELETE FROM users WHERE mail = ? AND guild_id = ?",
            (mail, guild_id),
        )
        return cur.rowcount > 0


def list_accounts(guild_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT name, last_name, mail, created_at FROM users WHERE guild_id = ? ORDER BY created_at DESC",
            (guild_id,),
        )
        return cur.fetchall()

def total_accounts(guild_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "SELECT COUNT(*) FROM users WHERE guild_id = ?",
            (guild_id,),
        )
        return cur.fetchall()[0]


async def give_role(interaction: discord.Interaction) -> bool:
    role = interaction.guild.get_role(ROLE_ID)
    if role is None:
        return False
    await interaction.user.add_roles(role)
    return True


async def do_login(interaction: discord.Interaction, mail: str):
    mail = mail.strip().lower()
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


async def do_verify(interaction: discord.Interaction, mail: str, code: str):
    mail = mail.strip().lower()
    code = code.strip()

    if not verify_code(mail, code):
        await interaction.response.send_message("Wrong code", ephemeral=True)
        return

    if not await give_role(interaction):
        await interaction.response.send_message("Verified, but the role was not found. Contact an admin.", ephemeral=True)
        return

    await interaction.response.send_message("Welcome, login successful!", ephemeral=True)


async def do_register(interaction: discord.Interaction, name: str, last_name: str, mail: str):
    name = name.strip()
    last_name = last_name.strip()
    mail = mail.strip().lower()

    if "@" not in mail or "." not in mail:
        await interaction.response.send_message("Invalid mail address", ephemeral=True)
        return

    if create_account(name, last_name, mail, interaction.guild_id):
        await interaction.response.send_message(
            f"Welcome, {name}! Account created, you can now login.", ephemeral=True
        )
    else:
        await interaction.response.send_message("Account already exists, use Login.", ephemeral=True)


class RegisterModal(ui.Modal, title='Create account'):
    name = ui.Label(text='Name', component=ui.TextInput(placeholder="Name", max_length=50))
    last_name = ui.Label(text='Lastname', component=ui.TextInput(placeholder="Lastname", max_length=50))
    mail = ui.Label(text='Mail', component=ui.TextInput(placeholder="Mail", max_length=100))

    async def on_submit(self, interaction: discord.Interaction):
        await do_register(
            interaction,
            self.name.component.value,
            self.last_name.component.value,
            self.mail.component.value,
        )


class LoginModal(ui.Modal, title='Get a code'):
    mail = ui.Label(text='Mail', component=ui.TextInput(placeholder="Mail", max_length=100))

    async def on_submit(self, interaction: discord.Interaction):
        await do_login(interaction, self.mail.component.value)


class VerifyModal(ui.Modal, title='Enter your code'):
    mail = ui.Label(text='Mail', component=ui.TextInput(placeholder="Mail", max_length=100))
    code = ui.Label(text='Code', component=ui.TextInput(placeholder="6-digit code", min_length=6, max_length=6))

    async def on_submit(self, interaction: discord.Interaction):
        await do_verify(interaction, self.mail.component.value, self.code.component.value)


class DeleteModal(ui.Modal, title='Delete account'):
    mail = ui.Label(text='Mail', component=ui.TextInput(placeholder="Mail of the account", max_length=100))

    async def on_submit(self, interaction: discord.Interaction):
        mail = self.mail.component.value.strip().lower()
        if delete_account(mail, interaction.guild_id):
            await interaction.response.send_message(f"Account `{mail}` deleted.", ephemeral=True)
        else:
            await interaction.response.send_message("No account found with this mail.", ephemeral=True)


class SetupView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Create account", emoji="\u2795", style=discord.ButtonStyle.primary, custom_id="create_account")
    async def register_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(RegisterModal())

    @ui.button(label="Login", emoji="\U0001F4E7", style=discord.ButtonStyle.primary, custom_id="login_account")
    async def login_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(LoginModal())

    @ui.button(label="Verify", emoji="\u2705", style=discord.ButtonStyle.success, custom_id="verify_account")
    async def verify_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(VerifyModal())


class AdminView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Admins only.", ephemeral=True)
            return False
        return True

    @ui.button(label="List accounts", emoji="\U0001F4CB", style=discord.ButtonStyle.secondary, custom_id="admin_list")
    async def list_button(self, interaction: discord.Interaction, button: ui.Button):
        accounts = list_accounts(interaction.guild_id)

        if not accounts:
            await interaction.response.send_message("No accounts on this server.", ephemeral=True)
            return

        lines = [f"**{name} {last_name}** - {mail}" for name, last_name, mail, _ in accounts]

        embed = discord.Embed(
            title=f"Accounts ({len(accounts)})",
            description="\n".join(lines)[:4000],
            color=0x5865F2,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @ui.button(label="Total accounts", emoji="\U0001F4CB", style=discord.ButtonStyle.secondary, custom_id="admin_total")
    async def total_button(self, interaction: discord.Interaction, button: ui.Button):
        total = total_accounts(interaction.guild_id)

        if total == 0:
            await interaction.response.send_message("No accounts on this server.", ephemeral=True)
            return

        embed = discord.Embed(
            title="Accounts registered",
            description=f"Total: **{total}**",
            color=0x5865F2,
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label="Create account", emoji="\u2795", style=discord.ButtonStyle.primary, custom_id="admin_create")
    async def create_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(RegisterModal())

    @ui.button(label="Delete account", emoji="\U0001F5D1", style=discord.ButtonStyle.danger, custom_id="admin_delete")
    async def delete_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(DeleteModal())


@bot.tree.command(name="ping", description="Check the bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong ! Bot latency: **{round(bot.latency * 1000)}ms**")


@bot.tree.command(name="help", description="How to use bot")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="YOU NEED HELP ! (link to the official documentation)",
        url="https://tdoc-documentation.netlify.app/",
        description="Don't stress, I'm ready to help you",
        color=0xff79c6,
    )
    embed.set_author(
        name="PetitGameur404",
        url="https://lucahallet.com",
        icon_url="https://media.discordapp.net/attachments/1318216081160015974/1563886806615855214/discord-avatar-petitgameur1.png?ex=6adf4296&is=6addf116&hm=e54d8ed43d4f41fd54b12e275c83829d1cea5226314114c9b4b62f55376b17cc&=&format=webp&quality=lossless",
    )
    embed.add_field(name="/help", value="Explains what each command does", inline=True)
    embed.add_field(name="/ping", value="Checks the bot's latency", inline=True)
    embed.add_field(name="/setup", value="Sends an embed with buttons for register, login and verify", inline=True)
    embed.add_field(name="/admin-panel", value="Sends the admin panel to manage accounts", inline=True)
    embed.set_image(url="https://images-ext-1.discordapp.net/external/JBXaMUJbwNe7xy-Lm_WmVSU5C32KHxu3VOzKoqLlDZE/https/i.pinimg.com/736x/97/62/ae/9762ae972a93213643d599e5cf76910a.jpg?format=webp")
    embed.set_footer(text="Thanks for reading")
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="setup", description="Send the verification embed in the setup channel")
@app_commands.default_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Open an account now !",
        description="Welcome! Click on the buttons below.",
        color=0xff0000,
    )
    embed.add_field(name="1", value="Step 1: register", inline=False)
    embed.add_field(name="2", value="Step 2: login", inline=False)
    embed.add_field(name="3", value="Step 3: verify with the code sent to your mailbox", inline=False)

    channel = bot.get_channel(SETUP_CHANNEL)
    if channel is None:
        await interaction.response.send_message("SETUP_CHANNEL is invalid, check your .env", ephemeral=True)
        return

    await channel.send(embed=embed, view=SetupView())
    await interaction.response.send_message("Setup message sent!", ephemeral=True)


@bot.tree.command(name="admin-panel", description="Send admin panel")
@app_commands.default_permissions(administrator=True)
async def admin_panel(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Welcome to Admin Panel",
        description="You can manage the bot.",
        colour=0x00b0f4,
        timestamp=datetime.now(timezone.utc),
    )
    embed.set_author(name="Dracula Auth")
    embed.add_field(name="List accounts", value="See all user accounts", inline=True)
    embed.add_field(name="Create account", value="Create an account manually", inline=True)
    embed.add_field(name="Delete account", value="Delete a user account", inline=True)
    embed.set_image(url="https://media.discordapp.net/attachments/1318216081160015974/1563917918654169088/banniere-dracula-auth.png?ex=6adf5f8f&is=6ade0e0f&hm=dcffbc96c95aee93c66efde8512920c62fea688128f4fdc9621baaade9fe3c87&=&format=webp&quality=lossless&width=2048&height=683")
    embed.set_footer(
        text="Dracula Auth by PetitGameur404",
        icon_url="https://media.discordapp.net/attachments/1318216081160015974/1563914149052817408/a363495a-ecec-43c7-aaed-fc6ab91c291e.png?ex=6adf5c0d&is=6ade0a8d&hm=870579e4aa502a7c4fe051174e2db37d869a07f5bb942b9fea514a44ddcfd646&=&format=webp&quality=lossless",
    )

    channel = bot.get_channel(ADMIN_CHANNEL)
    if channel is None:
        await interaction.response.send_message("ADMIN_CHANNEL is invalid, check your .env", ephemeral=True)
        return

    await channel.send(embed=embed, view=AdminView())
    await interaction.response.send_message("Admin Panel sent!", ephemeral=True)


@bot.event
async def setup_hook():
    bot.add_view(SetupView())
    bot.add_view(AdminView())


@bot.event
async def on_ready():
    activity = discord.CustomActivity(name="I verify !", emoji="\u2705")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f'connect into {bot.user}')
    synced = await bot.tree.sync()
    print(f"{len(synced)} command(s) loaded")

init_db()
bot.run(DISCORD_TOKEN)