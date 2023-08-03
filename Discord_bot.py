import base64
import datetime
import discord
from discord.ext import commands
import time

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=",", intents=intents)
responses = {}
token = TOKEN
dsctoken = base64.b64decode(token).decode("utf-8")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} ({bot.user.id})")
    print("Rawr!")

@bot.event
async def on_message(message):
    member = message.author
    if message.author == bot.user:
        return

    if message.content.lower() == "rawr":
        response_message = await message.channel.send("Rawr! 🦖")
        responses[message.id] = response_message.id

    if "rawr" != message.content.lower() and "rawr" in message.content.lower() and "rawr, prefix is now" not in message.content.lower():
        response_message = await message.channel.send("I hear my name, hello :>")
        responses[message.id] = response_message.id

    if "rawr, prefix is now" in message.content.lower():
        split_message = message.content.lower().split("rawr, prefix is now ")
        if len(split_message) > 1:
                prefix = split_message[1]
                bot.command_prefix = prefix
                await message.channel.send(f"oki, it's now '{prefix}' tehe~ :3")
                print(f"the prefix is now {prefix}")

    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    if message.id in responses:
        channel = message.channel
        response_id = responses[message.id]
        response_message = await channel.fetch_message(response_id)
        await response_message.delete()
        del responses[message.id]

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.name}!")

@bot.command()
async def ping(ctx):
    start_time = time.time()
    message = await ctx.send("Pong!")
    latency = round((time.time() - start_time) * 1000, 2)
    await message.edit(content=f"Pong!  |  Latency: {latency} ms")
    print(f"A ping command has been sent, and the round trip took {latency} ms")

bot.run(dsctoken)
