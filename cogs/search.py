import functions
import discord
from discord.ext import commands

class Search(commands.Cog):
    def __init__(self, client):
        self.client = client

    # SEARCH COMMANDS



def setup(client):
    client.add_cog(Search(client))