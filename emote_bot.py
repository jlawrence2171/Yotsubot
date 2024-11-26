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

# Helper functions
def save_prefixes():
    with open("prefixes.json", "w") as f:
        json.dump(user_prefixes, f)

def save_emotes():
    with open("emotes.json", "w") as f:
        json.dump(user_emotes, f)

def get_user_prefix(user_id):
    return user_prefixes.get(user_id)

# Decorator to ensure a user has a prefix
def requires_prefix(func):
    async def wrapper(ctx, *args, **kwargs):
        user_id = str(ctx.author.id)
        prefix = get_user_prefix(user_id)
        if not prefix:
            await ctx.send("You must set a prefix using `!set_prefix` before managing emotes.")
            return
        await func(ctx, *args, **kwargs)
    return wrapper

# Command to set a custom prefix for the user
@bot.command()
async def set_prefix(ctx, new_prefix: str):
    user_id = str(ctx.author.id)
    if len(new_prefix) != 2:
        await ctx.send("Your prefix must be exactly 2 characters long. Please choose a different one.")
    elif new_prefix in user_prefixes.values() and user_prefixes.get(user_id) != new_prefix:
        await ctx.send(f"Sorry, the prefix `{new_prefix}` is already in use by another user.")
    else:
        user_prefixes[user_id] = new_prefix
        save_prefixes()
        await ctx.send(f"Your new prefix has been set to `{new_prefix}`!")

# Command to add a custom emote for a user with optional URL/code
@bot.command()
@requires_prefix
async def add_emote(ctx, emote_name: str, emote_code: str = None):
    user_id = str(ctx.author.id)
    prefix = get_user_prefix(user_id)
    if user_id not in user_emotes:
        user_emotes[user_id] = []

    full_emote_name = f"{prefix}:{emote_name}"
    emote_data = {"name": full_emote_name, "code": emote_code}

    if emote_data not in user_emotes[user_id]:
        user_emotes[user_id].append(emote_data)
        save_emotes()
        await ctx.send(f"Emote `{full_emote_name}` added for {ctx.author.display_name}!")
    else:
        await ctx.send(f"Emote `{full_emote_name}` is already saved for {ctx.author.display_name}.")

# Command to delete a custom emote for a user
@bot.command()
@requires_prefix
async def delete_emote(ctx, emote_name: str):
    user_id = str(ctx.author.id)
    prefix = get_user_prefix(user_id)

    if user_id in user_emotes:
        full_emote_name = f"{prefix}:{emote_name}"
        emote_to_delete = next((emote for emote in user_emotes[user_id] if emote["name"] == full_emote_name), None)

        if emote_to_delete:
            user_emotes[user_id].remove(emote_to_delete)
            save_emotes()
            await ctx.send(f"Emote `{full_emote_name}` deleted for {ctx.author.display_name}.")
        else:
            await ctx.send(f"Emote `{full_emote_name}` not found in your saved emotes.")
    else:
        await ctx.send("You have no saved emotes to delete.")

# Command to display an emote as an image (remove embed)
@bot.command()
@requires_prefix
async def emote(ctx, emote_name: str):
    user_id = str(ctx.author.id)
    prefix = get_user_prefix(user_id)
    full_emote_name = f"{prefix}:{emote_name}"

    if user_id in user_emotes:
        emote_data = next((emote for emote in user_emotes[user_id] if emote["name"] == full_emote_name), None)
        if emote_data:
            emote_code = emote_data["code"]
            if emote_code.startswith("http"):
                await ctx.send(emote_code)
            else:
                await ctx.send(emote_code)
        else:
            await ctx.send(f"Emote `{full_emote_name}` not found.")
    else:
        await ctx.send("You have no saved emotes.")

# Command to view saved emotes for a user
@bot.command()
@requires_prefix
async def view_emotes(ctx):
    user_id = str(ctx.author.id)
    prefix = get_user_prefix(user_id)
    if user_id in user_emotes:
        emotes = [emote["name"] for emote in user_emotes[user_id] if emote["name"].startswith(f"{prefix}:")]
        emote_list = ', '.join(emotes)
        await ctx.send(f"Your saved emotes: {emote_list}" if emote_list else "You have no saved emotes.")
    else:
        await ctx.send("You have no saved emotes.")

# Run the bot
bot.run(TOKEN)