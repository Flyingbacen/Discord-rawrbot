import discord
from discord import app_commands
import json
import base64
import time
import os
import aiohttp
import asyncio
import subprocess

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
responses = {}
config_items = [] # format: [token, counting, binary_counting, [download_users]]

try:
	with open("config.json") as config_file:
		config_data = json.load(config_file)
		for item in config_data:
			config_items.append(config_data[item]) 
			if item == "token":
				if isinstance(config_items[0], str) and "." not in config_items[0]: # primitive base64 detect
					config_items.append(base64.b64decode(config_data[item]).decode("utf-8"))
					config_items.remove(config_items[0])
except FileNotFoundError:
	print("FileNotFoundError: rename config_EXAMPLE.json to config.json")

# a ping command. 
@tree.command(name = "ping", description = "hopefully counts to a low number :)")
async def ping(interaction):
	"""Pong! (latency w/ bot)"""
	start_time = time.time()
	message = await interaction.response.send_message("Pong!")
	latency = round((time.time() - start_time) * 1000, 2)
	await interaction.edit_original_response(content=f"Pong!  |  Latency: {latency} ms")
	print(f"A ping command has been sent in {interaction.guild.name} -- {interaction.channel.name}, and the round trip took {latency} ms")
	
@tree.command(name = "ban_list", description = "returns a list of banned users + reason")
async def fwef(interaction):
	"""gives list of bans in server"""
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
	""":D"""
	await interaction.response.send_message(f"Hello {interaction.user.display_name}! I hope you're doing good :)")
	print("hello!")

# pop
@tree.command(name = "pop", description = "a balloon makes this noise once")
async def ballooonpop(interaction):
	"""pop :)"""
	await interaction.response.send_message("*pop*\nFun fact, did you know balloons make this noise only once?\n||I bet I can make that noise with you multiple times, *if you know what I mean 🤭*||")
	print(f"Having some fun w/ {interaction.user.name}, hehe")

# invite link
@tree.command(name = "invite", description = "generate an invite link to let the bot join your server")
async def invite(interaction):
	"""Generates a bot invite link."""
	embedd = discord.Embed(description = "[invite link](https://discord.com/oauth2/authorize?client_id=1118629362368008283&permissions=2147486720&scope=bot&permissions=2147486720&scope=messages.read%20bot)\n(discord.com)", type = "link")
	await interaction.response.send_message(embed = embedd)
	channel = interaction.channel.name
	print(f"sent bot invite to {channel}")

# random informationn
@tree.command(name = "info", description = "Some random information about the server you're in.")
async def information(interaction):
	"""Information about the current user."""
	await interaction.response.send_message(f"server -- {interaction.guild.name} ({interaction.guild.id})\nchannel -- {interaction.channel.name} ({interaction.channel.id})\nUser Information --> \n> Display name -- {interaction.user.display_name}\n> Username -- {interaction.user.name}\n> User ID -- {interaction.user.id}\n> Date Created -- {interaction.user.created_at}")
	print(f"{interaction.user.name} has asked for information.")

# current count of counting
@tree.command(name = "current_count", description = "gives the current count in the counting channel channel.")
async def currentcount(interaction):
	"""gives the current count in the counting channel."""
	count_file = open("CurrentCount.txt", "r+")
	numcount = int(count_file.read())
	await interaction.response.send_message(f"the current number is {numcount}", ephemeral = True)
	count_file.close()

# current count of binary counting
@tree.command(name = "current_count_binary", description = "gives the current count in the binary counting channel.")
async def currentcountbinary(interaction):
	"""gives the current count in the binary counting channel."""
	count_file_binary = open("CurrentCount-Binary.txt", "r+")
	numcount_binary = int(count_file_binary.read())
	await interaction.response.send_message(f"the current number is {numcount_binary}", ephemeral = True)
	count_file_binary.close()


@tree.command(name="cue_redeem", description="Redeems the currently available free cue piece from 8ballpool.com using your user id (1 for help)")
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

@tree.context_menu(name="message")
async def dm(interaction: discord.Interaction, message: discord.Message):
	"""I should probably remove this lmao"""
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
	"""Respond to messages that mention the bot or contain certain words."""
	member = message.author
	if message.author.id == 1118629362368008283: # ignore messages from the bot
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
	
	# counting :) (has to be made an if cause then it won't go to binary counting if I just return :<)
	counting = int(config_items[1])
	if message.channel.id == counting and counting != 1000: # not sure if int is needed, but eh
		count_file = open("CurrentCount.txt", "r+")
		numcount = int(count_file.read())
		try:
			if int(message.content) == (numcount):  # Convert message.content to an integer for comparison
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
		bincounting = int(config_items[2])
		if bincounting == None or bincounting == 1000:
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
