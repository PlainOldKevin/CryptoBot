# Imports
import discord
from discord.ext import commands
import asyncio
import aiohttp
import pandas as pd
from rapidfuzz import process

# Create class
class DataManager:

    # Init function 
    def __init__(self):
        self.gecko_df = pd.DataFrame()
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
    def get_coin_name(self, coin_name) -> str:         
        # Checks for the matching input from the user in the df and assigns that to a new df
        match = self.gecko_df[self.gecko_df['name'].str.lower() == coin_name.lower()]

        if not match.empty:                                             # If there is a match and the df is not empty after the previous code is executed
            return match.iloc[0]['id']                                  # Return the id from the Series in the df to the calling function
        else:
            return None
        
    # Function to get coin data from the df when called upon
    def get_coin_id(self, coin_id) -> str:                                  
        # Checks for the matching input from the user in the df and assigns that to a new df
        match = self.gecko_df[self.gecko_df['id'].str.lower() == coin_id.lower()]

        if not match.empty:                                             # If there is a match and the df is not empty after the previous code is executed
            return match.iloc[0]['id']                                  # Return the id from the Series in the df to the calling function
        else:
            return None
        
    # Function to search through the database if the user gets a name wrong
    async def get_corrected_name(self, ctx, coin_name) -> str:
        # Create a lowercase list to compare user input to
        lowercase_name_list = [name.lower() for name in self.gecko_df['name'].tolist()]
        # Get top 3 similar values in the gecko_df compared to the coin_name arg (return as list of tuples based on fuzzywuzzy similarity score)
        similar_coins = process.extract(coin_name.lower(), lowercase_name_list, limit=3)

        # Create an embed for the user to read their options and choose the next course of action
        embed = discord.Embed(
            title="Similar Coins",
            description=f"Sorry, I didn't find a match for '{coin_name}'. Perhaps you meant one of these? (Enter the number that corresponds with your desired selection. Enter 'q' to quit).",
            color=discord.Color.dark_purple()
        )

        # Create for loop to add coins from similar_coins list into embed
        for i, (similar_name, score, idx) in enumerate(similar_coins, start=1):
            original_name_row = self.gecko_df[self.gecko_df['name'].str.lower() == similar_name].iloc[0] # Get the normal-case version of each respective coin's row in the df
            original_name = original_name_row['name'] # Isolate the name for readability and modularity
            symbol = original_name_row['symbol']      # Isolate the symbol to be put into the embed
            embed.add_field(name=f"{i}. {original_name} ({symbol})", value="\u200b", inline=False) # Add field with info to embed

        # Add footer and send embed
        embed.set_footer(text="Powered by CoinGecko")
        await ctx.send(embed=embed)

        # Function to check the user's response
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        
        # Handle the user's response
        try: 
            msg = await ctx.bot.wait_for('message', check=check, timeout=30)                      # Check the message
            # If the message is 'q',
            if msg.content.lower() == 'q':        
                # Create an embed for user bad input
                embed = discord.Embed(
                    title="Function Termination",
                    description="Quitting execution.",
                    color=0xC41E3A
                )

                # Send embed
                await ctx.send(embed=embed)

                return None
            
            # Else,
            choice = int(msg.content)                                                             # Turn message into an int
            if 1 <= choice <= len(similar_coins):                                                 # Check message's validity
                ans = similar_coins[choice - 1][0]                                                # Return corresponding coin data
                return self.gecko_df.loc[self.gecko_df['name'].str.lower() == ans, 'id'].iloc[0]  # Return the id that corresponds with that coin name
            else:
                # Create an embed for user bad input
                embed = discord.Embed(
                    title="ERROR",
                    description="Invalid input. Quitting execution.",
                    color=0xC41E3A
                )

                # Send embed
                await ctx.send(embed=embed)

                return None
        # User took too long
        except TimeoutError:
            # Create an embed for user taking too long and being out of options
            embed = discord.Embed(
                title="ERROR",
                description="Function timeout. No answer within 20 seconds. Quitting execution.",
                color=0xC41E3A
            )

            # Send embed
            await ctx.send(embed=embed)

            return None
        # Bad input
        except ValueError:
            # Create an embed for user bad input
            embed = discord.Embed(
                title="ERROR",
                description="Invalid input. Quitting execution.",
                color=0xC41E3A
            )

            # Send embed
            await ctx.send(embed=embed)
            return None
        
    # Function to search through the database if the user gets an id wrong
    async def get_corrected_id(self, ctx, coin_id) -> str:
        # Create a lowercase list to compare user input to
        lowercase_name_list = [id.lower() for id in self.gecko_df['id'].tolist()]
        # Get top 3 similar values in the gecko_df compared to the coin_name arg (return as list of tuples based on fuzzywuzzy similarity score)
        similar_coins = process.extract(coin_id.lower(), lowercase_name_list, limit=3)

        # Create an embed for the user to read their options and choose the next course of action
        embed = discord.Embed(
            title="Similar Coins",
            description=f"Sorry, I didn't find a match for '{coin_id}'. Perhaps you meant one of these? (Enter the number that corresponds with your desired selection. Enter 'q' to quit).",
            color=discord.Color.dark_purple()
        )

        # Create for loop to add coins from similar_coins list into embed
        for i, (similar_id, score, idx) in enumerate(similar_coins, start=1):
            original_id_row = self.gecko_df[self.gecko_df['id'].str.lower() == similar_id].iloc[0] # Get the normal-case version of each respective coin's row in the df
            original_id = original_id_row['id'] # Isolate the name for readability and modularity
            symbol = original_id_row['symbol']      # Isolate the symbol to be put into the embed
            embed.add_field(name=f"{i}. {original_id} ({symbol})", value="\u200b", inline=False) # Add field with info to embed

        # Add footer and send embed
        embed.set_footer(text="Powered by CoinGecko")
        await ctx.send(embed=embed)

        # Function to check the user's response
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel
        
        # Handle the user's response
        try: 
            msg = await ctx.bot.wait_for('message', check=check, timeout=30)                    # Check the message
            # If the message is 'q',
            if msg.content.lower() == 'q':        
                # Create an embed for user bad input
                embed = discord.Embed(
                    title="Function Termination",
                    description="Quitting execution.",
                    color=0xC41E3A
                )

                # Send embed
                await ctx.send(embed=embed)

                return None
            
            # Else,
            choice = int(msg.content)                                                             # Turn message into an int
            if 1 <= choice <= len(similar_coins):                                                 # Check message's validity
                ans = similar_coins[choice - 1][0]                                                # Return corresponding coin data
                return self.gecko_df.loc[self.gecko_df['id'].str.lower() == ans, 'id'].iloc[0]  # Return the id that corresponds with that coin name
            else:
                # Create an embed for user bad input
                embed = discord.Embed(
                    title="ERROR",
                    description="Invalid input. Quitting execution.",
                    color=0xC41E3A
                )

                # Send embed
                await ctx.send(embed=embed)

                return None
        # User took too long
        except TimeoutError:
            # Create an embed for user taking too long and being out of options
            embed = discord.Embed(
                title="ERROR",
                description="Function timeout. No answer within 20 seconds. Quitting execution.",
                color=0xC41E3A
            )

            # Send embed
            await ctx.send(embed=embed)

            return None
        # Bad input
        except ValueError:
            # Create an embed for user bad input
            embed = discord.Embed(
                title="ERROR",
                description="Invalid input. Quitting execution.",
                color=0xC41E3A
            )

            # Send embed
            await ctx.send(embed=embed)
            return None