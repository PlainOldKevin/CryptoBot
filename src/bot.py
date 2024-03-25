# Imports
import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

# Initialize load-env for token accessing
load_dotenv()

# Store important values from .env in variables
BOT_TOKEN = os.getenv('TOKEN')
TEST_TOKEN = os.getenv('TEST_TOKEN')

# Add instance of discord client with intents
intents = discord.Intents.default()
intents.message_content = True

# Initialiaze bot
bot = commands.Bot(command_prefix='/', intents=intents)

# Run function when bot is initialized
@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))

# Bot says hi to the user
@bot.command()
async def hello(ctx):
    await ctx.send("hi")

# Main function to handle bot's cog loading and running
async def main():
    # List of all the cog files (to be loaded into the bot below)
    cogs_list = ['cogs.prices_cog']

    # Load the extensions into the bot
    for cog in cogs_list:
        try:
            await bot.load_extension(cog)
            print(f"Loaded cog: {cog}")
        except Exception as e:
            print(f"Failed to load cog: {cog}")
            print(f"[ERROR] {e}")

    await bot.start(TEST_TOKEN)

# Run the asynchronous main method (containing bot initialization)
if __name__ == '__main__':
    asyncio.run(main())