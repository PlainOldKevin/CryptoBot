# Imports
import discord
import requests
import os
from dotenv import load_dotenv

# Initialize load-env for token accessing
load_dotenv()

# Store important values from .env in variables
BOT_TOKEN = os.getenv('TOKEN')
API_KEY = os.getenv('KEY')

# Add instance of discord client with intents
intents = discord.Intents.default()
intents.message_content = True
bot = discord.commands.bot(command_prefix='/', intents=intents)

# Add on ready instance (when client is ready for use)
@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))

# Bot behavior when it receives an external message
@bot.event
async def on_message(message):
    if message.author == bot.user: # If message sender is the bot, return nothing to avoid infinite loop
        return
    
    # Test prompt for bot to respond to
    if message.content.startswith('/hello'):
        await message.channel.send('hi')

# Run the bot
bot.run(BOT_TOKEN)