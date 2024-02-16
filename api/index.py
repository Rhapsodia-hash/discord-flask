from flask import Flask
from discord.ext import commands
from discord import Intents
import discord

app = Flask(__name__)


@app.route("/")
def home():
    intents = Intents.all()
    intents.typing = False
    intents.members = True
    client = discord.Client(intents=intents)

    return "Hello, World!"


@app.route("/about")
def about():
    return "About"
