# Intended for @on_message type commands, but I wasn't really using any of them
# So I decided to scrap the whole thing. Might add more later


import discord
from discord.ext import commands
from discord import app_commands

bigDict = {
    
}

class otherevents(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tree = bot.tree




async def setup(bot: commands.Bot):
    await bot.add_cog(otherevents(bot))