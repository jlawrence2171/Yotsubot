from discord.ext import commands
from functools import wraps

def setup_commands(bot, user_prefixes, user_emotes, save_prefixes, save_emotes):
    def requires_prefix(func):
        @wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            user_id = str(ctx.author.id)
            prefix = user_prefixes.get(user_id)
            if not prefix:
                await ctx.send("You must set a prefix using `!set_custom_prefix` before managing emotes.")
                return
            await func(ctx, *args, **kwargs)
        return wrapper

    @commands.command()
    async def set_custom_prefix(ctx, new_prefix: str):
        user_id = str(ctx.author.id)
        if len(new_prefix) != 2:
            await ctx.send("Your prefix must be exactly 2 characters long. Please choose a different one.")
        elif new_prefix in user_prefixes.values() and user_prefixes.get(user_id) != new_prefix:
            await ctx.send(f"Sorry, the prefix `{new_prefix}` is already in use by another user.")
        else:
            user_prefixes[user_id] = new_prefix
            save_prefixes()
            await ctx.send(f"Your new prefix has been set to `{new_prefix}`!")

    @commands.command()
    @requires_prefix
    async def add_custom_emote(ctx, emote_name: str, emote_code: str = None):
        user_id = str(ctx.author.id)
        prefix = user_prefixes.get(user_id)
        if user_id not in user_emotes:
            user_emotes[user_id] = []

        full_emote_name = f"{prefix}{emote_name}"
        emote_data = {"name": full_emote_name, "code": emote_code}

        if emote_data not in user_emotes[user_id]:
            user_emotes[user_id].append(emote_data)
            save_emotes()
            await ctx.send(f"Emote `{full_emote_name}` added for {ctx.author.display_name}!")
        else:
            await ctx.send(f"Emote `{full_emote_name}` is already saved for {ctx.author.display_name}.")

    @commands.command()
    @requires_prefix
    async def delete_custom_emote(ctx, emote_name: str):
        user_id = str(ctx.author.id)
        prefix = user_prefixes.get(user_id)

        if user_id in user_emotes:
            full_emote_name = f"{prefix}{emote_name}"
            emote_to_delete = next((emote for emote in user_emotes[user_id] if emote["name"] == full_emote_name), None)

            if emote_to_delete:
                user_emotes[user_id].remove(emote_to_delete)
                save_emotes()
                await ctx.send(f"Emote `{full_emote_name}` deleted for {ctx.author.display_name}.")
            else:
                await ctx.send(f"Emote `{full_emote_name}` not found in your saved emotes.")
        else:
            await ctx.send("You have no saved emotes to delete.")

    @commands.command(name="list_emotes")
    async def list_emotes(ctx):
        user_id = str(ctx.author.id)
        prefix = user_prefixes.get(user_id, None)
        if not prefix:
            await ctx.send("You must set a prefix using `!set_custom_prefix` before managing emotes.")
            return

        if user_id in user_emotes and user_emotes[user_id]:
            emotes = [emote["name"] for emote in user_emotes[user_id] if emote["name"].startswith(prefix)]
            emote_list = "\n".join(emotes)
            if emote_list:
                await ctx.send(f"Your saved emotes:\n```\n{emote_list}\n```")
            else:
                await ctx.send("You have no saved emotes under your prefix.")
        else:
            await ctx.send("You have no saved emotes.")

    # Register commands with the bot
    bot.add_command(set_custom_prefix)
    bot.add_command(add_custom_emote)
    bot.add_command(delete_custom_emote)
    bot.add_command(list_emotes)
