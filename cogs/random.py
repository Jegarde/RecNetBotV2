import functions
import discord
import random
import json
from discord.ext import commands

class Random(commands.Cog):
    def __init__(self, client):
        self.client = client
    # RANDOM COMMANDS

    # CMD-RANDOMBIO
    @commands.command(aliases=["rb"])
    @commands.check(functions.beta_tester)
    async def randombio(self, ctx, amount=1):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        
        author = f"<@{ctx.author.id}>"

        if amount > 5:
            amount = 5
        elif amount < 1:
            amount = 1

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            description = f"<a:spinning:803586183895580672> Searching for {amount} random bio(s)..."
        )
        functions.embed_footer(ctx, embed)
        loading = await ctx.send(embed=embed)

        bio_list = []

        for x in range(amount):
            bio = functions.find_random_bio()
            bio_list.append(bio)

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title = "Random bio(s)",
            description = "*username / display name / bio*"
        )

        # make fields for bios
        for x in bio_list:
            account_id = x["account_id"]
            username = functions.id_to_username(account_id)
            display_name = functions.id_to_display_name(account_id)
            bio = x["bio"]
            embed.add_field(name=f"👤 {username} ({display_name})", value=f"```{bio}```[🔗Profile](https://rec.net/user/{username})", inline=False)

        functions.embed_footer(ctx, embed) # get default footer from function
        await loading.delete()
        await ctx.send(author, embed=embed)

    # CMD-FASTRANDOMBIO
    @commands.command(aliases=["frb"])
    @commands.check(functions.beta_tester)
    async def fastrandombio(self, ctx, amount=1):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        
        author = f"<@{ctx.author.id}>"

        if amount > 5:
            amount = 5
        elif amount < 1:
            amount = 1

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title = "Random bio(s)",
            description = "*username / display name / bio*"
        )

        with open('randombio_list.json') as json_file: 
            data = json.load(json_file)
            for x in range(amount): 
                random_bio = random.randint(0, len(data)-1) 
                username = functions.id_to_username(data[random_bio]["account_id"])
                display_name = functions.id_to_display_name(data[random_bio]["account_id"])
                bio = data[random_bio]["bio"]
                embed.add_field(name=f"👤 {username} ({display_name})", value=f"```{bio}```[🔗Profile](https://rec.net/user/{username})", inline=False)

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(author, embed=embed)
def setup(client):
    client.add_cog(Random(client))