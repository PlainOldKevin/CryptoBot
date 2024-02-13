# Imports
import discord
import requests

# Add instance of discord client
client = discord.Client()

# Add on ready instance (when client is ready for use)
@client.event
async def on_ready():
    print("We have logged in as " + client)