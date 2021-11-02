import functions
import requests
import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType


class API(commands.Cog):
    def __init__(self, client):
        self.client = client

    # API COMMANDS

    # CMD-ACCOUNTID
    @commands.command()
    @commands.check(functions.beta_tester)
    async def accountid(self, ctx, account_id: int):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        try:
            account = requests.get(
                f"https://accounts.rec.net/account/{account_id}").json()
            embed = discord.Embed(colour=discord.Colour.orange())
            embed.set_author(name=f"🔗 {account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}",
                             icon_url=functions.id_to_pfp(
                                 account['accountId'], True))
            for item in account:
                embed.add_field(name=item, value=f"`{account[item]}`",inline=False)

        except:  # account doesn't exist
            embed = functions.error_msg(
                ctx, f"User not found with the account id `{account_id}`.")

        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(embed=embed)

    @accountid.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an account id!")

            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = functions.error_msg(ctx, "Account id's are digits!")

            await ctx.send(embed=embed)
        else:
            pass

    # CMD-ACCOUNTDATA
    @commands.command()
    @commands.check(functions.beta_tester)
    async def accountdata(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if account:
            account = requests.get(
                f"https://accounts.rec.net/account/{account['account_id']}"
            ).json()
            embed = discord.Embed(colour=discord.Colour.orange())
            embed.set_author(name=f"🔗 {account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}",
                             icon_url=functions.id_to_pfp(
                                 account['accountId'], True))
            for item in account:
                embed.add_field(name=item,
                                value=f"`{account[item]}`",
                                inline=False)

        else:  # account doesn't exist
            embed = functions.error_msg(ctx,
                                        f"User `@{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(embed=embed)

    @accountdata.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")

            await ctx.send(embed=embed)
        else:
            pass

    #CMD-IMAGEID
    @commands.command()
    @commands.check(functions.beta_tester)
    async def imageid(self, ctx, image_id: int):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        try:
            image_data = requests.get(
                f"https://api.rec.net/api/images/v4/{image_id}").json()
            embed = discord.Embed(colour=discord.Colour.orange())
            username = functions.id_to_username(image_data['PlayerId'])
            embed.set_author(name=f"🔗 {username}'s profile",
                             url=f"https://rec.net/user/{username}",
                             icon_url=functions.id_to_pfp(
                                 image_data['PlayerId'], True))
            for item in image_data:
                embed.add_field(name=item,
                                value=f"`{image_data[item]}`",
                                inline=False)
            embed.set_image(
                url=f"https://img.rec.net/{image_data['ImageName']}")
        except:
            embed = functions.error_msg(
                ctx, f"Image not found with the id `{image_id}`")
        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(embed=embed)

    @imageid.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(
                ctx,
                "Please include in an image id!\nExample: rec.net/image/`55947515`"
            )

            await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = functions.error_msg(ctx, "Image id's are digits!")

            await ctx.send(embed=embed)
        else:
            pass

    # CMD-roomid
    @commands.command()
    @commands.check(functions.beta_tester)
    async def roomid(self, ctx, room):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        room_data = functions.id_to_room_data(room)
        if not room_data:
            embed = functions.error_msg(ctx, f"Room with the id `{room}` doesn't exist!")
            return await ctx.send(embed=embed)

        embed = discord.Embed(colour=discord.Colour.orange())
        count = 0
        for item in room_data:
            if count == 25:
                await ctx.send(embed=embed)
                embed = discord.Embed(colour=discord.Colour.orange())
                count = 0
            em_value = str(room_data[item])
            em_value = em_value.replace("'", "\"")
            em_value = em_value.replace("None", "null")
            em_value = em_value.replace("True", "true")
            em_value = em_value.replace("False", "false")
            if len(em_value) > 6000:
                embed.add_field(name=item, value=f"```Too much data to handle!```", inline=False)
            else:
                embed.add_field(name=item, value=f"```json\n{em_value}```", inline=False)
            count += 1

        if count:
            await ctx.send(
                embed=embed,
                components=[
                    [
                        Button(style=ButtonStyle.URL, label="Room Link",
                               url=f"https://rec.net/room/{room_data['Name']}"),
                        Button(style=ButtonStyle.URL, label="Creator Link",
                               url=f"https://rec.net/user/{functions.id_to_username(room_data['CreatorAccountId'])}")
                    ]
                ]
            )

    @roomid.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in a room id!")

            await ctx.send(embed=embed)
        else:
            raise error

    # CMD-roomdata
    @commands.command()
    @commands.check(functions.beta_tester)
    async def roomdata(self, ctx, room):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        room_data = functions.name_to_room_data(room)
        if not room_data:
            embed = functions.error_msg(ctx, f"Room `^{room}` doesn't exist!")
            return await ctx.send(embed=embed)

        embed = discord.Embed(colour=discord.Colour.orange())
        count = 0
        for item in room_data:
            if count == 25:
                await ctx.send(embed=embed)
                embed = discord.Embed(colour=discord.Colour.orange())
                count = 0
            em_value = str(room_data[item])
            em_value = em_value.replace("'", "\"")
            em_value = em_value.replace("None", "null")
            em_value = em_value.replace("True", "true")
            em_value = em_value.replace("False", "false")
            if len(em_value) > 6000:
                embed.add_field(name=item, value=f"```Too much data to handle!```", inline=False)
            else:
                embed.add_field(name=item, value=f"```json\n{em_value}```", inline=False)
            count += 1

        if count:
            await ctx.send(
                embed=embed,
                components=[
                    [
                        Button(style=ButtonStyle.URL, label="Room Link",
                               url=f"https://rec.net/room/{room_data['Name']}"),
                        Button(style=ButtonStyle.URL, label="Creator Link",
                               url=f"https://rec.net/user/{functions.id_to_username(room_data['CreatorAccountId'])}")
                    ]
                ]
            )

    @roomdata.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in a room name!")

            await ctx.send(embed=embed)
        else:
            raise error



def setup(client):
    client.add_cog(API(client))
