import discord
from discord.ext import commands
from discord import app_commands
from typing import Any
import time
import asyncio

bigDict: dict[str, dict[Any, Any]] = {
    "ping": {
        "name": "ping",
        "description": "hopefully counts to a low number :)",
        "nsfw": False,
        "auto_locale_strings": True,
        "extras": {

        }
    },
    "hello": {
        "name": "hello",
        "description": "I would love to talk to you more, but perhaps a simple hello will suffice",
        "nsfw": False,
        "auto_locale_strings": True,
        "extras": {
            
        }
    },
    "invite": {
        "name": "invite",
        "description": "invite the bot to your server! (perms are not properly set up for this version of the bot)",
        "nsfw": False,
        "auto_locale_strings": True,
        "extras": {
            
        }
    },
    "pop": {
        "name": "pop",
        "description": "goes the weasel!",
        "nsfw": False,
        "auto_locale_strings": True,
        "extras": {
            
        }
    },
    "sync": {
        "name": "sync",
        "description": "...",
        "nsfw": False,
        "auto_locale_strings": True,
        "extras": {
            "allowedUsers": [
                717471432816459840
            ]
        }
    },

}

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tree = bot.tree


    @app_commands.allowed_contexts(True, True, True)
    @app_commands.allowed_installs(True, True)
    @app_commands.command(**bigDict["ping"])
    async def ping(self, interaction: discord.Interaction):
        start_time = time.time()
        latency = interaction.client.latency
        await interaction.response.send_message(f"Pong! | Latency: {round(interaction.client.latency * 1000, 2)} ms")
        latency = round((time.time() - start_time) * 1000, 2)
        await interaction.edit_original_response(content=f"Pong! | Latency: {round(interaction.client.latency * 1000, 2)} ms | Message Latency: {latency} ms")


    @app_commands.allowed_contexts(True, True, True)
    @app_commands.allowed_installs(True, True)
    @app_commands.command(**bigDict["hello"])
    async def hello(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Hello {interaction.user.display_name}! I hope you're doing good :)")
        

    @app_commands.allowed_contexts(True, True, True)
    @app_commands.allowed_installs(True, True)
    @app_commands.command(**bigDict["pop"])
    async def pop(self, interaction: discord.Interaction):
        await interaction.response.send_message("*pop*\nFun fact, did you know balloons make this noise only once?\n" + ("||I bet I can make that noise with you multiple times, *if you know what I mean 🤭*||" if interaction.guild is None else "")) # If there isn't a guild, we're in a (Group)/DM
        print(f"Having some fun w/ {interaction.user.name}, hehe")
        

    @app_commands.allowed_contexts(True, True, True)
    @app_commands.allowed_installs(True, True)
    @app_commands.command(**bigDict["invite"])
    async def invite(self, interaction: discord.Interaction):
        """Generates a bot invite link."""
        link = "[invite link](https://discord.com/oauth2/authorize?client_id=1118629362368008283&permissions=2147486720&scope=bot&permissions=2147486720&scope=messages.read%20bot)"
        message = await interaction.response.send_message(link)
        channelID = message.id
        channelCache = self.bot.get_channel(channelID)
        
        if isinstance(channelCache, discord.TextChannel):
            channelName = channelCache.name
            serverName = channelCache.guild.name if channelCache.guild else "unknown server"
        elif isinstance(channelCache, discord.DMChannel):
            channelName = "DM"
            serverName = channelCache.recipients[0].name
        elif isinstance(channelCache, discord.GroupChannel):
            channelName = "Group DM"
            serverName = ((user.name + ", ") for user in channelCache.recipients)
        else:
            channelName = "unknown"
            serverName = "unknown"

        print(f"sent bot invite to MessageID: {channelID} in {channelName} (server/DM User: {serverName})")
        

    @app_commands.allowed_contexts(True, True, True)
    @app_commands.allowed_installs(False, True)
    @app_commands.command(**bigDict["sync"])
    async def sync(self, interaction: discord.Interaction):
        if interaction.user.id in bigDict["sync"]["extras"]["allowedUsers"]:
            await interaction.response.defer()
            await self.tree.sync()
            await interaction.followup.send("Commands synced successfully.")
            print("Synced commands")
            await asyncio.sleep(10)
            await interaction.delete_original_response()
            return
        else:
            await interaction.response.send_message("Missing perms")
            print("[missing perms] failed to sync commands")
            await asyncio.sleep(5)
            await interaction.delete_original_response()
        

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))