import discord
from discord.ext import commands
import os
import json
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

with open('db.json', 'r') as user:
    users = json.load(user)

liste = users["utilisateurs"]



@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong !")

@bot.tree.command(name="login", description="verify if your mail is on list")
async def verify(interaction: discord.Interaction, mail: str):
    find = False
    for user in liste:
       if mail == user["mail"]:
        find = True
        break
    if find:
        role = interaction.guild.get_role(1562441324555149424)
        await interaction.user.add_roles(role)
        await interaction.response.send_message("Your mail is on list", ephemeral=True) 
    else:
        await interaction.response.send_message("Sorry but your mail is not on liste", ephemeral=True)

@bot.tree.command(name="verify", description="But the code is send on your mailbox")
async def verify(interaction: discord.Interaction, mail: str):
    find = False
    for user in liste:
       if mail == user["mail"]:
        find = True
        break
    if find:
        role = interaction.guild.get_role(1562441324555149424)
        await interaction.user.add_roles(role)
        await interaction.response.send_message("Your mail is on list", ephemeral=True) 
    else:
        await interaction.response.send_message("Sorry but your mail is not on liste", ephemeral=True)


@bot.event
async def on_ready():
    activity = discord.CustomActivity(name="I verify !", emoji="✅")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f'Connecté en tant que {bot.user}')
    synced = await bot.tree.sync()
    print(f"{len(synced)} commande(s) synchronisees")

bot.run(DISCORD_TOKEN)