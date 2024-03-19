# Imports
import discord
from discord.ext import commands
import requests
import os
import aiohttp

# Create class
class PricesCog(commands.Cog):

    # Init method (set important variables)
    def __init__(self, bot):
        self.bot = bot 
        self.api_key = os.getenv('KEY')

    # Function to automatically fetch the price of any cryptocurrency
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

        # Send and HTTP request for the data
        response = requests.get(url, params=parameters, headers=headers)

        # HTTP request is successful, run following code
        if response.status_code == 200:
            # Parse the response as JSON data
            data = response.json()
            
            # Create the embed to hold the message
            embed = discord.Embed(
                title=f"{data['data'][symbol.upper()]['name']}",
                color=discord.Color.dark_purple()
            )

            # Find the price of the specified crypto and assign it to memory, next add this price to an f-string to add to embed field
            price = data['data'][symbol.upper()]['quote']['USD']['price']
            price_value_string = f"${price:,.2f}"

            # Add it to the embed
            embed.add_field(name="Price (USD):", value=price_value_string, inline=False)

            # Set a professional footer to the message
            embed.set_footer(text="Data retrieved from CoinMarketCap")

            # Send the message
            await ctx.send(embed=embed)
            
        else:
            # HTTP request is not successful, display error message
            await ctx.send(f"There was an error fetching the cryptocurrency list. Error Code: {response.status_code}")

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

            # Send and HTTP request for the data
            response = requests.get(url, params=parameters, headers=headers)

            # HTTP request is successful, run following code
            if response.status_code == 200:
                # Parse the response as JSON data
                data = response.json()

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
                    price_market_cap = f"Price: ${coin['quote']['USD']['price']:,.2f}\nMarket Cap: ${coin['quote']['USD']['market_cap']:,.0f}"
                    
                    # Each cryptocurrency is added as a new field
                    embed.add_field(name=name_symbol, value=price_market_cap, inline=False)

                # Set a professional footer to the message
                embed.set_footer(text="Data retrieved from CoinMarketCap")

                # Send the message
                await ctx.send(embed=embed)

            # HTTP request is not successful, display error message
            else:    
                await ctx.send(f"There was an error fetching the cryptocurrency list. Error Code: {response.status_code}")

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
                        embed.add_field(name="Invalid input", value="Cryptocurrency and id not found. Check your spelling and try again.", inline=False)

                        # Deliver
                        await ctx.send(embed=embed)

    # Test method for preview of embeded messages
    @commands.command()
    async def embed_test(self, ctx):
        embed = discord.Embed(
            title="Bitcoin (BTC)",
            description="Here's some info about Bitcoin\n(The below values are placeholders)",
            color=discord.Color.dark_purple()
        )

        # Adding various fields to the embed
        embed.add_field(name="Price", value="$40,000", inline=False)
        embed.add_field(name="Market Cap", value="$700B", inline=False)
        embed.add_field(name="24h Volume", value="$35B", inline=False)

        embed.set_footer(text="Data retrieved from CoinMarketCap")

        await ctx.send(embed=embed)

# Setup function to load the cog into the bot
async def setup(bot):
    try:
        await bot.add_cog(PricesCog(bot))
    except Exception as e:
        print(f"Error when loading cog: {e}")