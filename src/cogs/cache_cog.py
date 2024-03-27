# Imports
from discord.ext import commands
from decimal import *
import os
import aiohttp
import pandas as pd

# Create class
class CacheCog(commands.Cog):

    # Init method (set important variables)
    def __init__(self, bot):
        self.bot = bot 
        self.api_key = os.getenv('KEY')
        self.gecko_key = os.getenv('GECKO_KEY') 
        self.gecko_df = pd.DataFrame() # Cache for individual coins' id, name, and symbol (from CoinGecko API)

    # Function to populate gecko cache (to be run daily soon... for data integrity & accuracy)
    async def populate_cache(self):
            # Obtain API link to request & receive the data from
            url = 'https://api.coingecko.com/api/v3/coins/list'

            # Asynchronously create a ClientSession (so the bot can make multiple HTTP calls and not get blocked from just one call)
            async with aiohttp.ClientSession() as session:
                # The actual request
                async with session.get(url) as response:
                    # Request successsful,
                    if response.status == 200:
                        # Parse the response as JSON data
                        data = await response.json()

                        # Assign the updated df cache to the empty df
                        self.gecko_df = pd.DataFrame(data)

                        # Log the successful population
                        print("Cache population successful.")

                    # If the request was not successful,
                    else:
                        # Log the error
                        print(f"Failed to retrieve coin data. Status code: {response.status}")  
            
    # Function to be called upon class initialization
    @commands.Cog.listener()                        
    async def on_ready(self):
        await self.populate_cache()

# Setup function to load the cog into the bot
async def setup(bot):
    try:
        await bot.add_cog(CacheCog(bot))
    except Exception as e:
        print(f"Error when loading cog: {e}")