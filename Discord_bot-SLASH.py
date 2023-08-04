import discord
from discord import app_commands
import base64
import time

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
responses = {}

# a ping command. 
@tree.command(name = "ping", description = "hopefully counts to a low number :)")
async def ping(interaction):
    """
    await interaction.response.send_message("Counting...")
    for x in range(9223372036854775807):
        await ctx.message.channel.send(x)
    """

    start_time = time.time()
    message = await interaction.response.send_message("Pong!")
    latency = round((time.time() - start_time) * 1000, 2)
    await interaction.edit_original_response(content=f"Pong!  |  Latency: {latency} ms")
    print(f"A ping command has been sent, and the round trip took {latency} ms")


# nice chat :)
@tree.command(name = "hello", description = "I would love to talk to you more, but perhaps a simple hello will suffice")
async def hello(interaction):
    await interaction.response.send_message(f"Hello {interaction.user.display_name}! I hope you're doing good :)")
    print("hello!")

# pop
@tree.command(name = "pop", description = "a balloon makes this noise once")
async def ballooonpop(interaction):
    await interaction.response.send_message("*pop*\nFun fact, did you know balloons make this noise only once?\n||I bet I can make that noise with you multiple times, *if you know what I mean 😉*||")
    print(f"Having some fun w/ {interaction.user.name}, hehe")

# invite link
@tree.command(name = "invite", description = "generate in an invite link to let the bot join your server")
async def invite(interaction):
    embedd = discord.Embed(description = "[invite link](https://discord.com/oauth2/authorize?client_id=1118629362368008283&permissions=2147486720&scope=bot&permissions=2147486720&scope=messages.read%20bot).", type = "link")
    await interaction.response.send_message(embed = embedd)
    channel = interaction.channel.name
    print(f"sent bot invite to {channel}")


# get the slash commands ready, and set the status
@client.event
async def on_ready():
    await tree.sync()
    game = discord.Game("with some funny sounding words")
    await client.change_presence(status=discord.Status.idle, activity=game)
    print("Ready!")


# respond to rawr
@client.event
async def on_message(message):
    member = message.author

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
        elif await message.channel.send(f"ok then!\n > {quotemessage[1]}"):
            print(f"imma boutta say {quotemessage[1]}")
            return



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


token = TOKEN
dsctoken = base64.b64decode(token).decode("utf-8")

client.run(dsctoken)
