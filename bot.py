# Imports
import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv
from tabulate import tabulate

# Initialize load-env for token accessing
load_dotenv()

# Store important values from .env in variables
BOT_TOKEN = os.getenv('TOKEN')
API_KEY = os.getenv('KEY')

# Add instance of discord client with intents
intents = discord.Intents.default()
intents.message_content = True

# Initialiaze bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Add on ready instance (when client is ready for use)
@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))

# Bot says hi to the user
@bot.command()
async def hello(ctx):
    await ctx.send("hi")

# Function to automatically fetch the price of any cryptocurrency in the top 50 by market cap
@bot.command()
async def price(ctx, symbol: str):
    # Fetch cryptocurrencies (sorted by market cap) with url below
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    
    # Headers for CoinMarketCap API authentication
    headers = { 
        'X-CMC_PRO_API_KEY': API_KEY,
        'Accepts': 'application/json'
    }

    # Only access the top 50 of those listings, and return their prices in USD
    parameters = {
        'start': '1',
        'limit': '50', 
        'convert': 'USD'
    }

    # Send and HTTP request for the data
    response = requests.get(url, params=parameters, headers=headers)

    # HTTP request is successful, run following code
    if response.status_code == 200:
        # Parse the response as JSON data
        data = response.json()
        # Create a list of the top 50 cryptocurrency symbols (by mkt cap) using comprehension
        top_50_symbols = [coin['symbol'] for coin in data['data']]
        
        # Check if the requested coin is in the top 50
        if symbol.upper() in top_50_symbols:
            # Fetch and display the price of the coin
            price_url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

            # Define params to query the url with
            price_parameters = {
                'symbol': symbol.upper(),
                'convert': 'USD'
            }
            
            # Get the response data and parse as JSON all on the same line
            price_response_data = requests.get(price_url, params=price_parameters, headers=headers).json()

            # Get the specific coin (by symbol) and price of that coin
            coin = price_response_data['data'][symbol.upper()]
            price = coin['quote']['USD']['price']

            # Output the data 
            await ctx.send(f"The current price of {symbol.upper()} is ${price:,.2f}")
        else:
            # Tell user their entry is not in the top 50 cryptos
            await ctx.send(f"{symbol.upper()} is not in the top 50 cryptocurrencies by market cap.")
    else:
        # HTTP request is not successful, display error message
        await ctx.send(f"There was an error fetching the cryptocurrency list. Error Code: {response.status_code}")

# Function to display top 5 cryptocurrencies by market cap (include symbol, name, price as well)
@bot.command()
async def top5(ctx):
    # Fetch cryptocurrencies (sorted by market cap) with url below
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    
    # Headers for CoinMarketCap API authentication
    headers = { 
        'X-CMC_PRO_API_KEY': API_KEY,
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
        # Create a list of the all the data to use later in the function
        top5_coins = data['data']

        # Header
        header = "**Top 5 Cryptocurrencies by Market Cap**\n"

        # Create a table for every coin in the top 5 using comprehension (for tabulate purposes)
        table_data = [ # Each coin's rank (by mkt cap), name, symbol, price (USD), and market cap (USD) added to table
            {
                'Rank': coin['cmc_rank'],
                'Name': coin['name'],
                'Symbol': coin['symbol'],
                'Price': f"${coin['quote']['USD']['price']:,.2f}",
                'Market Cap': f"${coin['quote']['USD']['market_cap']:,.0f}"
            }
            for coin in top5_coins # Said comprehension
        ]

        # Specify column alignment for first column (hard-code for a bug with left-aligning 'Rank' values)
        column_alignments = ('left',)
        # Create the table using tabulate
        table = tabulate(table_data, headers='keys', tablefmt='plain', stralign='left', colalign=column_alignments)
            
        # Send message
        await ctx.send(header)
        await ctx.send(f"```\n{table}\n```")
    
    # HTTP request is not successful, display error message
    else:    
        await ctx.send(f"There was an error fetching the cryptocurrency list. Error Code: {response.status_code}")

# Run the bot
bot.run(BOT_TOKEN)