import discord
from discord.ext import commands
from discord import app_commands
from translate import Translator
from typing import Optional
import random
import asyncio
import os
import re
import glob
import aiohttp
import json
# from NEW.main import config_items
from main import config_items

bigDict = {
    "translate": {
        "name": "translate",
        "description": "Translate text from one language to another",
        "nsfw": False,
        "auto_locale_strings": True,
        "extras": {
            
        }
    },
    "random_image": {
        "name": "random_image",
        "description": "finds and selects a random image. If `channel` is not set, then searches the server",
        "nsfw": False,
        "auto_locale_strings": True,
        "extras": {
            
        }
    },
    "upload": {
        "name": "upload",
        "description": "Downloads a video, then uploads it to catbox.moe (max 200MB)",
        "nsfw": False,
        "auto_locale_strings": True,
        "extras": {
            
        }
    },
    "test": {
        "name": "test",
        "description": "...",
        "nsfw": False,
        "auto_locale_strings": True,
        "extras": {
            "AllowedUsers": [
                717471432816459840
            ]
        }
    },
}

class utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tree = bot.tree
        self.lock = asyncio.Lock()

    async def languages(self, interaction, current):
        return [
            app_commands.Choice(name="English", value="en"),
            app_commands.Choice(name="Spanish", value="es"),
            app_commands.Choice(name="German", value="de"),
            app_commands.Choice(name="Russian", value="ru"),
            app_commands.Choice(name="Japanese", value="ja"),
            app_commands.Choice(name="Chinese", value="zh"),
            app_commands.Choice(name="French", value="fr"),
            app_commands.Choice(name="Italian", value="it"),
            app_commands.Choice(name="Korean", value="ko"),
            app_commands.Choice(name="Portuguese", value="pt"),
            app_commands.Choice(name="Dutch", value="nl"),
            app_commands.Choice(name="Danish", value="da"),
            app_commands.Choice(name="Finnish", value="fi"),
            app_commands.Choice(name="Greek", value="el"),
            app_commands.Choice(name="Arabic", value="ar"),
            app_commands.Choice(name="Hebrew", value="he"),
            app_commands.Choice(name="Hindi", value="hi"),
            app_commands.Choice(name="Indonesian", value="id"),
            app_commands.Choice(name="Latvian", value="lv"),
            app_commands.Choice(name="Lithuanian", value="lt"),
            app_commands.Choice(name="Malay", value="ms"),
            app_commands.Choice(name="Swahili", value="sw"),
            app_commands.Choice(name="Tamil", value="ta"),
            app_commands.Choice(name="Telugu", value="te"),
            app_commands.Choice(name="Urdu", value="ur")
        ]


    @app_commands.autocomplete(from_language=languages)
    @app_commands.autocomplete(to_language=languages)
    @app_commands.describe(
        text="The text to translate",
        from_language="The language to translate from",
        to_language="The language to translate to"
    )
    @app_commands.allowed_contexts(True, True, True)
    @app_commands.allowed_installs(True, True)
    @app_commands.command(**bigDict["translate"])
    async def translate(self, interaction: discord.Interaction, text: str, from_language: str, to_language: str, ephemeral: bool = False):
        await interaction.response.defer()
        translator = Translator(from_lang=from_language, to_lang=to_language)
        translation = translator.translate(text)
        await interaction.followup.send(translation, ephemeral=ephemeral)


    @app_commands.describe(
        channel = "The channel to search images in"
    )
    @app_commands.allowed_contexts(True, False, False)
    @app_commands.allowed_installs(True, False)
    @app_commands.command(**bigDict["random_image"])
    async def random_image(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        await interaction.response.defer()
        guild = interaction.guild
        images = []

        async def fetch_images(channel: discord.TextChannel):
            messagetime = None
            while True:
                found = False
                async for msg in channel.history(limit=100, before=messagetime):
                    if msg.attachments:
                        for attachment in msg.attachments:
                            if attachment.content_type and attachment.content_type.startswith("image"):
                            # Save both the message and the attachment URL
                                images.append({"message_url": msg.jump_url, "attachment_url": attachment.url})
                                found = True
                    messagetime = msg.created_at
                if not found:
                    break

        if channel is None and guild is not None:
            for channel in guild.text_channels:
                try:
                    print(f"Checking channel: {channel.name}")
                    await asyncio.wait_for(fetch_images(channel), timeout=10)
                except discord.Forbidden:
                    continue  # Skip channels where the bot doesn't have permission to read history
                except asyncio.TimeoutError:
                    print(f"Timeout while fetching images from {channel.name}")
                    continue
        elif channel:
            try:
                print(f"Checking channel: {channel.name}")
                await asyncio.wait_for(fetch_images(channel), timeout=20)
            except discord.Forbidden:
                await interaction.followup.send("I don't have permission to read messages in that channel.", ephemeral=True)
                return
            except asyncio.TimeoutError:
                pass

        if images:
            random_image = random.choice(images)
            # await interaction.followup.send(random_image["attachment_url"])
            await interaction.followup.send(f"[Jump to message]({random_image['message_url']}) [.]({random_image['attachment_url']})")
        else:
            await interaction.followup.send("No images found in channel history.", ephemeral=True)


    @app_commands.command(**bigDict["upload"])
    async def upload(self, interaction: discord.Interaction, link: str, optional_message: str = ""):
        if interaction.user.id != 717471432816459840:
            await interaction.response.send_message("You do not have permission to use this command. Wait for some other time.\nTry </Image:1279220378945720320> instead")
            return
        skip = False
        if any(link.lower().startswith(drive_letter) for drive_letter in ["c:", "d:"]):
            skip = True

        regex = re.compile(
            r"""
            (?P<protocol>https?://)    # Protocol
            (?P<www>www\.)?    # Optional www
            (?P<host>    # Entire host (domain + TLD)
                (?:[\w\-.~%]+|\p{L}[\p{L}\d\-]*\.)*    # Optional subdomains
                (?:[\w\-.~%]+|\p{L}[\p{L}\d\-]*)    # Main domain + TLD
            )
            (?P<path>/[\w\-._~:/?#[\]@!$&'()*+,;=%\p{L}]*)?  # Optional path/query/fragment
            """,
            re.VERBOSE | re.IGNORECASE | re.UNICODE
        )
        if not re.search(regex, link) and not skip:
            await interaction.response.send_message("Invalid link", ephemeral=True)
            return

        for file in glob.glob("temp.*"):
            os.remove(file)
        
        await self.lock.acquire()
        await interaction.response.defer(ephemeral=True)
        # region download file
        if not skip:
            message1 = await interaction.followup.send("Downloading file", ephemeral=True, wait=True)
            process = await asyncio.create_subprocess_exec(
            'yt-dlp', link, "--no-part", "-o", "temp.webm",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
            )
            await process.communicate() 
            await interaction.followup.edit_message(message1.id, content="Downloaded file")
        # endregion

        try:
            file = glob.glob("temp.*")[0]
            # await interaction.followup.send(glob.glob("temp.webm*"))
            # return
        except IndexError:
            if skip:
                file = link
            else:
                await interaction.followup.send("An error occurred: Could not find the file", ephemeral=True)
                self.lock.release()
            return


        # region get file info
        process = await asyncio.create_subprocess_exec(
            'c:/windows/ffprobe.exe', '-v', 'quiet', '-print_format', 'json', '-show_format', file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        data = json.loads(stdout)
        # endregion
        if int(data["format"]["size"]) >= 2.0e+8: # 200MB
            await interaction.followup.send("File is too large, please select a file smaller than 200MB", ephemeral=True)
            if not skip: os.remove(file)
            self.lock.release()
            return
        # region upload file - Discord
        if int(data["format"]["size"]) <= 1.0e+7:
            await interaction.followup.send("File is smaller than 10MB, uploading directly.", ephemeral=True)
            print("uploading directly")
            if interaction.channel and interaction.channel.id == 1278161126860787837:
                async with aiohttp.ClientSession() as session:
                    messagewebhook = discord.Webhook.from_url(config_items["webhook"], session=session)
                    await messagewebhook.send(optional_message, file=discord.File(file), username=interaction.user.display_name, avatar_url=interaction.user.display_avatar.url)
            else:
                await interaction.followup.send(optional_message, file=discord.File(file), username=interaction.user.display_name, avatar_url=interaction.user.display_avatar.url)
            if not skip: os.remove(file)
            self.lock.release()
            return
        # endregion

        # region upload file - catbox
        await interaction.followup.send("Uploading file to catbox", ephemeral=True)
        url = "https://catbox.moe/user/api.php"
        async with aiohttp.ClientSession() as session:
            with open(file, "rb") as file_binary:
                data = aiohttp.FormData()
                data.add_field('reqtype', 'fileupload')
                data.add_field('fileToUpload', file_binary, filename=os.path.basename(file))
                async with session.post(
                    url,
                    data=data
                ) as response:
                    response_data = await response.text()

        await interaction.followup.send(response_data, username=interaction.user.display_name, avatar_url=interaction.user.display_avatar.url)
        os.remove(file)
        self.lock.release()

async def setup(bot: commands.Bot):
    await bot.add_cog(utility(bot))