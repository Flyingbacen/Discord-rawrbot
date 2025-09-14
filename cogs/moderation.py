import datetime
import discord
from discord.ext import commands
from discord import app_commands
import asyncio

bigDict = {
    "ban_list": {
        "name": "ban_list",
        "description": "Gives a list of banned users in the server and the reason",
        "nsfw": False,
        "auto_locale_strings": True,
        "extras": {
            
        }
    },
    "mute": {
        "name": "mute",
        "description": "Mutes a user (Optionally for `time` seconds)",
        "nsfw": False,
        "auto_locale_strings": True,
        "extras": {
            
        }
    },
    "deafen": {
        "name": "deafen",
        "description": "Deafens a user (Optionally for `time` seconds)",
        "nsfw": False,
        "auto_locale_strings": True,
        "extras": {
            
        }
    },
    "timeout": {
        "name": "timeout",
        "description": "Times out a user for `duration` seconds",
        "nsfw": False,
        "auto_locale_strings": True,
        "extras": {
            
        }
    },
    "move_user": {
        "name": "move_user",
        "description": "Moves a user from one VC to another",
        "nsfw": False,
        "auto_locale_strings": True,
        "extras": {
            
        }
    },
    "move_voicechannel": {
        "name": "move_voicechannel",
        "description": "Moves all users in a voice channel to another",
        "nsfw": False,
        "auto_locale_strings": True,
        "extras": {
            
        }
    },
}

class moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tree = bot.tree


    @app_commands.allowed_contexts(True, False, False)
    @app_commands.allowed_installs(True, False)
    @app_commands.command(**bigDict["ban_list"])
    async def ban_list(self, interaction: discord.Interaction):
        """gives list of bans in server"""
        await interaction.response.defer()
        badaaa = ""
        if interaction.guild:
            bans = [entry async for entry in interaction.guild.bans()]
        else:
            return # This shouldn't be able to happen, but pylance is weird
        for BanEntry in bans:
            user = BanEntry.user.global_name
            reason = BanEntry.reason
            badaaa += f"User: {user}\nReason: {reason}\n\n"
        badaaa += "\n\n note: users titled \"none\" have since been deleted since they were banned."
        await interaction.followup.send(badaaa)
        if badaaa == "\n\n note: users titled \"none\" have since been deleted since they were banned.":
            await interaction.followup.send("No people have been banned in this server")
        print(bans)


    @app_commands.describe(
        voice_channel="The voice channel to (un)mute the user in",
        user="The user to (un)mute",
        mute="Whether to mute or unmute the user",
        time="The time to mute the user for, default is 5, set to 0 to disable. Only used when muting"
    )
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.allowed_installs(True, False)
    @app_commands.command(**bigDict["mute"])
    async def mute(self, interaction: discord.Interaction, voice_channel: discord.VoiceChannel, user: discord.Member, mute: bool, time: int = 5):
        """Mutes a user"""
        
        tempMember = next((e for e in voice_channel.members if e.id == user.id), None)
        if tempMember is None:
            await interaction.followup.send(f"{user.display_name} is not in the voice channel")
            return
        else:
            await interaction.response.defer(ephemeral=True)
            await tempMember.edit(mute=mute)
            if time != 0 and mute:
                mutingmessage = await interaction.followup.send(f"{'Muted' if mute else 'Unmuted'} {user.display_name} for {time} seconds", wait=True)
                await asyncio.sleep(time)
                await tempMember.edit(mute=False)
                await interaction.followup.edit_message(mutingmessage.id, content = f"Unmuted {user.mention} after {time} seconds")
            else:
                await interaction.followup.send(f"{'Muted' if mute else 'Unmuted'} {user.display_name}")


    @app_commands.describe(
        voice_channel="The voice channel to (un)deafen the user in",
        user="The user to (un)deafen",
        deafen="Whether to deafen or undeafen the user",
        time="The time to deafen the user for, default is 5, set to 0 to disable. Only used when deafening"
    )
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.allowed_installs(True, False)
    @app_commands.command(**bigDict["deafen"])
    async def deafen(self, interaction: discord.Interaction, voice_channel: discord.VoiceChannel, user: discord.Member, deafen: bool, time: int = 5):
        """Deafens a user"""
            
        tempMember = next((e for e in voice_channel.members if e.id == user.id), None)
        if tempMember is None:
            await interaction.followup.send(f"{user.display_name} is not in the voice channel")
            return
        else:
            await interaction.response.defer(ephemeral=True)
            await tempMember.edit(deafen=deafen)
            if time != 0 and deafen:
                deafeningmessage = await interaction.followup.send(f"{'Deafened' if deafen else 'Undeafened'} {user.display_name} for {time} seconds", wait=True)
                await asyncio.sleep(time)
                await tempMember.edit(deafen=False)
                await interaction.followup.edit_message(deafeningmessage.id, content = f"Undeafened {user.mention} after {time} seconds")
            else:
                await interaction.followup.send(f"{'Deafened' if deafen else 'Undeafened'} {user.display_name}")


    @app_commands.describe(
        user="The user to timeout",
        duration="The duration of the timeout in seconds"
    )
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.allowed_installs(True, False)
    @app_commands.command(**bigDict["timeout"])
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, duration: int = 60):
        """Times out a user for a specified duration"""
        if interaction.user.id != 717471432816459840:
            await interaction.response.send_message("You do not have permission to use this command. Wait for some other time.")
            return
        if duration < 1 or duration > 2419200:  # 28 days in seconds
            await interaction.response.send_message("Duration must be between 1 second and 28 days (2419200 seconds).", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        
        try:
            await user.timeout(discord.utils.utcnow() + datetime.timedelta(seconds=duration))
            await interaction.followup.send(f"Timed out {user.display_name} for {duration} seconds.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("I do not have permission to timeout this user.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"An error occurred while trying to timeout the user: {e}", ephemeral=True)


    @app_commands.describe(
        user="The user to move",
        voice_channel="The voice channel to move the user to"
    )
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.allowed_installs(True, False)
    @app_commands.command(**bigDict["move_user"])
    async def move_user(self, interaction: discord.Interaction, user: discord.Member, voice_channel: discord.VoiceChannel):
        """Moves a user to a different voice channel"""
        await interaction.response.defer(ephemeral=True)
        if user.voice is None:
            await interaction.followup.send(f"{user.mention} is not in a voice channel", ephemeral=True)
        elif user.voice.channel == voice_channel:
            await interaction.followup.send(f"{user.mention} is already in {voice_channel.mention}", ephemeral=True)
        else:
            await user.move_to(voice_channel)
            await interaction.followup.send(f"Moved {user.mention} to {voice_channel.mention}", ephemeral=True)


    @app_commands.describe(
        voice_channel="The voice channel to move users from",
        new_channel="The voice channel to move users to",
        lock_channel="Whether to lock the channel while moving users"
    )
    @app_commands.allowed_contexts(True, True, True)
    @app_commands.allowed_installs(True, False)
    @app_commands.command(**bigDict["move_voicechannel"])
    async def move_voicechannel(self, interaction: discord.Interaction, voice_channel: discord.VoiceChannel, new_channel: discord.VoiceChannel, list_users: bool = False, lock_channel: bool = False):
        """Moves all users in a voice channel to a different voice channel"""
        if interaction.user.id == 783494134061203526:
            await interaction.response.send_message("You do not have permission to use this command, Coldyn :3w", ephemeral=True)
            return
        if voice_channel == new_channel:
            await interaction.response.send_message("The voice channels are the same", ephemeral=True)
            return
        elif voice_channel.members == []:
            await interaction.response.send_message("The voice channel is empty", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        if lock_channel:
            await voice_channel.set_permissions(voice_channel.guild.default_role, connect=False)
        if len(voice_channel.members) > 20:
            await interaction.followup.send("Moving users, please wait", ephemeral=True)
        if list_users:
            users = [member.mention for member in voice_channel.members]
            await interaction.followup.send(f"Moving users: {', '.join(users)}", ephemeral=True)
        for member in voice_channel.members:
            await member.move_to(new_channel)
        await interaction.followup.send(f"Moved {len(voice_channel.members)} user{"" if len(voice_channel.members) == 1 else "s"} to {new_channel.mention}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(moderation(bot))