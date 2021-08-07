import functions
import discord
from discord.ext import commands

class Other(commands.Cog):
    def __init__(self, client):
        self.client = client

    # CMD-DOC
    @commands.command()
    @commands.check(functions.beta_tester)
    async def doc(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title = "Unofficial documentation of RecNet API, made by ColinXYZ",
            description = "[Documentation Link](https://documenter.getpostman.com/view/13848200/TVt184DN)"
        )

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)


    # CMD-INVITE
    @commands.command()
    @commands.check(functions.beta_tester)
    async def invite(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title = "🔗 Invitation links!",
            description = "<:discord:803539862435135510> [Test server](https://discord.gg/GPVdhMa2zK)\n<:BotGraffiti:803539486930763786> [Bot invite link](https://discord.com/api/oauth2/authorize?client_id=788632031835324456&permissions=322624&scope=bot)"
        )

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    #CMD-CRINGEBIOS
    @commands.command()
    async def cringebios(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        with open("cringe_bios.json", "rb") as bios:
            await ctx.send(file=discord.File(bios, "Cringe bio list.json"))

def setup(client):
    client.add_cog(Other(client))
