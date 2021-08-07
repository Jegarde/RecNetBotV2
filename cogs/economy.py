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

    @commands.command()
    async def unbox(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        session = random.randint(0, 999999)
        self.session[ctx.author.id] = session

        em = discord.Embed(
            title="Choose a reward!",
            color=0x2f3136
        )

        await ctx.send(
            embed=em,
            components=[
                [
                    Button(style=ButtonStyle.red, label="1"),
                    Button(style=ButtonStyle.red, label="2"),
                    Button(style=ButtonStyle.red, label="3")
                ]
            ]
        )

    @unbox.error
    async def on_command_error(self, ctx, error):
        raise error


def setup(client):
    client.add_cog(Economy(client))
