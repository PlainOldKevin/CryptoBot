# Imports
import os
import asyncio
import aiohttp
import pandas as pd

# Create class
class DataManager:

    # Init function 
    def __init__(self):
        self.gecko_df = None
        self.subscriptions_data = None
    
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

    # Function to get coin data from the df when called upon
    def get_coin_name(self, coin_name):                                  
        # Checks for the matching input from the user in the df and assigns that to a new df
        match = self.df_coins[self.df_coins['name'].lower() == coin_name.lower()]

        if not match.empty:                                             # If there is a match and the df is not empty after the previous code is executed
            return match.iloc[0]['id']                                  # Return the id from the Series in the df to the calling function
        else:
            return None
        
    # Function to get coin data from the df when called upon
    def get_coin_id(self, coin_id):                                  
        # Checks for the matching input from the user in the df and assigns that to a new df
        match = self.df_coins[self.df_coins['id'].lower() == coin_id.lower()]

        if not match.empty:                                             # If there is a match and the df is not empty after the previous code is executed
            return match.iloc[0]['id']                                  # Return the id from the Series in the df to the calling function
        else:
            return None