from flask import Flask
import discord,json, datetime,mysql.connector
from discord import Intents

app = Flask(__name__)


@app.route("/")
def home():
    intents = Intents.all()
    intents.typing = False
    intents.members = True
    client = discord.Client(intents=intents)

    return "Estamos con el cliente activo"


@app.route("/about")
def about():
    return "About"
