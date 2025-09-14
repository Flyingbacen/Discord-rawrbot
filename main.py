import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="!", intents=intents) # prefix is unused, but still needed afaik
# tree = app_commands.CommandTree(client)


config_path = os.path.join(os.path.dirname(__file__), "config.json")
with open(config_path) as config_file:
    config_items = json.load(config_file)


@client.event
async def on_ready():
    # await client.tree.sync()
    activity = discord.Activity(type=discord.ActivityType.listening, name="your commands")
    await client.change_presence(activity=activity, status=discord.Status.idle)
    print("Ready!")


async def load_cogs():
    cogs = [
        "cogs.general",
        "cogs.moderation",
        "cogs.music",
        "cogs.utility"
    ]
    for cog in cogs:
        await client.load_extension(cog)

if __name__ == "__main__":
    import asyncio
    asyncio.run(load_cogs())
    client.run(config_items["token"])