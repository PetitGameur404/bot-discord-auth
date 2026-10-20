import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong !")





@bot.event
async def on_ready():
    activity = discord.CustomActivity(name="I verify !", emoji="1557444301116542986​")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f'Connecté en tant que {bot.user}')
    synced = await bot.tree.sync()
    print(f"{len(synced)} commande(s) synchronisees")

bot.run(DISCORD_TOKEN)