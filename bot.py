# Imports
import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

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

            
            coin = price_response_data['data'][symbol.upper()]
            price = coin['quote']['USD']['price']
            await ctx.send(f"The current price of {symbol.upper()} is ${price:.2f}")
        else:
            await ctx.send(f"{symbol.upper()} is not in the top 50 cryptocurrencies by market cap.")
    else:
        # HTTP request is not successful, display error message
        await ctx.send(f"There was an error fetching the cryptocurrency list. Error Code: {response.status_code}")

# Run the bot
bot.run(BOT_TOKEN)