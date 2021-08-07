import functions
import discord
import random
import asyncio
import requests
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType
from discord.ext import commands


class Beta(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.session_message = {}
        DiscordComponents(client)

    async def cosmetic_embed(self, item):
        bool_emjs = {
            "True": "✅",
            "False": "❌"
        }

        price = f"<:RRtoken:825288414789107762> `{item['Price']}`"
        rarity = '<:RRStar:825357537209090098>' * int(item['Rarity'])
        obtainable = f"{bool_emjs[str(item['Obtainable'])]} Obtainable?"
        rrplus = f"{bool_emjs[str(item['Premium'])]} RR+?"
        hideshair = f"{bool_emjs[str(item['HidesHair'])]} Hides hair?"
        obtainedfrom = f"Obtained from `{item['ObtainedBy']}`"
        slot = f"Slot: `{item['Type']}`"
        if item['ReleaseDate'] != "0000-00-00":
            release = f"📆 `{item['ReleaseDate'][8:10]}. {functions.months[item['ReleaseDate'][5:7]]} {item['ReleaseDate'][0:4]}`"
        else:
            release = f"📆 `UNKNOWN!`"

        em = discord.Embed(
            colour=discord.Colour.orange(),
            title=item["Name"],
            description=f"{price}\n{rarity}\n{release}\n{slot}\n{obtainedfrom}"
        )

        em.add_field(name="Details", value=f"{obtainable}\n{rrplus}\n{hideshair}", inline=False)

        if item['ImageName']:
            em.set_image(url=f"https://www.recdb.xyz/CDN/Images/{item['ImageName']}")
        else:
            em.set_image(url="https://i.imgur.com/paO6CDA.png")

        return em


    # CMD-COSMETIC
    @commands.command(aliases=['csearch'])
    @commands.check(functions.beta_tester)
    async def cosmeticsearch(self, ctx, *item_name):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        pure_name = ' '.join(item_name)
        item_name = '+'.join(item_name)

        if len(pure_name) < 3:
            em = functions.error_msg(ctx, "Name must be at least 3 chars long!")
            return await ctx.send(embed=em)

        r = requests.get(f"https://www.recdb.xyz/api/clothing/v1/search?contains={item_name}")
        if not r.ok:
            em = functions.error_msg(ctx, "Couldn't connect to RecDB.")
            return await ctx.send(embed=em)

        item_json = r.json()
        if not item_json:
            em = functions.error_msg(ctx, f"Couldn't find `{pure_name}`!")
            return await ctx.send(embed=em)

        item = item_json[0]
        em = await self.cosmetic_embed(item)

        functions.embed_footer(ctx, em)  # get default footer from function
        return await ctx.send(embed=em)

    @cosmeticsearch.error
    async def clear_error(self, ctx, error):
        raise error


    # CMD-COSMETICLIST
    @commands.command(aliases=['c'])
    @commands.check(functions.beta_tester)
    async def cosmetic(self, ctx, *item_name):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session
        pure_name = ' '.join(item_name)
        item_name = '+'.join(item_name)

        if len(pure_name) < 3:
            em = functions.error_msg(ctx, "Name must be at least 3 chars long!")
            return await ctx.send(embed=em)

        r = requests.get(f"https://www.recdb.xyz/api/clothing/v1/search?contains={item_name}")
        if not r.ok:
            em = functions.error_msg(ctx, "Couldn't connect to RecDB.")
            return await ctx.send(embed=em)

        item_json = r.json()
        if not item_json:
            em = functions.error_msg(ctx, f"Couldn't find `{pure_name}`!")
            return await ctx.send(embed=em)

        if len(item_json) == 1:
            return await self.cosmeticsearch(ctx, item_json[0]['Name'])

        catalog = "**Select item by sending the index!**\n*Catalog caps at 30 items.*\n"
        items = []
        temp_items = item_json[:30]
        for item in temp_items:
            items.append(item['Name'])
            catalog += f"{len(items)}. `{item['Name']}`\n"

        #functions.embed_footer(ctx, em)  #  get default footer from function
        m = await ctx.send(
            catalog
        )

        def check(m):
            return m.author == ctx.author and m.content.isdigit() and self.session_message[
                ctx.author.id] == m_session

        try:
            choice = await self.client.wait_for('message', check=check, timeout=30.0)
        except asyncio.TimeoutError:
            return await m.edit(content="Request timed out! <:RectNe:873328661590310922>")

        choice = int(choice.content)-1
        if len(items) > choice >= 0:
            await self.cosmeticsearch(ctx, items[choice])
        elif len(items) > choice <= 1:
            await self.cosmeticsearch(ctx, items[0])
        else:
            await self.cosmeticsearch(ctx, items[-1])

    @cosmetic.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an item!")

            await ctx.send(embed=embed)
        else:
            raise error


    # CMD-RANDOMCOSMETIC
    @commands.command(aliases=['rc'])
    @commands.check(functions.beta_tester)
    async def randomcosmetic(self, ctx, *item_name):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        r = requests.get(f"https://www.recdb.xyz/api/clothing/v1/search")
        if not r.ok:
            em = functions.error_msg(ctx, "Couldn't connect to RecDB.")
            return await ctx.send(embed=em)

        item_json = r.json()
        item = random.choice(item_json)
        em = await self.cosmetic_embed(item)

        functions.embed_footer(ctx, em)  # get default footer from function
        return await ctx.send(embed=em)

    @randomcosmetic.error
    async def clear_error(self, ctx, error):
        raise error


    # CMD-WEEKLY
    @commands.command(aliases=['w'])
    @commands.check(functions.beta_tester)
    async def weekly(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        r = requests.get("https://www.recdb.xyz/api/weekly/v1/current")
        if not r.ok:
            em = functions.error_msg(ctx, "Couldn't connect to RecDB.")
            return await ctx.send(embed=em)

        weekly = r.json()
        item = weekly['Reward']
        release = weekly['Date']
        challenges = "`\n`".join(weekly['Challenges'])
        em = discord.Embed(
            colour=discord.Colour.orange(),
            title=f"{weekly['Title']} ({release[8:10]}. {functions.months[release[5:7]]} {release[0:4]})"
        )

        em.add_field(name="Reward", value=f"Name: `{item['Name']}`\nItem: `{item['Item']}`", inline=False)
        em.add_field(name="Challenges", value="`" + challenges + "`", inline=False)
        em.set_image(url="https://i.imgur.com/paO6CDA.png")

        functions.embed_footer(ctx, em)  # get default footer from function
        return await ctx.send(embed=em)

    @weekly.error
    async def clear_error(self, ctx, error):
        raise error


def setup(client):
    client.add_cog(Beta(client))
