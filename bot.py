# Imports
import discord
import requests
import os
from dotenv import load_dotenv

# Initialize load-env for token accessing
load_dotenv()

# Add instance of discord client with intents
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Add on ready instance (when client is ready for use)
@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

# Bot behavior when it receives an external message
@client.event
async def on_message(message):
    if message.author == client.user: # If message sender is the bot, return nothing to avoid infinite loop
        return
    
    # Test prompt for bot to respond to
    if message.content.startswith('/hello'):
        await message.channel.send('hi')

# Run the bot
client.run(os.getenv('TOKEN'))