import functions
import discord
from discord.ext import commands

class Random(commands.Cog):
    def __init__(self, client):
        self.client = client
    # RANDOM COMMANDS

    # CMD-RANDOMBIO
    @commands.command()
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
            bio_list.append(functions.find_random_bio())


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
def setup(client):
    client.add_cog(Random(client))