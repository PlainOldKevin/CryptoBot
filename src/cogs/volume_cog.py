# Imports
import discord
from discord.ext import commands
from decimal import *
import os
import aiohttp

# Create class
class VolumeCog(commands.Cog):

    # Init method (set important variables)
    def __init__(self, bot):
        self.bot = bot
        self.data_manager = bot.data_manager
        self.gecko_df = bot.data_manager.gecko_df
        self.api_key = os.getenv('KEY')
        self.gecko_key = os.getenv('GECKO_KEY')

    # Internal helper function for price display (to display prices below $0.01, instead of just `0.00`) to be used inside of other functions
    @staticmethod
    def format_crypto_price(price) -> str:
        # Check if the price exists
        if price is None:
            return "0"

        # Convert the price (from the CMC API call) to a Decimal object (instead of float. Gives us more precision instead of worrying about float rounding conventions)
        price = Decimal(str(price))
        
        # If price is >= $1.00, format with two decimal places and return (ezpz)
        if price >= Decimal('1.00'):
            return f"${price:,.2f}"
        # If price is between $1.00 and $0.01, show 4 decimal places exactly (ezpz)
        elif Decimal('1.00') > price >= Decimal('0.01'):
            # Format the price exactly as-is; cut off at 4 decimals
            formatted_price = f"${price.quantize(Decimal('0.0001'), rounding=ROUND_DOWN)}"
            # Return the price with no trailing zeros
            return formatted_price.rstrip('0')
        # If less than $0.01,
        else:
            # Define the number of digits to cut off the number at (to avoid overflow or Discord message errors) (I use 15 arbitrarily; beginning-string slicing is non-inclusive)
            MAX_DIGITS = 16

            # Convert the price to string (within the fixed-point context 'f') for further breakdown/analysis
            raw_price_str = format(price, 'f')

            # Extract the decimal portion out of the string (because we only care about the decimal here, being that the price is less than 1 cent)
            raw_decimal_str = raw_price_str.split('.')[1]

            # Create variable to store the first non-zero index in our decimal point (beyond the hundreths place obv)
            # Set to None as we do not know the first non-zero index yet
            non_zero_index = None
            
            # Use a for loop (with enumerate) to iterate over to 'digits' (characters) in our string to see if we can find a non-zero index in our first 15 indices
            for i, digit in enumerate(raw_decimal_str[:MAX_DIGITS], 1):
                # Check if digit is non-zero (remember, we are enumerating over a string!)
                if digit != '0':
                    # Store this non-zero index
                    non_zero_index = i
                    # Exit loop; we got what we need
                    break
            
            # If the number cannot be formatted, return None and handle the issue in the calling function
            if non_zero_index == None:
                return "0"

            # Otherwise,
            else:
                # Choose the number's display cutoff (using non_zero_index + 2 for context beyond just the one decimal place found; MAX_DIGITS for max-length arbitrary cutoff)
                displayed_sigfigs = min(non_zero_index + 2, MAX_DIGITS)
                # Format as string
                formatted_number = f"${price:.{displayed_sigfigs}f}"
                # And return
                return formatted_number

    # Function to get 24-hour volume of a coin by name
    @commands.command()
    async def vol24(self, ctx, name:str):
        # Check the user-inputted name for validity
        checked_name = self.data_manager.get_coin_name(name)

        # If no name found, try to find other name
        if checked_name == None:
            checked_name = await self.data_manager.get_corrected_name(ctx, name)

        # If none found after that, quit function
        if checked_name == None:
            return
        
        # Fetch cryptocurrencies with simple/price endpoint
        url = 'https://api.coingecko.com/api/v3/simple/price'
        
        # Headers for CoinGecko API authentication
        headers = { 
            'x-cg-demo-api-key': self.gecko_key,
        }
        
        # Parameters for the search to query the url
        parameters = { 
            'vs_currencies': 'usd',
            'ids': checked_name,
            'include_24hr_vol' : 'true',
        }
        
        # Asynchronously create a ClientSession (so the bot can make multiple HTTP calls and not get blocked from just one call)
        async with aiohttp.ClientSession() as session:
            # Make the aynchronous request to the api
            async with session.get(url, params=parameters, headers=headers) as response:
                # If request successsful,
                if response.status == 200:
                    # Parse the response as JSON data
                    crypto_data = await response.json()
                    
                    # Check if our parameter is in the response data,
                    if crypto_data and checked_name in crypto_data and 'usd_24h_vol' in crypto_data[checked_name] and crypto_data[checked_name]['usd_24h_vol'] is not None:

                        # Find the volume of the specified crypto and use the helper function that I spent 8 years on to format it
                        volume = self.format_crypto_price(crypto_data[checked_name]['usd_24h_vol'])

                        # Check if the volume is too small (or null) and create an embed
                        if volume == "0":

                            # Make a pretty embed for the user's unfortunate news
                            embed = discord.Embed(
                                title="ERROR",
                                color=0xC41E3A
                            )

                            # Add field with details
                            embed.add_field(name="Volume display error", value="The volume of this coin does not exist, or is too small to display. For more accurate results, visit [coingecko.com](https://www.coingecko.com/).", inline=False)

                            # Send the message
                            await ctx.send(embed=embed)

                        # If volume can be displayed,
                        else:
                            # Get the row of data in the df that holds the coin's info
                            df_row = self.gecko_df[self.gecko_df['id'] == checked_name].iloc[0]
                            # Get the name and id of the coin to display
                            coin_name = df_row['name']
                            coin_symbol = df_row['symbol']

                            # Create the embed to hold the message
                            embed = discord.Embed(
                                title=f"{coin_name} ({coin_symbol})",
                                color=discord.Color.dark_purple()
                            )

                            # Add it to the embed
                            embed.add_field(name="24h Volume (USD):", value=volume, inline=False)

                            # Set a professional footer to the message
                            embed.set_footer(text="Powered by CoinGecko")

                            # Send the message
                            await ctx.send(embed=embed)

                    # If id not in response data (user messed up)
                    else:
                        # Make a pretty embed for the user's unfortunate news
                        embed = discord.Embed(
                            title="ERROR",
                            color=0xC41E3A
                        )
                        
                        # Add field with details
                        embed.add_field(name="Cryptocurrency Data Not Found", value="The data for the provided cryptocurrency name is not available. For more information, visit [coingecko.com](https://www.coingecko.com/).", inline=False)

                        # Send the message
                        await ctx.send(embed=embed)
                
                # If the request was not successful,
                else:
                    # Make a pretty embed for the user's unfortunate news
                    embed = discord.Embed(
                        title="ERROR",
                        color=0xC41E3A
                    )

                    # Add field with details
                    embed.add_field(name="API Error", value="An error occurred while fetching the data from CoinGecko API. Please try again later.", inline=False)

                    # Send the message
                    await ctx.send(embed=embed)

    # Function to get 24-hour volume of a coin by id
    @commands.command()
    async def vol24id(self, ctx, id:str):
        # Check the user-inputted id for validity
        checked_id = self.data_manager.get_coin_id(id)

        # If no id found, try to find other id
        if checked_id == None:
            checked_id = await self.data_manager.get_corrected_id(ctx, id)

        # If none found after that, quit function
        if checked_id == None:
            return
        
        # Fetch cryptocurrencies with simple/price endpoint
        url = 'https://api.coingecko.com/api/v3/simple/price'
        
        # Headers for CoinGecko API authentication
        headers = { 
            'x-cg-demo-api-key': self.gecko_key,
        }
        
        # Parameters for the search to query the url
        parameters = { 
            'vs_currencies': 'usd',
            'ids': checked_id,
            'include_24hr_vol' : 'true',
        }
        
        # Asynchronously create a ClientSession (so the bot can make multiple HTTP calls and not get blocked from just one call)
        async with aiohttp.ClientSession() as session:
            # Make the aynchronous request to the api
            async with session.get(url, params=parameters, headers=headers) as response:
                # If request successsful,
                if response.status == 200:
                    # Parse the response as JSON data
                    crypto_data = await response.json()
                    
                    # Check if our parameter is in the response data,
                    if crypto_data and checked_id in crypto_data and 'usd_24h_vol' in crypto_data[checked_id] and crypto_data[checked_id]['usd_24h_vol'] is not None:

                        # Find the volume of the specified crypto and use the helper function that I spent 8 years on to format it
                        volume = self.format_crypto_price(crypto_data[checked_id]['usd_24h_vol'])

                        # Check if the volume is too small (or null) and create an embed
                        if volume == "0":

                            # Make a pretty embed for the user's unfortunate news
                            embed = discord.Embed(
                                title="ERROR",
                                color=0xC41E3A
                            )

                            # Add field with details
                            embed.add_field(name="Volume display error", value="The volume of this coin does not exist, or is too small to display. For more accurate results, visit [coingecko.com](https://www.coingecko.com/).", inline=False)

                            # Send the message
                            await ctx.send(embed=embed)

                        # If volume can be displayed,
                        else:
                            # Get the row of data in the df that holds the coin's info
                            df_row = self.gecko_df[self.gecko_df['id'] == checked_id].iloc[0]
                            # Get the name and id of the coin to display
                            coin_name = df_row['name']
                            coin_symbol = df_row['symbol']

                            # Create the embed to hold the message
                            embed = discord.Embed(
                                title=f"{coin_name} ({coin_symbol})",
                                color=discord.Color.dark_purple()
                            )

                            # Add it to the embed
                            embed.add_field(name="24h Volume (USD):", value=volume, inline=False)

                            # Set a professional footer to the message
                            embed.set_footer(text="Powered by CoinGecko")

                            # Send the message
                            await ctx.send(embed=embed)

                    # If id not in response data (user messed up)
                    else:
                        # Make a pretty embed for the user's unfortunate news
                        embed = discord.Embed(
                            title="ERROR",
                            color=0xC41E3A
                        )
                        
                        # Add field with details
                        embed.add_field(name="Cryptocurrency Data Not Found", value="The data for the provided cryptocurrency id is not available. For more information, visit [coingecko.com](https://www.coingecko.com/).", inline=False)

                        # Send the message
                        await ctx.send(embed=embed)
                
                # If the request was not successful,
                else:
                    # Make a pretty embed for the user's unfortunate news
                    embed = discord.Embed(
                        title="ERROR",
                        color=0xC41E3A
                    )

                    # Add field with details
                    embed.add_field(name="API Error", value="An error occurred while fetching the data from CoinGecko API. Please try again later.", inline=False)

                    # Send the message
                    await ctx.send(embed=embed)

    # Function to get a coin's total volume by name
    @commands.command()
    async def totalvol(self, ctx, name:str):
        # Check the user-inputted name for validity
        checked_name = self.data_manager.get_coin_name(name)

        # If no name found, try to find other name
        if checked_name == None:
            checked_name = await self.data_manager.get_corrected_name(ctx, name)

        # If none found after that, quit function
        if checked_name == None:
            return
        
        # Fetch cryptocurrencies with simple/price endpoint
        url = 'https://api.coingecko.com/api/v3/coins/markets'
        
        # Headers for CoinGecko API authentication
        headers = { 
            'x-cg-demo-api-key': self.gecko_key,
        }
        
        # Parameters for the search to query the url
        parameters = { 
            'vs_currency': 'usd',
            'ids': checked_name,
        }

        # Asynchronously create a ClientSession (so the bot can make multiple HTTP calls and not get blocked from just one call)
        async with aiohttp.ClientSession() as session:
            # Make the aynchronous request to the api
            async with session.get(url, params=parameters, headers=headers) as response:
                # If request successsful,
                if response.status == 200:
                    # Parse the response as JSON data
                    data = await response.json()

                    # Response data is dict in a list, so get the first item and assign to variable
                    crypto_data = data[0]

                    # Check if our response data exists, and holds data relevant to user return embed
                    if crypto_data and crypto_data['total_volume'] is not None:

                        # Find the volume of the specified crypto and use the helper function that I spent 8 years on to format it
                        volume = self.format_crypto_price(crypto_data['total_volume'])

                        # Check if the volume is too small (or null) and create an embed
                        if volume == "0":

                            # Make a pretty embed for the user's unfortunate news
                            embed = discord.Embed(
                                title="ERROR",
                                color=0xC41E3A
                            )

                            # Add field with details
                            embed.add_field(name="Volume display error", value="The volume of this coin does not exist, or is too small to display. For more accurate results, visit [coingecko.com](https://www.coingecko.com/).", inline=False)

                            # Send the message
                            await ctx.send(embed=embed)

                        # If volume can be displayed,
                        else:
                            # Get the row of data in the df that holds the coin's info
                            df_row = self.gecko_df[self.gecko_df['id'] == checked_name].iloc[0]
                            # Get the name and id of the coin to display
                            coin_name = df_row['name']
                            coin_symbol = df_row['symbol']

                            # Create the embed to hold the message
                            embed = discord.Embed(
                                title=f"{coin_name} ({coin_symbol})",
                                color=discord.Color.dark_purple()
                            )

                            # Add it to the embed
                            embed.add_field(name="Total Volume (USD):", value=volume, inline=False)

                            # Set a professional footer to the message
                            embed.set_footer(text="Powered by CoinGecko")

                            # Send the message
                            await ctx.send(embed=embed)

                    # If id not in response data (user messed up)
                    else:
                        # Make a pretty embed for the user's unfortunate news
                        embed = discord.Embed(
                            title="ERROR",
                            color=0xC41E3A
                        )
                        
                        # Add field with details
                        embed.add_field(name="Cryptocurrency Data Not Found", value="The data for the provided cryptocurrency name is not available. For more information, visit [coingecko.com](https://www.coingecko.com/).", inline=False)

                        # Send the message
                        await ctx.send(embed=embed)
                
                # If the request was not successful,
                else:
                    # Make a pretty embed for the user's unfortunate news
                    embed = discord.Embed(
                        title="ERROR",
                        color=0xC41E3A
                    )

                    # Add field with details
                    embed.add_field(name="API Error", value="An error occurred while fetching the data from CoinGecko API. Please try again later.", inline=False)

                    # Send the message
                    await ctx.send(embed=embed)

# Setup function to load the cog into the bot
async def setup(bot):
    try:
        await bot.add_cog(VolumeCog(bot))
    except Exception as e:
        print(f"Error when loading cog: {e}")