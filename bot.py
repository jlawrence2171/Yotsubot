import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from commands import setup_commands
from utils import load_json, save_json

# Load environment variables
load_dotenv()

# Bot token from .env file
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Define bot intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Data file paths
PREFIX_FILE = "prefixes.json"
EMOTE_FILE = "emotes.json"

# Load persistent data
user_prefixes = load_json(PREFIX_FILE)
user_emotes = load_json(EMOTE_FILE)

# Save functions
def save_prefixes():
    save_json(PREFIX_FILE, user_prefixes)

def save_emotes():
    save_json(EMOTE_FILE, user_emotes)

# Set up commands and pass shared variables
setup_commands(bot, user_prefixes, user_emotes, save_prefixes, save_emotes)

# Event listener for direct emote calls
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_id = str(message.author.id)
    prefix = user_prefixes.get(user_id)

    if prefix and message.content.startswith(prefix):
        emote_name = message.content[len(prefix):].strip()
        user_emotes_list = user_emotes.get(user_id, [])

        emote_data = next((emote for emote in user_emotes_list if emote["name"] == f"{prefix}{emote_name}"), None)

        if emote_data:
            emote_code = emote_data["code"]
            if emote_code.startswith("http"):
                await message.channel.send(emote_code)
            else:
                await message.channel.send(emote_code)
        else:
            await message.channel.send(f"Emote `{emote_name}` not found under your prefix `{prefix}`.")

    await bot.process_commands(message)

# Run the bot
bot.run(TOKEN)
