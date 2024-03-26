# Imports
import discord
from discord.ext import commands
from decimal import *
import os
import aiohttp

# Create class
class PricesCog(commands.Cog):

    # Init method (set important variables)
    def __init__(self, bot):
        self.bot = bot 
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

    # Function to automatically fetch the price of any cryptocurrency using its symbol as the arg
    @commands.command()
    async def price(self, ctx, symbol: str):
        # Fetch cryptocurrencies with url below
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        
        # Headers for CoinMarketCap API authentication
        headers = { 
            'X-CMC_PRO_API_KEY': self.api_key,
            'Accepts': 'application/json'
        }

        # Parameters for the search to query the url
        parameters = { 
            'convert': 'USD',
            'symbol': symbol.upper(),
        }

        # Asynchronously create a ClientSession (so the bot can make multiple HTTP calls and not get blocked from just one call) (really useful for big boy apps and bots)
        async with aiohttp.ClientSession() as session:
            # The actual request
            async with session.get(url, params=parameters, headers=headers) as response:
                # Request successsful,
                if response.status == 200:
                    # Parse the response as JSON data
                    data = await response.json()

                    # Check if symbol is in the response data (CMC API send 200s no matter what idk why)
                    if symbol.upper() in data['data']:

                        # Find the price of the specified crypto and use the helper function that I spent 8 years on to format it
                        price_value_string = self.format_crypto_price(data['data'][symbol.upper()]['quote']['USD']['price'])

                        # Check if the price is too small and create an embed
                        if price_value_string == "0":
                            # Make a pretty embed for the user's unfortunate news
                            embed = discord.Embed(
                                title="ERROR",
                                color=0xC41E3A
                            )

                            # Add field with details
                            embed.add_field(name="Price display error", value="The price of this coin is too small to display. For more accurate results, visit [coinmarketcap.com](https://coinmarketcap.com/)", inline=False)

                            # Send the message
                            await ctx.send(embed=embed)

                        # If price can be displayed,
                        else:
                            # Create the embed to hold the message
                            embed = discord.Embed(
                                title=f"{data['data'][symbol.upper()]['name']}",
                                color=discord.Color.dark_purple()
                            )

                            # Add it to the embed
                            embed.add_field(name="Price (USD):", value=price_value_string, inline=False)

                            # Set a professional footer to the message
                            embed.set_footer(text="Data retrieved from CoinMarketCap")

                            # Send the message
                            await ctx.send(embed=embed)

                    # If symbol not in response data (user messed up)
                    else:
                        # Make a pretty embed for the user's unfortunate news
                        embed = discord.Embed(
                            title="ERROR",
                            color=0xC41E3A
                        )

                        # Add field with details
                        embed.add_field(name="Cryptocurrency not found", value="The symbol you provided is not recognized. Please check the symbol and try again.", inline=False)

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
                    embed.add_field(name="Cryptocurrency not found", value="The symbol you provided is not recognized. Please check the symbol and try again.", inline=False)

                    # Send the message
                    await ctx.send(embed=embed)

    # Function to automatically fetch the price of any cryptocurrency using its (CoinGecko) id as the arg
    @commands.command()
    async def priceid(self, ctx, id: str):
        # Fetch cryptocurrencies with markets endpoint (provides some better data than simple/price endpoint)
        url = f'https://api.coingecko.com/api/v3/coins/markets'
        
        # Headers for CoinGecko API authentication
        headers = { 
            'x-cg-demo-api-key': self.gecko_key,
        }

        # Parameters for the search to query the url
        parameters = { 
            'vs_currency': 'usd',
            'ids': id,
            'precision': '15',
        }

        # Asynchronously create a ClientSession (so the bot can make multiple HTTP calls and not get blocked from just one call)
        async with aiohttp.ClientSession() as session:
            # Make the aynchronous request to the api
            async with session.get(url, params=parameters, headers=headers) as response:
                # If request successsful,
                if response.status == 200:
                    # Parse the response as JSON data
                    data = await response.json()

                    # Check if our parameter is in the response data,
                    if data:

                        # Reassign the JSON data to a variable for easier token access (because we GET a list of one dict)
                        crypto_data = data[0]

                        # Find the price of the specified crypto and use the helper function that I spent 8 years on to format it
                        price_value_string = self.format_crypto_price(crypto_data['current_price'])

                        # Check if the price is too small (or null) and create an embed
                        if price_value_string == "0":

                            # Make a pretty embed for the user's unfortunate news
                            embed = discord.Embed(
                                title="ERROR",
                                color=0xC41E3A
                            )

                            # Add field with details
                            embed.add_field(name="Price display error", value="The price of this coin does not exist, or is too small to display. For more accurate results, visit [coingecko.com](https://www.coingecko.com/).", inline=False)

                            # Send the message
                            await ctx.send(embed=embed)
                        # If price can be displayed,
                        else:

                            # Create the embed to hold the message
                            embed = discord.Embed(
                                title=f"{crypto_data['name']}",
                                color=discord.Color.dark_purple()
                            )

                            # Add it to the embed
                            embed.add_field(name="Price (USD):", value=price_value_string, inline=False)

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
                        embed.add_field(name="Cryptocurrency not found", value="The id you provided is not recognized. Please check the id and try again.", inline=False)

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
                    embed.add_field(name="API Error", value="An error occurred while fecthing the data from CoinGecko API. Please try again later.", inline=False)

                    # Send the message
                    await ctx.send(embed=embed)

    # Function to display custom (up to 10) amount of top cryptocurrencies by market cap (includes symbol, name, price as well)
    @commands.command()
    async def topcap(self, ctx, number: int):
        # Check if input is valid, proceed if so
        if 10 >= number >= 1:

            # Fetch cryptocurrencies (sorted by market cap) with url below
            url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
            
            # Headers for CoinMarketCap API authentication
            headers = { 
                'X-CMC_PRO_API_KEY': self.api_key,
                'Accepts': 'application/json'
            }

            # Only access the top 5 of those listings, and return their prices in USD
            parameters = {
                'start': '1',
                'limit': number, 
                'convert': 'USD'
            }

            # Asynchronously create a ClientSession (so the bot can make multiple HTTP calls and not get blocked from just one call)
            async with aiohttp.ClientSession() as session:
                # The actual request
                async with session.get(url, params=parameters, headers=headers) as response:
                    # Request successsful,
                    if response.status == 200:
                        # Parse the response as JSON data
                        data = await response.json()

                        # Check user input before we create embed (for accurate grammar in title)
                        if number == 1:
                            title = "Top Cryptocurrency by Market Cap"
                        else:
                            title = f"Top {str(number)} Cryptocurrencies by Market Cap"

                        # Create the embed to hold the message
                        embed = discord.Embed(
                            title=title,
                            color=discord.Color.dark_purple()
                        )

                        # Iterate through every value in the JSON data (each coin's data)
                        for coin in data['data']:
                            # Add name and symbol to one field; price and market cap in another
                            name_symbol = f"{coin['cmc_rank']}. {coin['name']} ({coin['symbol']})"
                            price_market_cap = f"Price: {self.format_crypto_price(coin['quote']['USD']['price'])}\nMarket Cap: ${coin['quote']['USD']['market_cap']:,.0f}"
                            
                            # Each cryptocurrency is added as a new field
                            embed.add_field(name=name_symbol, value=price_market_cap, inline=False)

                            # Set a professional footer to the message
                            embed.set_footer(text="Data retrieved from CoinMarketCap")

                        # Send the message
                        await ctx.send(embed=embed)

                    # HTTP request is not successful, display error message
                    else:
                        # Make a pretty embed for the user's unfortunate news
                        embed = discord.Embed(
                            title="ERROR",
                            color=0xC41E3A
                        )

                        # Add the bad news
                        embed.add_field(name="There was an error fetching the cryptocurrency list", value=f"Error Code: {response.status_code}", inline=False)

                        # Deliver
                        await ctx.send(embed=embed)

        # If the user input was invalid, tell the user to try again
        else:
            # Make a pretty embed for the user's unfortunate news
            embed = discord.Embed(
                title="ERROR",
                color=0xC41E3A
            )

            # Add the bad news
            embed.add_field(name="Invalid input", value="Please enter a valid input (1-10)", inline=False)

            # Deliver
            await ctx.send(embed=embed)

    # Function to display the 'id' value of a specific coin from CMC API
    @commands.command()
    async def id(self, ctx, name: str):
        # Fetch specified crypto using this url + extension (it has every crypto easily accessible) 
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map'

        # Headers for CoinMarketCap API authentication
        headers = { 
            'X-CMC_PRO_API_KEY': self.api_key,
            'Accepts': 'application/json'
        }

        # Asynchronously create a ClientSession (so the bot can make multiple HTTP calls and not get blocked from just one call)
        async with aiohttp.ClientSession() as session:
            # The actual request
            async with session.get(url, headers=headers) as response:
                # Request successsful,
                if response.status == 200:
                    # Parse the response as JSON data
                    data = await response.json()

                    # Search for id in crypto map (so efficient and amazing omg I defintely don't wish there was a better way to do this!)
                    crypto_id = next((item for item in data['data'] if item['name'].lower() == name.lower()), None)

                    # Create logic for crypto being found in map
                    if crypto_id:

                        # Create the embed to hold the message
                        embed = discord.Embed(
                            title="Coin-Specific CMC API id",
                            color=discord.Color.dark_purple()
                        )

                        # Add info to embed
                        embed.add_field(name=f"{crypto_id['name']} id:", value=f"{crypto_id['id']}", inline=False)

                        # Add footer to embed
                        embed.set_footer(text="Data retrieved from CoinMarketCap")

                        # Send message
                        await ctx.send(embed=embed)
                    
                    # If crypto not found in map,
                    else:
                        # Make a pretty embed for the user's unfortunate news
                        embed = discord.Embed(
                            title="ERROR",
                            color=0xC41E3A
                        )

                        # Add the bad news
                        embed.add_field(name="Invalid input", value="The cryptocurrency you provided is not recognized. Please check the spelling and try again.", inline=False)

                        # Deliver
                        await ctx.send(embed=embed)

# Setup function to load the cog into the bot
async def setup(bot):
    try:
        await bot.add_cog(PricesCog(bot))
    except Exception as e:
        print(f"Error when loading cog: {e}")