import discord
from discord import app_commands
import json
import base64
import time
import os
import aiohttp
import asyncio
import re
from translate import Translator
import glob
import ffmpeg
# import ffprobe
import yt_dlp

# region startup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
responses = {}
randomnumber = 0
lock = asyncio.Lock()
webhook = "https://discord.com/api/webhooks/1296600068639555624/RlIBWMp7ljcanoZ7mi-iq7UkVyjptnEpr7MgYJrPeuB1KZ1KJ-H6rsWK5noyMqzVeCoz"

try:
    with open("responses.json") as responses_file:
        responses = json.load(responses_file)
except FileNotFoundError:
    choice = input("responses.json not found, would you like to create a new one? (y/n)\n")
    if choice.lower() in ["yes", "y"]:
        with open("responses.json", "w") as responses_file:
            json.dump({"responses": []}, responses_file)
    exit(0)

config_items = [] # format: [token, counting, binary_counting]

try:
    with open("config.json") as config_file:
        config_data = json.load(config_file)
        for item in config_data:
            config_items.append(config_data[item]) 
            if item == "token":
                if isinstance(config_items[0], str) and "." not in config_items[0]: # bad base64 detect
                    config_items.append(base64.b64decode(config_data[item]).decode("utf-8"))
                    config_items.remove(config_items[0])
except IndexError:
    print("Check that there are 3 items in the config.json file")
    exit()
except FileNotFoundError:
    print("FileNotFoundError: rename config_EXAMPLE.json to config.json")
    choice = input("Would you like to create a placeholder? (y/n)\n")
    if choice.lower() in ["yes", "y"]:
        with open("config.json", "w") as config_file:
            json.dump({"token": "token", "counting": 1000, "binary_counting": 1000}, config_file)
    exit()
# endregion

# a ping command. 
@tree.command(name = "ping", description = "hopefully counts to a low number :)")
# region /ping
async def ping(interaction):
    """Pong! (latency w/ bot)"""
    start_time = time.time()
    message = await interaction.response.send_message("Pong!")
    latency = round((time.time() - start_time) * 1000, 2)
    await interaction.edit_original_response(content=f"Pong!    |    Latency: {latency} ms")
    print(f"A ping command has been sent in {interaction.guild.name} -- {interaction.channel.name}, and the round trip took {latency} ms")
# endregion
    
@tree.command(name = "ban_list", description = "returns a list of banned users + reason")
# region /ban_list
async def fwef(interaction):
    """gives list of bans in server"""
    await interaction.response.defer()
    badaaa = " "
    bans = [entry async for entry in interaction.guild.bans()]
    for BanEntry in bans:
        user = BanEntry.user.global_name
        reason = BanEntry.reason
        badaaa += f"User: {user}\nReason: {reason}\n\n"
    badaaa += "\n\n note: users titled \"none\" have since been deleted since they were banned."
    await interaction.followup.send(badaaa)
    if badaaa == " \n\n note: users titled \"none\" have since been deleted since they were banned.":
        await interaction.followup.send("No people have been banned in this server")
    print(bans)
# endregion

# nice chat :)
@tree.command(name = "hello", description = "I would love to talk to you more, but perhaps a simple hello will suffice")
# region /hello
async def hello(interaction):
    """:D"""
    await interaction.response.send_message(f"Hello {interaction.user.display_name}! I hope you're doing good :)")
    print("hello!")
# endregion

# pop
@tree.command(name = "pop", description = "a balloon makes this noise once")
# region /pop
async def ballooonpop(interaction):
    """pop :)"""
    await interaction.response.send_message("*pop*\nFun fact, did you know balloons make this noise only once?\n||I bet I can make that noise with you multiple times, *if you know what I mean 🤭*||")
    print(f"Having some fun w/ {interaction.user.name}, hehe")
# endregion

# invite link
@tree.command(name = "invite", description = "generate an invite link to let the bot join your server")
# region /invite
async def invite(interaction):
    """Generates a bot invite link."""
    embedd = discord.Embed(description = "[invite link](https://discord.com/oauth2/authorize?client_id=1118629362368008283&permissions=2147486720&scope=bot&permissions=2147486720&scope=messages.read%20bot)\n(discord.com)", type = "link")
    await interaction.response.send_message(embed = embedd)
    channel = interaction.channel.name
    print(f"sent bot invite to {channel}")
# endregion

# random informationn
@tree.command(name = "info", description = "Some random information about the server you're in.")
# region /info
async def information(interaction):
    """Information about the current user."""
    await interaction.response.send_message(f"server -- {interaction.guild.name} ({interaction.guild.id})\nchannel -- {interaction.channel.name} ({interaction.channel.id})\nUser Information --> \n> Display name -- {interaction.user.display_name}\n> Username -- {interaction.user.name}\n> User ID -- {interaction.user.id}\n> Date Created -- {interaction.user.created_at}")
    print(f"{interaction.user.name} has asked for information.")
# endregion

# current count of counting
@tree.command(name = "current_count", description = "gives the current count in the counting channel channel.")
# region /current_count
async def currentcount(interaction):
    """gives the current count in the counting channel."""
    count_file = open("CurrentCount.txt", "r+")
    numcount = int(count_file.read())
    await interaction.response.send_message(f"the current number is {numcount}", ephemeral = True)
    count_file.close()
# endregion

# current count of binary counting
@tree.command(name = "current_count_binary", description = "gives the current count in the binary counting channel.")
# region /current_count_binary
async def currentcountbinary(interaction):
    """gives the current count in the binary counting channel."""
    count_file_binary = open("CurrentCount-Binary.txt", "r+")
    numcount_binary = int(count_file_binary.read())
    await interaction.response.send_message(f"the current number is {numcount_binary}", ephemeral = True)
    count_file_binary.close()
# endregion

@tree.command(name="cue_redeem", description="Redeems the currently available free cue piece from 8ballpool.com using your user id (1 for help)")
# region /cue_redeem
async def CueRedeem(interaction: discord.Interaction, userid: int):
    """Redeems the cue piece from 8 ball pool's api"""
    if userid == 1:
        await interaction.response.send_message("To find your User ID, go in the 8 ball pool app. Tap your profile icon, and your 10 digit ID in the format 123-456-789-0 will be displayed. Do not include the dashes.", ephemeral=True)
    else:
        await interaction.response.defer()
        async with aiohttp.ClientSession() as session:
            async def get_free_cue_sku(user_id, category_wildcard):
                url = f'https://8ballpool.com/api/items?userId={user_id}'

                try:
                    async with session.get(url) as response:
                        response.raise_for_status()    # Check for HTTP errors

                        data = await response.json()
                        items = data.get('items', [])

                        for item in items:
                            if category_wildcard in item.get('category', ''):
                                return item.get('sku')

                except aiohttp.ClientError as e:
                    return None

            async def redeem_free_cue(user_id, sku):
                url = 'https://8ballpool.com/api/claim'
                headers = {'content-type': 'application/json'}
                payload = {
                    "user_id": str(user_id),
                    "sku": sku
                }
                try:
                    async with session.post(url, headers=headers, json=payload) as response:
                        response.raise_for_status()
                        z = response.status

                        print(f"Redemption response status code: {z}")

                        if z == 200:
                            return True
                        else:
                            return z

                except aiohttp.ClientResponseError as e:
                    print(f"Error during redemption: {e}")
                    return e

            async def check(user_id):
                if user_id == 2:
                    user_id = 2705321800 # my user ID :3
                return user_id
            user_id = userid

            category_wildcard = 'free_'

            # Retrieve SKU for the free piece
            free_cue_sku = await get_free_cue_sku(await check(user_id), category_wildcard)
            if free_cue_sku:
                print(f"SKU for the free cue piece: {free_cue_sku}")

                # Redeem the free cue piece
                cue_StatusCode = await redeem_free_cue(await check(user_id), free_cue_sku)
                if cue_StatusCode == True:
                    await interaction.followup.send(f"Successfully redeemed today's cue piece\n\t\tsku:||{free_cue_sku}||")
                else:
                    if cue_StatusCode == "400, message='Bad Request', url=URL('https://8ballpool.com/api/claim')":
                        await interaction.followup.send("Error redeeming today's cue piece.\nStatus code:\t`400`\nPossible reasons: User ID is invalid or the free cue piece has already been redeemed today.")
                    await interaction.followup.send(f"Error redeeming today's cue piece.\nStatus code:\t{cue_StatusCode}")
            else:
                await interaction.followup.send(f"Failed to retrieve SKU for the free cue piece with category wildcard: {category_wildcard}.")
# endregion

@tree.command(name="mute", description="Mutes a user")
@app_commands.describe(voice_channel="The voice channel to (un)mute the user in",
                         user="The user to (un)mute",
                         mute="Whether to mute or unmute the user",
                         time="The time to mute the user for, default is 5, set to 0 to disable. Only used when muting")
# region /mute
async def remute(interaction: discord.Interaction, voice_channel: discord.VoiceChannel, user: discord.Member, mute: bool, time: int = 5):
    """Mutes a user"""
    
    tempMember = next((e for e in voice_channel.members if e.id == user.id), None)
    if tempMember is None:
        await interaction.followup.send(f"{user.display_name} is not in the voice channel")
        return
    else:
        await interaction.response.defer(ephemeral=True)
        await tempMember.edit(mute=mute)
        if time != 0 and mute:
            mutingmessage = await interaction.followup.send(f"{'Muted' if mute else 'Unmuted'} {user.display_name} for {time} seconds")
            await asyncio.sleep(time)
            await tempMember.edit(mute=False)
            await interaction.followup.edit_message(mutingmessage.id, content = f"Unmuted <@{user.id}> after {time} seconds")
        else:
            await interaction.followup.send(f"{'Muted' if mute else 'Unmuted'} {user.display_name}")
# endregion

@tree.command(name="deafen", description="Deafens a user")
@app_commands.describe(voice_channel="The voice channel to (un)deafen the user in",
                         user="The user to (un)deafen",
                         deafen="Whether to deafen or undeafen the user",
                         time="The time to deafen the user for, default is 5, set to 0 to disable. Only used when deafening")
# region /deafen
async def deafen(interaction: discord.Interaction, voice_channel: discord.VoiceChannel, user: discord.Member, deafen: bool, time: int = 5):
    """Deafens a user"""
    await interaction.response.defer(ephemeral=True)
    
    tempMember = next((e for e in voice_channel.members if e.id == user.id), None)
    if tempMember is None:
        await interaction.followup.send(f"{user.display_name} is not in the voice channel")
        return
    else:
        await tempMember.edit(deafen=deafen)
        if time != 0 and deafen:
            deafeningmessage = await interaction.followup.send(f"{'Deafened' if deafen else 'Undeafened'} {user.display_name} for {time} seconds")
            await asyncio.sleep(time)
            await tempMember.edit(deafen=False)
            await interaction.followup.edit_message(deafeningmessage.id, content = f"Undeafened {user.mention} after {time} seconds")
        else:
            await interaction.followup.send(f"{'Deafened' if deafen else 'Undeafened'} {user.display_name}")
# endregion

@tree.command(name="move_single", description="Moves a user to a different voice channel")
@app_commands.describe(user="The user to move",
                         voice_channel="The voice channel to move the user to")
# region /move_single
async def move(interaction: discord.Interaction, user: discord.Member, voice_channel: discord.VoiceChannel):
    """Moves a user to a different voice channel"""
    await interaction.response.defer(ephemeral=True)
    if user.voice is None:
        await interaction.followup.send(f"{user.mention} is not in a voice channel", ephemeral=True)
    elif user.voice.channel == voice_channel:
        await interaction.followup.send(f"{user.mention} is already in {voice_channel.mention}", ephemeral=True)
    else:
        await user.move_to(voice_channel)
        await interaction.followup.send(f"Moved {user.mention} to {voice_channel.mention}", ephemeral=True)
# endregion

@tree.command(name="move_all", description="Moves all users in a voice channel to a different voice channel")
@app_commands.describe(voice_channel="The voice channel to move users from",
                         new_channel="The voice channel to move users to",
                         lock_channel="Whether to lock the channel while moving users")
# region /move_all
async def move_all(interaction: discord.Interaction, voice_channel: discord.VoiceChannel, new_channel: discord.VoiceChannel, list_users: bool = False, lock_channel: bool = False):
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
# endregion



"""User app commands"""

async def languages(interaction, current):
    return [
        app_commands.Choice(name="English",    value="en"),
        app_commands.Choice(name="Spanish",    value="es"),
        app_commands.Choice(name="German",     value="de"),
        app_commands.Choice(name="Russian",    value="ru"),
        app_commands.Choice(name="Japanese",     value="ja"),
        app_commands.Choice(name="Chinese",    value="zh"),
        app_commands.Choice(name="French",     value="fr"),
        app_commands.Choice(name="Italian",    value="it"),
        app_commands.Choice(name="Korean",     value="ko"),
        app_commands.Choice(name="Portuguese", value="pt"),
        app_commands.Choice(name="Dutch",        value="nl"),
        app_commands.Choice(name="Danish",     value="da"),
        app_commands.Choice(name="Finnish",    value="fi"),
        app_commands.Choice(name="Greek",        value="el"),
        app_commands.Choice(name="Arabic",     value="ar"),
        app_commands.Choice(name="Hebrew",     value="he"),
        app_commands.Choice(name="Hindi",        value="hi"),
        app_commands.Choice(name="Indonesian", value="id"),
        app_commands.Choice(name="Latvian",    value="lv"),
        app_commands.Choice(name="Lithuanian", value="lt"),
        app_commands.Choice(name="Malay",        value="ms"),
        app_commands.Choice(name="Swahili",    value="sw"),
        app_commands.Choice(name="Tamil",        value="ta"),
        app_commands.Choice(name="Telugu",     value="te"),
        app_commands.Choice(name="Urdu",         value="ur")
    ]

@tree.command(name="translate", description="Translates text to a different language")
@app_commands.user_install()
@app_commands.allowed_contexts(True, True, True)
@app_commands.autocomplete(from_language=languages)
@app_commands.autocomplete(to_language=languages)
@app_commands.describe(
    text="The text to translate",
    from_language="The language to translate from",
    to_language="The language to translate to"
)
# region /translate
async def Translate(interaction: discord.Interaction, text: str, from_language: str, to_language: str, ephemeral: bool = False):
    await interaction.response.defer()
    translator = Translator(from_lang=from_language, to_lang=to_language)
    translation = translator.translate(text)
    await interaction.followup.send(translation, ephemeral=True if ephemeral else False)
# endregion

@tree.command(name="upload", description="Uploads a file to sxcu.net and returns the URL")
@app_commands.user_install()
@app_commands.allowed_contexts(True, True, True)
@app_commands.describe(link="The link to the file to upload", optional_message="An optional message to send with the file")
# region /upload
async def upload(interaction: discord.Interaction, link: str, optional_message: str = ""):
    if interaction.user.id != 717471432816459840:
        await interaction.response.send_message("You do not have permission to use this command. Wait for some other time.\nTry </Image:1279220378945720320> instead")
        return

    regex = re.compile("((http|https)://)(www\\.)?" +
             "[a-zA-Z0-9@:%._\\+~#?&//=]" +
             "{2,256}\\.[a-z]" +
             "{2,6}\\b([-a-zA-Z0-9@:%" +
             "._\\+~#?&//=]*)")
    if not re.search(regex, link):
        await interaction.response.send_message("Invalid link", ephemeral=True)
        return

    # if    isinstance(interaction.channel, discord.DMChannel):
    #     await interaction.response.send_message("This command can not be used in a DM channel. This is due to the bot not having the permission to upload files and no ability to embed files either.", ephemeral=True)
    #     return

    for file in glob.glob("temp.*"):
        os.remove(file)

    """import io
    filestream = io.BytesIO()
    ydl_opts = { 
        'quiet': True,
        'format': 'bestaudio/best',
        'outtmpl': filestream,
        'noplaylist': True,
        'nocheckcertificate': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'webm',
            'preferredquality': '192',
        }],
    }
    ydl = yt_dlp.YoutubeDL(ydl_opts)
    metadata = ydl.extract_info([link])
    try:
        file_size = metadata["requested_formats"][0]["filesize"]
    except KeyError:
        ydl.download([link])

    if file_size >= 9.5e+7:
        await interaction.followup.send("File is too large, please select a file smaller than 95MB", ephemeral=True)
        lock.release()
        return
        filename = metadata["title"] + ".webm"
    elif file_size >= 2.5e+7 and file_size <= 9.5e+7:

        uploading = await interaction.followup.send("Uploading file", ephemeral=True)
        ydl.download([link])
        output_stream = io.BytesIO()
        
        process = (
            ffmpeg
            .input('pipe:0')
            .output('pipe:1', format='webm', acodec='copy')
            .run_async(pipe_stdin=True, pipe_stdout=True)
        )
        process.stdin.write(filestream.read())
        process.stdin.close()
        filestream.close()

        output_stream.write(await process.stdout.read())
        process.stdout.close()

        process.wait()
        output_stream.seek(0)
        filestream = output_stream
        output_stream.close()


        url = "https://sxcu.net/api/files/create"
        async with aiohttp.ClientSession() as session: # upload the file to sxcu
            file_data = filestream.read()
            data = aiohttp.FormData()
            data.add_field('file', file_data, filename=link.split('/')[-1])
            async with session.post(
                url,
                headers={
                    "User-Agent": "Uploader",
                    "token": "03667999-fec2-4afb-8bf2-792c4444ee8d"
                },
                data=data
            ) as response:
                response_data = await response.json()
        
        url = f"https://sxcu.net/api/files/{response_data['id']}"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={
                    "User-Agent": "Uploader"
                }
            ) as response:
                response_info = await response.json()
        
        await interaction.followup.edit_message(uploading.id, content = "Uploaded")
        await interaction.followup.send(response_info["url"], username=interaction.user.display_name, avatar_url=interaction.user.display_avatar.url)
        return
    elif file_size <= 2.5e+7:
        await interaction.followup.send("File is smaller than 25MB, uploading directly.", ephemeral=True)

        ydl.download([link])
        output_stream = io.BytesIO()
        
        process = (
            ffmpeg
            .input('pipe:0')
            .output('pipe:1', format='webm', acodec='copy')
            .run_async(pipe_stdin=True, pipe_stdout=True)
        )
        process.stdin.write(filestream.read())
        process.stdin.close()
        filestream.close()

        output_stream.write(await process.stdout.read())
        process.stdout.close()

        process.wait()
        output_stream.seek(0)
        filestream = output_stream
        output_stream.close()

        interaction.followup.send(file=discord.File(filestream))
        lock.release()
        return"""
    
    await lock.acquire()
    await interaction.response.defer(ephemeral=True)
    # region download file
    message1 = await interaction.followup.send("Downloading file", ephemeral=True)
    process = await asyncio.create_subprocess_exec(
        'c:/users/aster/yt-dlp.exe', link, "--no-part", "-o", "temp.webm",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()    
    await interaction.followup.edit_message(message1.id, content="Downloaded file")
    # endregion

    try:
        file = glob.glob("temp.webm*")[0]
        # await interaction.followup.send(glob.glob("temp.webm*"))
        # return
    except IndexError:
        await interaction.followup.send("An error occurred: Could not find the file", ephemeral=True)
        lock.release()
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
    if int(data["format"]["size"]) >= 9.5e+7: # 95MB, sxcu limit
        await interaction.followup.send("File is too large, please select a file smaller than 95MB", ephemeral=True)
        os.remove(file)
        lock.release()
        return
    # region upload file - Discord
    if int(data["format"]["size"]) <= 2.5e+7:
        await interaction.followup.send("File is smaller than 25MB, uploading directly.", ephemeral=True)
        print("uploading directly")
        if interaction.channel.id == 1278161126860787837:
            async with aiohttp.ClientSession() as session:
                messagewebhook = discord.Webhook.from_url(webhook, session=session)
                await messagewebhook.send(optional_message, file=discord.File(file), username=interaction.user.display_name, avatar_url=interaction.user.display_avatar.url)
        else:
            await interaction.followup.send(optional_message, file=discord.File(file), username=interaction.user.display_name, avatar_url=interaction.user.display_avatar.url)
        os.remove("temp.webm")
        lock.release()
        return
    # endregion

    # region upload file - sxcu
    if data["format"]["format_name"] != "matroska,webm":
        message3 = await interaction.followup.send("File is not a webm file, converting", ephemeral=True)
        process = await asyncio.create_subprocess_exec(
            'c:/windows/ffmpeg.exe', '-i', file, "-y" , '-c:v', 'libvpx', '-c:a', 'libopus', file + 'temp_convert.webm',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.wait()
        await process.communicate()
        os.remove(file)
        os.rename(file + 'temp_convert.webm', file)
        await interaction.followup.edit_message(message3.id, content="Converted file")

    message2 = await interaction.followup.send("Uploading file", ephemeral=True)
    url = "https://sxcu.net/api/files/create"
    async with aiohttp.ClientSession() as session: # upload the file to sxcu
        with open(file, "rb") as file_binary:
            file_data = file_binary.read()
        data = aiohttp.FormData()
        data.add_field('file', file_data, filename=link.split('/')[-1])
        async with session.post(
            url,
            headers={
                "User-Agent": "Uploader",
                "token": "03667999-fec2-4afb-8bf2-792c4444ee8d"
            },
            data=data
        ) as response:
            response_data = await response.json()
    
    url = f"https://sxcu.net/api/files/{response_data['id']}"
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url,
            headers={
                "User-Agent": "Uploader"
            }
        ) as response:
            response_info = await response.json()
    await interaction.followup.edit_message(message2.id, content = "Uploaded")
    # endregion
    await interaction.followup.send(response_info["url"], username=interaction.user.display_name, avatar_url=interaction.user.display_avatar.url)
    if interaction.channel.id == 1278161126860787837:
        async with aiohttp.ClientSession() as session:
            messagewebhook = discord.Webhook.from_url(webhook, session=session)
            if optional_message != "":
                await messagewebhook.send(optional_message, username=interaction.user.display_name, avatar_url=interaction.user.display_avatar.url)
            await messagewebhook.send(response_info["url"], username=interaction.user.display_name, avatar_url=interaction.user.display_avatar.url)
            # two seperate messages to avoid the link being shown
    else:
        interaction.followup.send(optional_message, username=interaction.user.display_name, avatar_url=interaction.user.display_avatar.url)
        interaction.followup.send(response_info["url"], username=interaction.user.display_name, avatar_url=interaction.user.display_avatar.url)
    os.remove(file)
    lock.release()
# endregion

@tree.command(name="playinaudiochannel", description="Plays audio in a voice channel, downloaded with yt-dlp")
@app_commands.allowed_contexts(True, False, False)
@app_commands.describe(link="The link to the audio to play", channel="The voice channel to play the audio in")
async def playinaudiochannel(interaction: discord.Interaction, link: str, channel: discord.VoiceChannel):
    if interaction.user.id != 717471432816459840:
        await interaction.response.send_message("You do not have permission to use this command. Wait for some other time.")
        return
    if not link.startswith("http"):
        await interaction.followup.send("Invalid link", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)

    process = await asyncio.create_subprocess_exec(
        'c:/users/aster/yt-dlp.exe', "-x", link, "-o", "temp.mp3",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()
    try:
        file = glob.glob("temp.mp3*")[0]
    except IndexError:
        await interaction.followup.send("An error occurred: Could not find the file", ephemeral=True)
        return

    voice_client = await channel.connect()
    voice_client.play(discord.FFmpegPCMAudio(file))
    while voice_client.is_playing():
        await asyncio.sleep(1)
    await voice_client.disconnect()
    os.remove(file)
    await interaction.followup.send("Finished playing audio", ephemeral=True)

@tree.command(name="test", description="test command")
@app_commands.user_install()
@app_commands.allowed_contexts(False, True, True)
async def test(interaction: discord.Interaction, file: discord.Attachment):
    file = await file.to_file()
    await interaction.response.send_message(file=file)

# get the slash commands ready, and set the status
@client.event
async def on_ready():
    await tree.sync()
    activity = discord.Activity(type=discord.ActivityType.listening, name="your commands")
    await client.change_presence(activity=activity, status=discord.Status.idle)
    print("Ready!")


### NON-SLASH COMMANDS/REPLIES

# respond to rawr
@client.event
async def on_message(message):
    """Respond to messages that mention the bot or contain certain words."""
    member = message.author
    if message.author.id == 1118629362368008283: # ignore messages from the bot
        return

    # respond to rawr
    if message.content.lower() == "rawr":
        response_message = await message.channel.send("Rawr! 🦖")
        responses[message.id] = response_message.id
        print("rawr")
        with open("responses.json", 'r+') as responses_file:
            data = json.load(responses_file)
            data['rawr'] = data.get('rawr', []) + [str(response_message.id)] # idk what's going on here
            responses_file.seek(0)
            json.dump(data, responses_file)
            responses_file.truncate()

    # respond to rawr being in a message
    if "rawr" != message.content.lower() and "rawr" in message.content.lower() and message.author.id != 1118629362368008283:
        if message.content.startswith("prepare to say something "):
            return
        response_message = await message.channel.send("I hear my name, hello :>")
        responses[message.id] = response_message.id
        print("hello to you too")
        
    # repeat what the user tells it to
    if message.content.startswith("prepare to say something bot,"):
        TheSavedMessage = message.content
        await message.delete()
        quotemessage = TheSavedMessage.split("prepare to say something bot,")
        if quotemessage[1].startswith(" be sneaky though,"):
            sneakyquotemessage = quotemessage[1].split(" be sneaky though,")
            await message.channel.send(sneakyquotemessage[1])
            print(f"sneakily saying {sneakyquotemessage[1]}")
        elif await message.channel.send(f">{quotemessage[1]}"):
            print(f"imma boutta say {quotemessage[1]}")
            return
    
    if message.content == "$~stop":
        if message.author.id != 717471432816459840: return
        await message.channel.send("Stopping the bot")
        await client.close()
        print("Stopping the bot")
    
    if message.content == "$~restart":
        if message.author.id != 717471432816459840: return
        await message.channel.send("Restarting the bot")
        await client.close()
        os.system("start cmd /c python Discord_bot-SLASH.py")
        exit(0)
    
    # counting :) (has to be made an if cause then it won't go to binary counting if I just return :<)
    if message.channel.id == config_items[1]:
        count_file = open("CurrentCount.txt", "r+")
        numcount = int(count_file.read())
        try:
            if int(message.content) == (numcount):    # Convert message.content to an integer for comparison
                numcount += 1
                count_file.seek(0)
                count_file.write(str(numcount))
                count_file.close()
                await message.add_reaction("✅")
                if int(message.content) % 100 == 0 and int(message.content) % 1000 != 0:
                    await message.add_reaction("❗")
                if int(message.content) % 1000 == 0:
                    await message.add_reaction("‼️")
            else:
                await message.delete()
                bomessage = await message.channel.send(f"{message.content.lower()} is not the correct number")
                await asyncio.sleep(3)
                await bomessage.delete()
        except ValueError:
            await message.delete()
            bomessage = await message.channel.send(f"your message, `({message.content.lower()})`, is not a number")
            await asyncio.sleep(3)
            await bomessage.delete()
    else:
        if message.channel.id != config_items[2]:
            return
        count_file_binary = open("CurrentCount-Binary.txt", "r+")
        numcount_binary = int(count_file_binary.read())
        if f"0b{message.content.lower()}" == bin(numcount_binary):
            numcount_binary += 1
            count_file_binary.seek(0)
            count_file_binary.write(str(numcount_binary))
            count_file_binary.close()
        else:
            await message.delete()
            njk = await message.channel.send(f"{message.content.lower()}...\n\tLook at you're mistake >:(")
            await asyncio.sleep(float(3))
            await njk.delete()



# delete the message if the original message to "rawr" is deleted

@client.event
async def on_message_delete(message):
    """Delete the response message if the original message is deleted."""
    if message.id in responses:
        channel = message.channel
        response_id = responses[message.id]
        response_message = await channel.fetch_message(response_id)
        await response_message.delete()
        del responses[message.id]
        print(f"bye bye {response_message}")



client.run(config_items[0])
