# Imports
import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from utils.data_manager import DataManager

# Initialize load-env for token accessing
load_dotenv()

# Store important values from .env in variables
BOT_TOKEN = os.getenv('TOKEN')
TEST_TOKEN = os.getenv('TEST_TOKEN')

# Create class
class CryptoBot(commands.Bot):

    # Init method (set important variables)
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents) # Call commands.bot init method for this bot
        self.data_manager = DataManager()                                # Set up singular database class

    # Log function when bot is running
    async def on_ready(self):
        print("We have logged in as {0.user}".format(self))

    # Bot says hi to the user
    @commands.command()
    async def hello(self, ctx):
        await ctx.send("hi")

    # Function to load cogs into the bot
    async def load_cogs(self):
        # List of all the cog files (to be loaded into the bot below)
        cogs_list = ['cogs.prices_cog']

        # Load the extensions into the bot
        for cog in cogs_list:
            try:
                await self.load_extension(cog)
                print(f"Loaded cog: {cog}")
            except Exception as e:
                print(f"Failed to load cog: {cog}")
                print(f"[ERROR] {e}")
    
    # Function to start necessary processes and run the bot
    async def run_bot(self):
        await self.data_manager.populate_cache()
        await self.load_cogs()
        await self.start(BOT_TOKEN)

# Main function to be ran
async def main():
    # Add instance of discord client with intents
    intents = discord.Intents.default()
    intents.message_content = True

    # Create CryptoBot instance 
    bot = CryptoBot(command_prefix='/', intents=intents)

    # Start bot
    await bot.run_bot()

# Run the asynchronous main method (containing bot initialization)
if __name__ == '__main__':
    asyncio.run(main())