import functions
import requests
import discord
import asyncio
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client
    # UTILITY COMMANDS

    # CMD-BIO
    @commands.command()
    @commands.check(functions.beta_tester)
    async def bio(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if account:
            bio = functions.get_bio(account['account_id'])
            pfp = functions.id_to_pfp(account['account_id'], True)

            print(f"{ctx.command} > {account['account_id']}, {account['username']}, {bio}, {pfp}")

            embed=functions.default_embed()
            embed.add_field(name=f"{account['username']}'s bio:", value=f"```{bio}```")
            embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=pfp)
        else:
            embed = functions.error_msg(ctx, f"User `{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @bio.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass

    # CMD-PFP
    @commands.command()
    @commands.check(functions.beta_tester)
    async def pfp(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if account:
            pfp = functions.id_to_pfp(account['account_id'], False)

            print(f"{ctx.command} > {account['account_id']}, {account['username']}, {pfp}")

            embed=discord.Embed(
                colour=discord.Colour.orange(),
                description = f"[{account['username']}'s profile picture](https://rec.net/image/{functions.id_to_pfp(account['account_id'], False, False)})"
            )
            embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=functions.id_to_pfp(account['account_id'], True))
            embed.set_image(url=pfp)
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @pfp.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass


    # CMD-BANNER
    @commands.command()
    @commands.check(functions.beta_tester)
    async def banner(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if account:
            banner = functions.id_to_banner(account['account_id'], True)

            print(f"{ctx.command} > {account['account_id']}, {account['username']}, {banner}")

            if not banner:
                embed=discord.Embed(
                    colour=discord.Colour.orange(),
                    description = f"{account['username']}'s banner"
                )
                banner = "https://cdn.rec.net/static/banners/default_player.png" # replace with default banner
            else:
                embed=discord.Embed(
                    colour=discord.Colour.orange(),
                    description = f"[{account['username']}'s banner](https://rec.net/image/{functions.id_to_banner(account['account_id'], False)})"
                )
            embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=functions.id_to_pfp(account['account_id']))
            embed.set_image(url=banner)
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `{profile}` doesn't exist!")
        
        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @banner.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass


    # CMD-PROFILE
    @commands.command()
    @commands.check(functions.beta_tester)
    async def profile(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if account:
            display_name = functions.id_to_display_name(account['account_id'])
            pfp = functions.id_to_pfp(account['account_id'], False)
            bio = functions.get_bio(account['account_id'])
            created_at = functions.id_to_creation_date(account['account_id'])
            is_junior = functions.id_to_is_junior(account['account_id'])

            print(f"{ctx.command} > {account['account_id']}, {account['username']}, {display_name}, {pfp}, {bio}, {created_at}, {is_junior}")

            embed=discord.Embed(
                colour=discord.Colour.orange()
            )
            embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=functions.id_to_pfp(account['account_id'], True))
            embed.add_field(name="Display name", value=f"`{display_name}`", inline=True)
            embed.add_field(name="Created at", value=f"`{created_at[:10]}`", inline=True)
            embed.add_field(name="Is junior?", value=f"`{is_junior}`", inline=True)
            embed.add_field(name="Bio", value=f"```{bio}```", inline=False)
            embed.set_image(url=pfp)
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @profile.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass

    # CMD-JUNIOR
    @commands.command()
    @commands.check(functions.beta_tester)
    async def junior(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if account:
            is_junior = functions.id_to_is_junior(account['account_id'])

            print(f"{ctx.command} > {account['account_id']}, {account['username']}, {is_junior}")

            if is_junior:
                title = f"{account['username']} is a junior! 🧒"
            else:
                title = f"{account['username']} is not junior! 🧔"

            embed=discord.Embed(
                colour=discord.Colour.orange(),
                title = title
            )
            embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=functions.id_to_pfp(account['account_id'], True))
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @junior.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass

    # CMD-DATE
    @commands.command()
    @commands.check(functions.beta_tester)
    async def date(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if account:
            created_at = functions.id_to_creation_date(account['account_id'])

            print(f"{ctx.command} > {account['account_id']}, {account['username']}, {created_at}")

            embed=discord.Embed(
                colour=discord.Colour.orange(),
                title = f"{account['username']}'s account was created at",
                description = f"📆 `{created_at[:10]}`\n⏰ `{created_at[11:16]} UTX`"
            )
            embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=functions.id_to_pfp(account['account_id'], True))
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @date.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass
    

    # CMD-NICKNAME
    @commands.command()
    @commands.check(functions.beta_tester)
    async def nickname(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if account:
            display_name = functions.id_to_display_name(account['account_id'])

            print(f"{ctx.command} > {account['account_id']}, {account['username']}, {display_name}")

            embed=discord.Embed(
                colour=discord.Colour.orange(),
                title=f"{account['username']}'s display name is",
                description=f"`{display_name}`"
            )
            embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=functions.id_to_pfp(account['account_id'], True))
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @nickname.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass


    # CMD-LATEST
    @commands.command()
    @commands.check(functions.beta_tester)
    async def latest(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if account:
            latest = functions.id_to_latest_photo(account['account_id'])
            if latest:
                tagged = ""
                if latest['TaggedPlayerIds']:
                    tagged = "👥 "
                    for account_id in latest['TaggedPlayerIds']:
                        username = functions.id_to_username(account_id)
                        tagged += f"[`@{username}`](https://rec.net/user/{username}) "

                room_name = functions.id_to_room_name(latest['RoomId'])
                embed=discord.Embed(
                    colour=discord.Colour.orange(),
                    description=f"🔗 **[{account['username']}'s latest picture](https://rec.net/image/{latest['Id']})**\n🚪 [`^{room_name}`](https://rec.net/room/{room_name})\n<:CheerGeneral:803244099510861885> `{latest['CheerCount']}` 💬 `{latest['CommentCount']}`\n📆 `{latest['CreatedAt'][:10]}` ⏰ `{latest['CreatedAt'][11:16]} UTX`\n{tagged}"
                )
                embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=functions.id_to_pfp(account['account_id'], True))
                embed.set_image(url=f"http://img.rec.net/{latest['ImageName']}")
            else:
                print(f"{ctx.command} > {account['account_id']}, {account['username']}, Latest not found!")
                embed = functions.error_msg(ctx, f"User `{account['username']}` hasn't shared any pictures!")
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @latest.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass

    # CMD-OLDEST
    @commands.command()
    @commands.check(functions.beta_tester)
    async def oldest(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if account:
            oldest = functions.id_to_oldest_photo(account['account_id'])
            if oldest:
                tagged = ""
                if oldest['TaggedPlayerIds']:
                    tagged = "👥 "
                    for account_id in oldest['TaggedPlayerIds']:
                        username = functions.id_to_username(account_id)
                        tagged += f"[`@{username}`](https://rec.net/user/{username}) "
                room_name = functions.id_to_room_name(oldest['RoomId'])
                embed=discord.Embed(
                    colour=discord.Colour.orange(),
                    description=f"🔗 **[{account['username']}'s oldest picture](https://rec.net/image/{oldest['Id']})**\n🚪 [`^{room_name}`](https://rec.net/room/{room_name})\n<:CheerGeneral:803244099510861885> `{oldest['CheerCount']}` 💬 `{oldest['CommentCount']}`\n📆 `{oldest['CreatedAt'][:10]}` ⏰ `{oldest['CreatedAt'][11:16]} UTX`\n{tagged}"
                )
                embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=functions.id_to_pfp(account['account_id'], True))
                embed.set_image(url=f"http://img.rec.net/{oldest['ImageName']}")
            else:
                print(f"{ctx.command} > {account['account_id']}, {account['username']}, Oldest not found!")
                embed = functions.error_msg(ctx, f"User `{account['username']}` hasn't shared any pictures!")
        else:
            embed = functions.error_msg(ctx, f"User `{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @oldest.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass

    # CMD-OLDESTFEED
    @commands.command()
    @commands.check(functions.beta_tester)
    async def oldestfeed(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)

        if account:
            oldestfeed = functions.id_to_oldest_feed(account['account_id'])
            if oldestfeed:
                tagged = ""
                if oldestfeed['TaggedPlayerIds']:
                    tagged = "👥 "
                    for account_id in oldestfeed['TaggedPlayerIds']:
                        username = functions.id_to_username(account_id)
                        tagged += f"[`@{username}`](https://rec.net/user/{username}) "
                room_name = functions.id_to_room_name(oldestfeed['RoomId'])
                embed=discord.Embed(
                    colour=discord.Colour.orange(),
                    description=f"🔗 **[{account['username']}'s oldest appearance](https://rec.net/image/{oldestfeed['Id']})**\n🚪 [`^{room_name}`](https://rec.net/room/{room_name})\n<:CheerGeneral:803244099510861885> `{oldestfeed['CheerCount']}` 💬 `{oldestfeed['CommentCount']}`\n📆 `{oldestfeed['CreatedAt'][:10]}` ⏰ `{oldestfeed['CreatedAt'][11:16]} UTX`\n{tagged}"
                )
                embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=functions.id_to_pfp(account['account_id'], True))
                embed.set_image(url=f"http://img.rec.net/{oldestfeed['ImageName']}")
            else:
                print(f"{ctx.command} > {account['account_id']}, {account['username']}, Oldestfeed not found!")
                embed = functions.error_msg(ctx, f"User `{account['username']}` isn't tagged in any post!")

        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `{profile}` doesn't exist!") 

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @oldestfeed.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass

    # CMD-LATESTFEED
    @commands.command()
    @commands.check(functions.beta_tester)
    async def latestfeed(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)

        if account:
            latestfeed = functions.id_to_latest_feed(account['account_id'])
            if latestfeed:
                tagged = ""
                if latestfeed['TaggedPlayerIds']:
                    tagged = "👥 "
                    for account_id in latestfeed['TaggedPlayerIds']:
                        username = functions.id_to_username(account_id)
                        tagged += f"[`@{username}`](https://rec.net/user/{username}) "
                room_name = functions.id_to_room_name(latestfeed['RoomId'])
                embed=discord.Embed(
                    colour=discord.Colour.orange(),
                    description=f"🔗 **[{account['username']}'s latest appearance](https://rec.net/image/{latestfeed['Id']})**\n🚪 [`^{room_name}`](https://rec.net/room/{room_name})\n<:CheerGeneral:803244099510861885> `{latestfeed['CheerCount']}` 💬 `{latestfeed['CommentCount']}`\n📆 `{latestfeed['CreatedAt'][:10]}` ⏰ `{latestfeed['CreatedAt'][11:16]} UTX`\n{tagged}"
                )
                embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=functions.id_to_pfp(account['account_id'], True))
                embed.set_image(url=f"http://img.rec.net/{latestfeed['ImageName']}")
            else:
                print(f"{ctx.command} > {account['account_id']}, {account['username']}, latestfeed not found!")
                embed = functions.error_msg(ctx, f"User `{account['username']}` isn't tagged in any post!")
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `{profile}` doesn't exist!") 

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @latestfeed.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass

    # CMD-CHEERS
    @commands.command()
    @commands.check(functions.beta_tester)
    async def cheers(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)

        if account:
            cheer_data = functions.id_to_cheer_stats(account['account_id'])
            
            if cheer_data['total_cheers'] > 0:
                most_cheered_post_text = f"\n<:CheerSport:803244185447956490> [Most Cheered Post:](https://rec.net/image/{cheer_data['most_cheered']['Id']}) (<:CheerGeneral:803244099510861885> `{cheer_data['most_cheered']['CheerCount']}`)"
            else:
                most_cheered_post_text = ""

            embed=discord.Embed(
                colour=discord.Colour.orange(),
                title = f"{account['username']}'s cheer statistics",
                description=f"<:CheerGeneral:803244099510861885> Total Cheers: `{cheer_data['total_cheers']}`{most_cheered_post_text}"
            )
            print("set image")
            embed.set_image(url=f"https://img.rec.net/{cheer_data['most_cheered']['ImageName']}?width=720")
            embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=functions.id_to_pfp(account['account_id'], True))
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `{profile}` doesn't exist!") 

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @cheers.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass

    # CMD-COMMENTS
    @commands.command()
    @commands.check(functions.beta_tester)
    async def comments(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)

        if account:
            comment_data = functions.id_to_comment_stats(account['account_id'])
            
            if comment_data['total_comments'] > 0:
                most_commented_post_text = f"\n<:CheerSport:803244185447956490> [Most Commented Post:](https://rec.net/image/{comment_data['most_commented']['Id']}) (💬 `{comment_data['most_commented']['CommentCount']}`)"
            else:
                most_commented_post_text = ""

            embed=discord.Embed(
                colour=discord.Colour.orange(),
                title = f"{account['username']}'s comment statistics",
                description=f"💬 Total Comments: `{comment_data['total_comments']}`{most_commented_post_text}"
            )
            print("set image")
            embed.set_image(url=f"https://img.rec.net/{comment_data['most_commented']['ImageName']}?width=720")
            embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=functions.id_to_pfp(account['account_id'], True))
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `{profile}` doesn't exist!") 

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @comments.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass

    # CMD-PICTURES
    @commands.command()
    @commands.check(functions.beta_tester)
    async def pictures(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)

        if account:
            photos = functions.id_to_photos(account['account_id'])
            total_pictures = len(photos)

            all_cheers = functions.id_to_all_cheers(account['account_id'])
            pictures_cheered = total_pictures - all_cheers.count(0)

            all_comments = functions.id_to_all_comments(account['account_id'])
            pictures_commented = total_pictures - all_comments.count(0)

            embed=discord.Embed(
                colour=discord.Colour.orange(),
                title = f"{account['username']} has shared {total_pictures} pictures!",
                description = f"<:CheerGeneral:803244099510861885> `{pictures_cheered}` of them are cheered!\n💬 `{pictures_commented}` of them have been commented!"
            )
            embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=functions.id_to_pfp(account['account_id'], True))
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `{profile}` doesn't exist!") 

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @pictures.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass

    # CMD-STATS
    @commands.command()
    @commands.check(functions.beta_tester)
    async def stats(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)

        if account:
            photos = functions.id_to_photos(account['account_id'])
            total_pictures = len(photos)
            if not total_pictures:
                embed = functions.error_msg(ctx, f"User `{account['username']}` hasn't shared a single picture!")
            else: 
                all_cheers = functions.id_to_all_cheers(account['account_id'])
                pictures_cheered = total_pictures - all_cheers.count(0)
                cheer_data = functions.id_to_cheer_stats(account['account_id'])
                all_comments = functions.id_to_all_comments(account['account_id'])
                pictures_commented = total_pictures - all_comments.count(0)
                comment_data = functions.id_to_comment_stats(account['account_id'])

                embed=discord.Embed(
                    colour=discord.Colour.orange(),
                    title = f"RecNet Statistics for {account['username']}!"
                )

                embed.add_field(name="Pictures shared", value=f"`{total_pictures}`\n", inline=False)

                if pictures_cheered:
                    embed.add_field(name="CHEER STATISTICS", value=f"Total Cheers: <:CheerGeneral:803244099510861885> `{cheer_data['total_cheers']}`\nUser's posts cheered: `{pictures_cheered}`\n[**Most cheered post**](https://rec.net/image/{cheer_data['most_cheered']['Id']})\n<:CheerGeneral:803244099510861885> `{cheer_data['most_cheered']['CheerCount']}` 💬 `{cheer_data['most_cheered']['CommentCount']}`",inline=True)

                if pictures_commented:
                    embed.add_field(name="COMMENT STATISTICS", value=f"Total Comments: 💬 `{comment_data['total_comments']}`\nUser's posts commented: `{pictures_commented}`\n[**Most commented post**](https://rec.net/image/{comment_data['most_commented']['Id']})\n<:CheerGeneral:803244099510861885> `{comment_data['most_commented']['CheerCount']}` 💬 `{comment_data['most_commented']['CommentCount']}`\n\n",inline=True)

                oldest_text = ""
                oldest = functions.id_to_oldest_photo(account['account_id'])
                print(oldest)
                if oldest:
                    oldest_text = f"[First post](https://rec.net/image/{oldest['Id']})\n"

                latest_text = "" 
                latest = functions.id_to_latest_photo(account['account_id'])
                print(latest)
                if latest:
                    latest_text = f"[Latest post](https://rec.net/image/{latest['Id']})\n"

                oldestfeed_text = ""
                oldestfeed = functions.id_to_oldest_feed(account['account_id'])
                print(oldestfeed)
                if oldestfeed:
                    oldestfeed_text = f"[First appearance](https://rec.net/image/{oldestfeed['Id']})\n"

                latestfeed_text = ""
                latestfeed = functions.id_to_latest_feed(account['account_id'])
                print(latestfeed)
                if latestfeed:
                    latestfeed_text = f"[Latest appearance](https://rec.net/image/{latestfeed['Id']})"

                embed.add_field(name="OTHER POSTS", value=f"{oldest_text}{latest_text}{oldestfeed_text}{latestfeed_text}", inline=False)

                embed.set_thumbnail(url=functions.id_to_pfp(account['account_id'], True))

                embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=functions.id_to_pfp(account['account_id'], True))
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `{profile}` doesn't exist!") 

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @stats.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass


    # CMD-ROOMINFO
    @commands.command(aliases=["rinfo"])
    @commands.check(functions.beta_tester)
    async def roominfo(self, ctx, room_name):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        print("Get room json")
        room_embed = functions.room_embed(room_name)
        
        if not room_embed:
            room_embed = functions.error_msg(ctx, f"Room `{room_name}` doesn't exist!")      
        functions.embed_footer(ctx, room_embed) # get default footer from function
        await ctx.send(embed=room_embed)

    @roominfo.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in a room!")
            
            await ctx.send(embed=embed)
        else:
            pass


    # CMD-APICHECK
    @commands.command()
    @commands.check(functions.beta_tester)
    async def apistatus(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        author = f"<@{ctx.author.id}>"
        embed = discord.Embed(
            description = "<a:loading:794930501597003786> Calling API to check its status...",
            colour = discord.Colour.orange()
        )
        functions.embed_footer(ctx, embed)
        loading = await ctx.send(embed=embed)

        embed = discord.Embed(
            title = "API call results!",
            colour = discord.Colour.orange()
        ) 
        # Rooms
        try:
            api = requests.get("https://api.rec.net/roomserver/rooms/search?query=paintball", timeout=10)
            if api.ok:
                embed.add_field(name="Room API call",value="`✅ Successful!`", inline=False)
            else: 
                embed.add_field(name="Room API call",value="`❌ Failure.`", inline=False)
        except:
            embed.add_field(name="Room API call",value="`❌ Failure.`", inline=False)

        # Accounts
        try:
            api = requests.get("https://accounts.rec.net/account?username=coach", timeout=10)
            if api.ok:
                embed.add_field(name="Account API call",value="`✅ Successful!`", inline=False)
            else: 
                embed.add_field(name="Account API call",value="`❌ Failure.`", inline=False)
        except:
            embed.add_field(name="Account API call",value="`❌ Failure.`", inline=False)

        # Images
        try:
            api = requests.get("https://api.rec.net/api/images/v3/feed/global?take=5", timeout=10)
            if api.ok:
                embed.add_field(name="Image API call",value="`✅ Successful!`", inline=False)
            else: 
                embed.add_field(name="Image API call",value="`❌ Failure.`", inline=False)
        except:
            embed.add_field(name="Image API call",value="`❌ Failure.`", inline=False)

        # Events
        try:
            api = requests.get("https://api.rec.net/api/playerevents/v1?take=5", timeout=10)
            if api.ok:
                embed.add_field(name="Event API call",value="`✅ Successful!`", inline=False)
            else: 
                embed.add_field(name="Event API call",value="`❌ Failure.`", inline=False)
        except:
            embed.add_field(name="Event API call",value="`❌ Failure.`", inline=False)

        await loading.delete()
        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(author, embed=embed)

    
    #CMD-SHORTCUTS
    @commands.command()
    @commands.check(functions.beta_tester)
    async def shortcuts(self, ctx, username=None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        author = f"<@{ctx.author.id}>"

        embed = discord.Embed(
            title = "Shortcuts for RecNet",
            colour = discord.Colour.orange()
        )
        
        embed.add_field(name="Rec.net", value="[Link](https://rec.net/)", inline = True)
        embed.add_field(name="Rooms", value="[Link](https://rec.net/room/browse)", inline = True)
        embed.add_field(name="Events", value="[Link](https://rec.net/event/browse)", inline = True)

        if not username:
            embed.add_field(name="LINKS TO YOUR PROFILE", value="If nothing shows up below this, you didn't enter your username. `.shortcuts <username>`", inline = False)
            embed.set_footer(text="Shortcuts for -")
        else:
            old_username = username
            try:
                username = functions.check_account_existence_and_return(username)["username"]
                embed.add_field(name="LINKS TO YOUR PROFILE", value=f"Account: `@{username}`", inline = False)
            except:
                embed.add_field(name="LINKS TO YOUR PROFILE", value=f"Account: `@{old_username}`", inline = False)
            embed.add_field(name="Profile", value=f"[Link](https://rec.net/user/{username})", inline = True)
            embed.add_field(name="Photos", value=f"[Link](https://rec.net/user/{username}/photos)", inline = True)
            embed.add_field(name="Rooms", value=f"[Link](https://rec.net/user/{username}/rooms)", inline = True)
            embed.add_field(name="Events", value=f"[Link](https://rec.net/user/{username}/events)", inline = True)
            embed.add_field(name="Settings", value=f"[Link](https://rec.net/user/{username}/settings)", inline = True)
            embed.add_field(name="Friends", value=f"[Link](https://rec.net/user/{username}/friends)", inline = True)
            embed.add_field(name="Subscribers", value=f"[Link](https://rec.net/user/{username}/subscribers)", inline = True)
            embed.add_field(name="Subscriptions", value=f"[Link](https://rec.net/user/{username}/subscriptions)", inline = True)
            embed.add_field(name="Seller stats", value="[Link](https://rec.net/seller-stats)", inline = True)
            embed.set_footer(text=f"Shortcuts for @{username}")

        functions.embed_footer(ctx, embed)
        await ctx.send(author, embed=embed)


    # CMD-PLACEMENT
    @commands.command()
    @commands.check(functions.beta_tester)
    async def placement(self, ctx, room):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        
        room_json = functions.get_room_json(room)
        if room_json:
            placement = functions.get_room_placement(room)
            if not placement:
                placement = "<1000"
            embed = discord.Embed(
                title = f"{room_json['Name']}'s placement on hot",
                description = f"🔥 `#{placement}`",
                url = f"https://rec.net/room/{room_json['Name']}",
                colour = discord.Colour.orange()
            )
            embed.set_thumbnail(url=f"https://img.rec.net/{room_json['ImageName']}?width=720")
        else:
            embed = functions.error_msg(ctx, f"Room `{room}` doesn't exist!") 

        functions.embed_footer(ctx, embed)
        await ctx.send(embed=embed)

    @placement.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in a room!")
            
            await ctx.send(embed=embed)
        else:
            pass


    # CMD-FEATURED
    @commands.command()
    @commands.check(functions.beta_tester)
    async def featured(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        author = f"<@{ctx.author.id}>"

        featured_rooms = functions.get_featured_rooms()

        embed=discord.Embed(
            colour = discord.Colour.orange(),
            description = "<a:spinning:804022054822346823> Getting featured rooms and their statistics..."
        )
        functions.embed_footer(ctx, embed)
        loading = await ctx.send(embed=embed)


        embed=discord.Embed(
            colour = discord.Colour.orange(),
            title = "Featured rooms"
        )
        
        count = 0
        for room in featured_rooms:
            count += 1
            room_data = functions.get_room_json(room['RoomId'], True)
            embed.add_field(name=f"{count}. ^{room['RoomName']}, by @{functions.id_to_username(room_data['CreatorAccountId'])}", value=f"[🔗 RecNet link](https://rec.net/room/{room['RoomName']})\n<:CheerGeneral:803244099510861885> `{room_data['Stats']['CheerCount']}` *(CHEERS)*\n⭐ `{room_data['Stats']['FavoriteCount']}` *(FAVORITES)*\n👤 `{room_data['Stats']['VisitorCount']}` *(VISITORS)*\n👥 `{room_data['Stats']['VisitCount']}` *(ROOM VISITS)*\n🔥 `#{functions.get_room_placement(room['RoomName'])}` *(HOT PLACEMENT)*\n💯 `{functions.get_room_score(room['RoomName'])}` *(AVG SCORE)*", inline=False)
            
        functions.embed_footer(ctx, embed)
        await loading.delete()
        await ctx.send(author, embed=embed)


    # CMD-FRONTPAGE
    @commands.command()
    @commands.check(functions.beta_tester)
    async def frontpage(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        author = f"<@{ctx.author.id}>"

        msg = ""
        frontpage = functions.get_frontpage(5)
        
        for post in frontpage:
            tagged = ""
            if post['TaggedPlayerIds']:
                tagged = "*Users tagged:* "
                for account_id in post['TaggedPlayerIds']:
                    tagged += f"`@{functions.id_to_username(account_id)}` "
            else: tagged = "*Users tagged:* None!"


            msg += f"https://rec.net/image/{post['Id']}\n**{functions.id_to_display_name(post['PlayerId'])}** @{functions.id_to_username(post['PlayerId'])}\n🚪 `^{functions.id_to_room_name(post['RoomId'])}`\n<:CheerGeneral:803244099510861885> `{post['CheerCount']}`\n💬 `{post['CommentCount']}`\n{tagged}\n\n"
            
        await ctx.send(msg)
        


def setup(client):
    client.add_cog(Utility(client))