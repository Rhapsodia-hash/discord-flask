from flask import Flask

import discord

app = Flask(__name__)


@app.route("/")
def home():
    intents = Intents.all()
    intents.typing = False
    intents.members = True
    client = discord.Client(intents=intents)

    return client


@app.route("/about")
def about():
    return "About"
