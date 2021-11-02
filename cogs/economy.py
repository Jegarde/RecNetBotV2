import functions
import requests
import discord
import random
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType


class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.session = {}
        DiscordComponents(client)




def setup(client):
    client.add_cog(Economy(client))
