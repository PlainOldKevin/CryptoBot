# Imports
import discord
from discord.ext import commands
import requests
import os

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

        # Return their prices in USD
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

    # Function to display top 5 cryptocurrencies by market cap (include symbol, name, price as well)
    @commands.command()
    async def top5(self, ctx):
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
            'limit': '5', 
            'convert': 'USD'
        }

        # Send and HTTP request for the data
        response = requests.get(url, params=parameters, headers=headers)

        # HTTP request is successful, run following code
        if response.status_code == 200:
            # Parse the response as JSON data
            data = response.json()

            # Create the embed to hold the message
            embed = discord.Embed(
                title="Top 5 Cryptocurrencies by Market Cap",
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