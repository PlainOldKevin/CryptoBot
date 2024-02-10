# Imports
from flask import Flask
from threading import Thread

# Initiliaze app to be kept alive
app = Flask('/')

@app.route('/')
def home():
    return "CryptoBot is running"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()