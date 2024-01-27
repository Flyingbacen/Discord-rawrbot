import discord
from discord import app_commands
import base64
import time
import json
import aiohttp
import asyncio

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
responses = {}


# a ping command. 
@tree.command(name = "ping", description = "hopefully counts to a low number :)")
async def ping(interaction):
    start_time = time.time()
    message = await interaction.response.send_message("Pong!")
    latency = round((time.time() - start_time) * 1000, 2)
    await interaction.edit_original_response(content=f"Pong!  |  Latency: {latency} ms")
    print(f"A ping command has been sent in {interaction.guild.name} -- {interaction.channel.name}, and the round trip took {latency} ms")
    
@tree.command(name = "ban_list", description = "returns a list of banned users + reason")
async def fwef(interaction):
    badaaa = " "
    bans = [entry async for entry in interaction.guild.bans()]
    for BanEntry in bans:
        user = BanEntry.user.global_name
        reason = BanEntry.reason
        badaaa += f"User: {user}\nReason: {reason}\n\n"
    badaaa += "\n\n note: users titled \"none\" have since been deleted since they were banned."
    await interaction.response.send_message(badaaa)
    print(bans)


# nice chat :)
@tree.command(name = "hello", description = "I would love to talk to you more, but perhaps a simple hello will suffice")
async def hello(interaction):
    await interaction.response.send_message(f"Hello {interaction.user.display_name}! I hope you're doing good :)")
    print("hello!")

# pop
@tree.command(name = "pop", description = "a balloon makes this noise once")
async def ballooonpop(interaction):
    if interaction.user.id != "932447390672257025":
        print(f"{interaction.user.id}\n932447390672257025")
        await interaction.response.send_message("*pop*\nFun fact, did you know balloons make this noise only once?\n||I bet I can make that noise with you multiple times, *if you know what I mean 🤭*||")
        print(f"Having some fun w/ {interaction.user.name}, hehe")
    else:
        await interaction.response.send_message("no")
        print("ha")

# invite link
@tree.command(name = "invite", description = "generate in an invite link to let the bot join your server")
async def invite(interaction):
    embedd = discord.Embed(description = "[invite link](https://discord.com/oauth2/authorize?client_id=1118629362368008283&permissions=2147486720&scope=bot&permissions=2147486720&scope=messages.read%20bot)\n(discord.com)", type = "link")
    await interaction.response.send_message(embed = embedd)
    channel = interaction.channel.name
    print(f"sent bot invite to {channel}")

# random informationn
@tree.command(name = "info", description = "Some random information about the server you're in.")
async def information(interaction):
    await interaction.response.send_message(f"server -- {interaction.guild.name} ({interaction.guild.id})\nchannel -- {interaction.channel.name} ({interaction.channel.id})\nUser Information --> \n> Display name -- {interaction.user.display_name}\n> Username -- {interaction.user.name}\n> User ID -- {interaction.user.id}\n> Date Created -- {interaction.user.created_at}")
    print(f"{interaction.user.name} has asked for information.")

# current count of counting
@tree.command(name = "current_count", description = "gives the current count in the counting channel channel.")
async def currentcount(interaction):
    count_file = open("CurrentCount.txt", "r+")
    numcount = int(count_file.read())
    await interaction.response.send_message(f"the current number is {numcount}", ephemeral = True)
    count_file.close()

# current count of binary counting
@tree.command(name = "current_count_binary", description = "gives the current count in the binary counting channel.")
async def currentcountbinary(interaction):
    count_file_binary = open("CurrentCount-Binary.txt", "r+")
    numcount_binary = int(count_file_binary.read())
    await interaction.response.send_message(f"the current number is {numcount_binary}", ephemeral = True)
    count_file_binary.close()


@tree.command(name="cue_redeem", description="Redeems the currently available free cue piece from 8ballpool.com using your user id (1 for help)")
async def CueRedeem(interaction: discord.Interaction, userid: int):
    await interaction.response.defer()

    if userid == 1:
        await interaction.followup.send("To find your User ID, go in the 8 ball pool app. Tap your profile icon, and your 10 digit ID in the format 123-456-789-0 will be displayed. Do not include the dashes.", ephemeral=True)
    else:
        async with aiohttp.ClientSession() as session:
            async def get_free_cue_sku(user_id, category_wildcard):
                url = f'https://8ballpool.com/api/items?userId={user_id}'

                try:
                    async with session.get(url) as response:
                        response.raise_for_status()  # Check for HTTP errors

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

                        print(f"Redemption response status code: {response.status}")

                        if response.status == 200:
                            return True
                        else:
                            return response.status

                except aiohttp.ClientError as e:
                    print(f"Error during redemption: {e}")

            user_id = userid
            category_wildcard = 'free_cue_reward_'

            # Retrieve SKU for the free piece
            free_cue_sku = await get_free_cue_sku(user_id, category_wildcard)
            if free_cue_sku:
                print(f"SKU for the free cue piece: {free_cue_sku}")

                # Redeem the free cue piece
                cue_StatusCode = await redeem_free_cue(user_id, free_cue_sku)
                if cue_StatusCode == True:
                    await interaction.followup.send(f"Successfully redeemed today's cue piece\n\t\t~~||sku:{free_cue_sku}||~~")
                else:
                    await interaction.followup.send(f"Error redeeming today's cue piece.\nStatus code:\n\t{cue_StatusCode}")
            else:
                await interaction.followup.send(f"Failed to retrieve SKU for the free cue piece with category wildcard: {category_wildcard}.")

@tree.context_menu(name="message")
async def dm(interaction: discord.Interaction, message: discord.Message):
    channel = await interaction.user.create_dm()
    await channel.send("meow >\~<")
    await interaction.response.send_message(channel.id)

# get the slash commands ready, and set the status
@client.event
async def on_ready():
    await tree.sync()
    game = discord.Game("with some funny words")
    await client.change_presence(status=discord.Status.idle, activity=game)
    print("Ready!")


### NON-SLASH COMMANDS/REPLIES

# respond to rawr
@client.event
async def on_message(message):
    member = message.author
    # ignore messages from the bot	
    if message.author.id == 1118629362368008283:
        return

    # respond to rawr
    if message.content.lower() == "rawr":
        response_message = await message.channel.send("Rawr! 🦖")
        responses[message.id] = response_message.id
        print("rawr")

    # respond to rawr being in a message
    if "rawr" != message.content.lower() and "rawr" in message.content.lower() and message.author.id != 1118629362368008283:
        if message.content.startswith("prepare to say something "):
            return
        response_message = await message.channel.send("I hear my name, hello :>")
        responses[message.id] = response_message.id
        print("hello to you too")
        
    # repeat what the user tells it to
    if message.content.startswith("prepare to say something bot,"):
        TheSavedMessage = message.content.lower()
        await message.delete()
        quotemessage = TheSavedMessage.split("prepare to say something bot,")
        if quotemessage[1].startswith(" be sneaky though,"):
            sneakyquotemessage = quotemessage[1].split(" be sneaky though,")
            await message.channel.send(sneakyquotemessage[1])
            print(f"sneakily saying {sneakyquotemessage[1]}")
        elif await message.channel.send(f">{quotemessage[1]}"):
            print(f"imma boutta say {quotemessage[1]}")
            return
    
    # counting :) 
    if message.channel.id == 1165795834898698280:
        count_file = open("CurrentCount.txt", "r+")
        numcount = int(count_file.read())
        if message.content.lower() == str(numcount):  # Convert numcount to a string for comparison
            numcount += 1
            count_file.seek(0)
            count_file.write(str(numcount))
            count_file.close()
        else:
            await message.delete()
            bomessage = await message.channel.send(f"{message.content.lower()} is not the correct number")
            await asyncio.sleep(3)
            await bomessage.delete()
    elif message.channel.id != 1200257700378984509:
        return
    else: # A binary counting for some reason idk
        count_file_binary = open("CurrentCount-Binary.txt", "r+")
        numcount_binary = int(count_file_binary.read())
        if f"0b{message.content.lower()}" == bin(numcount_binary):
            numcount_binary += 1
            count_file_binary.seek(0)
            count_file_binary.write(str(numcount_binary))
            count_file_binary.close()
        else:
            await message.delete()
            njk = await message.channel.send(f"{message.channel.user_id}{message.content.lower()}...\n\tLook at you're mistake >:(")
            await asyncio.sleep(float(3))
            await njk.delete()



# delete the message if the original message to "rawr" is deleted
@client.event
async def on_message_delete(message):
    if message.id in responses:
        channel = message.channel
        response_id = responses[message.id]
        response_message = await channel.fetch_message(response_id)
        await response_message.delete()
        del responses[message.id]
        print(f"bye bye {response_message}")


dsctoken = "TOKEN"

client.run(dsctoken)