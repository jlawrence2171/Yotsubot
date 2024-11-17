import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Get the token from the environment
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Define intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize bot with intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Load user prefix and emote data
try:
    with open("prefixes.json", "r") as f:
        user_prefixes = json.load(f)
except FileNotFoundError:
    user_prefixes = {}

try:
    with open("emotes.json", "r") as f:
        user_emotes = json.load(f)
except FileNotFoundError:
    user_emotes = {}

# Helper function to save prefix data
def save_prefixes():
    with open("prefixes.json", "w") as f:
        json.dump(user_prefixes, f)

# Helper function to save emotes data
def save_emotes():
    with open("emotes.json", "w") as f:
        json.dump(user_emotes, f)

# Command to set a custom prefix for the user
@bot.command()
async def set_prefix(ctx, new_prefix: str):
    user_id = str(ctx.author.id)
    if new_prefix in user_prefixes.values():
        await ctx.send(f"Sorry, the prefix `{new_prefix}` is already in use by another user. Please choose a different one.")
    elif len(new_prefix) != 2:
        await ctx.send("Your prefix must be exactly 2 characters long. Please choose a different one.")
    else:
        user_prefixes[user_id] = new_prefix
        save_prefixes()
        await ctx.send(f"Your new prefix has been set to `{new_prefix}`!")

# Command to add a custom emote for a user with optional URL/code
@bot.command()
async def add_emote(ctx, emote_name: str, emote_code: str = None):
    user_id = str(ctx.author.id)
    if user_id not in user_emotes:
        user_emotes[user_id] = []
    emote_data = {"name": emote_name, "code": emote_code}
    if emote_data not in user_emotes[user_id]:
        user_emotes[user_id].append(emote_data)
        save_emotes()
        await ctx.send(f"Emote `{emote_name}` added for {ctx.author.display_name}!")
    else:
        await ctx.send(f"Emote `{emote_name}` is already saved for {ctx.author.display_name}.")

# Command to view saved emotes for a user
@bot.command()
async def view_emotes(ctx):
    user_id = str(ctx.author.id)
    if user_id in user_emotes:
        emotes = ', '.join([emote["name"] for emote in user_emotes[user_id]])
        await ctx.send(f"Your saved emotes: {emotes}")
    else:
        await ctx.send("You have no saved emotes.")

# Command to delete a custom emote for a user
@bot.command()
async def delete_emote(ctx, emote_name: str):
    user_id = str(ctx.author.id)
    if user_id in user_emotes:
        user_emotes[user_id] = [emote for emote in user_emotes[user_id] if emote["name"] != emote_name]
        save_emotes()
        await ctx.send(f"Emote `{emote_name}` deleted for {ctx.author.display_name}.")
    else:
        await ctx.send(f"Emote `{emote_name}` not found in your saved emotes.")

# Command to display an emote as an image (remove embed)
@bot.command()
async def emote(ctx, emote_name: str):
    user_id = str(ctx.author.id)
    if user_id in user_emotes:
        user_emote_list = [
            emote for emote in user_emotes[user_id] if isinstance(emote, dict) and "name" in emote and "code" in emote
        ]
        emote_data = next((emote for emote in user_emote_list if emote["name"] == emote_name), None)
        if emote_data:
            emote_code = emote_data["code"]
            if emote_code.startswith("http"):
                await ctx.send(emote_code)
            else:
                await ctx.send(emote_code)
        else:
            await ctx.send(f"Emote `{emote_name}` not found in your saved emotes.")
    else:
        await ctx.send("You have no saved emotes.")

# Run the bot
bot.run(TOKEN)
