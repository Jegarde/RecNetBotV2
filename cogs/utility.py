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
            account_id = account["account_id"]
            username = account["username"]
            bio = functions.get_bio(account_id)
            pfp = functions.id_to_pfp(account_id, True)

            print(f"{ctx.command} > {account_id}, {username}, {bio}, {pfp}")

            embed=functions.default_embed()
            embed.add_field(name=f"{username}'s bio:", value=f"```{bio}```")
            embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=pfp)
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
            account_id = account["account_id"]
            username = account["username"]
            pfp = functions.id_to_pfp(account_id, False)

            print(f"{ctx.command} > {account_id}, {username}, {pfp}")

            embed=discord.Embed(
                colour=discord.Colour.orange(),
                description = f"[{username}'s profile picture](https://rec.net/image/{functions.id_to_pfp(account_id, False, False)})"
            )
            embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=functions.id_to_pfp(account_id, True))
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
            account_id = account["account_id"]
            username = account["username"]
            banner = functions.id_to_banner(account_id, True)

            print(f"{ctx.command} > {account_id}, {username}, {banner}")

            if not banner:
                embed=discord.Embed(
                    colour=discord.Colour.orange(),
                    description = f"{username}'s banner"
                )
                banner = "https://cdn.rec.net/static/banners/default_player.png" # replace with default banner
            else:
                embed=discord.Embed(
                    colour=discord.Colour.orange(),
                    description = f"[{username}'s banner](https://rec.net/image/{functions.id_to_banner(account_id, False)})"
                )
            embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=functions.id_to_pfp(account_id))
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
            account_id = account["account_id"]
            username = account["username"]
            display_name = functions.id_to_display_name(account_id)
            pfp = functions.id_to_pfp(account_id, False)
            bio = functions.get_bio(account_id)
            created_at = functions.id_to_creation_date(account_id)
            is_junior = functions.id_to_is_junior(account_id)

            print(f"{ctx.command} > {account_id}, {username}, {display_name}, {pfp}, {bio}, {created_at}, {is_junior}")

            embed=discord.Embed(
                colour=discord.Colour.orange()
                #description = f"[{username}'s profile picture](https://rec.net/image/{functions.id_to_pfp(account_id, False, False)})"
            )
            embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=functions.id_to_pfp(account_id, True))
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
            account_id = account["account_id"]
            username = account["username"]
            is_junior = functions.id_to_is_junior(account_id)

            print(f"{ctx.command} > {account_id}, {username}, {is_junior}")

            if is_junior:
                title = f"{username} is a junior! 🧒"
            else:
                title = f"{username} is not junior! 🧔"

            embed=discord.Embed(
                colour=discord.Colour.orange(),
                title = title
            )
            embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=functions.id_to_pfp(account_id, True))
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
            account_id = account["account_id"]
            username = account["username"]
            created_at = functions.id_to_creation_date(account_id)

            print(f"{ctx.command} > {account_id}, {username}, {created_at}")

            embed=discord.Embed(
                colour=discord.Colour.orange(),
                title = f"{username}'s account was created at",
                description = f"📆 `{created_at[:10]}`\n⏰ `{created_at[11:16]} UTX`"
            )
            embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=functions.id_to_pfp(account_id, True))
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
            account_id = account["account_id"]
            username = account["username"]
            display_name = functions.id_to_display_name(account_id)

            print(f"{ctx.command} > {account_id}, {username}, {display_name}")

            embed=discord.Embed(
                colour=discord.Colour.orange(),
                title=f"{username}'s display name is",
                description=f"`{display_name}`"
            )
            embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=functions.id_to_pfp(account_id, True))
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
        latest = False # if it stays false, it couldn't be found
        if account:
            account_id = account["account_id"]
            username = account["username"]

            try:
                latest = functions.id_to_latest_photo(account_id)
                latest_id = latest["Id"]
                latest_img_name = latest["ImageName"]

                embed=discord.Embed(
                    colour=discord.Colour.orange(),
                    description=f"[{username}'s latest picture](https://rec.net/image/{latest_id})"
                )
                embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=functions.id_to_pfp(account_id, True))
                embed.set_image(url=f"http://img.rec.net/{latest_img_name}")
            except:
                print(f"{ctx.command} > {account_id}, {username}, Latest not found!")
                embed = functions.error_msg(ctx, f"User `{username}` hasn't shared any pictures!")
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
        oldest = False # if it stays false, it couldn't be found
        if account:
            account_id = account["account_id"]
            username = account["username"]

            try:
                oldest = functions.id_to_oldest_photo(account_id)
                oldest_id = oldest["Id"]
                oldest_img_name = oldest["ImageName"]

                embed=discord.Embed(
                    colour=discord.Colour.orange(),
                    description=f"[{username}'s oldest picture](https://rec.net/image/{oldest_id})"
                )
                embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=functions.id_to_pfp(account_id, True))
                embed.set_image(url=f"http://img.rec.net/{oldest_img_name}")
            except:
                print(f"{ctx.command} > {account_id}, {username}, Oldest not found!")
                embed = functions.error_msg(ctx, f"User `{username}` hasn't shared any pictures!")
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
        oldestfeed = False # if it stays false, it couldn't be found

        if account:
            account_id = account["account_id"]
            username = account["username"]

            try:
                oldestfeed = functions.id_to_oldest_feed(account_id)
                oldestfeed_id = oldestfeed["Id"]
                oldestfeed_img_name = oldestfeed["ImageName"]

                embed=discord.Embed(
                    colour=discord.Colour.orange(),
                    description=f"[{username}'s oldest appearance](https://rec.net/image/{oldestfeed_id})"
                )
                embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=functions.id_to_pfp(account_id, True))
                embed.set_image(url=f"http://img.rec.net/{oldestfeed_img_name}")
            except:
                print(f"{ctx.command} > {account_id}, {username}, Oldestfeed not found!")
                embed = functions.error_msg(ctx, f"User `{username}` isn't tagged in any post!")

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
        latestfeed = False # same thing here

        if account:
            account_id = account["account_id"]
            username = account["username"]

            try:
                latestfeed = functions.id_to_latest_feed(account_id)
                latestfeed_id = latestfeed["Id"]
                latestfeed_img_name = latestfeed["ImageName"]

                embed=discord.Embed(
                    colour=discord.Colour.orange(),
                    description=f"[{username}'s latest appearance](https://rec.net/image/{latestfeed_id})"
                )
                embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=functions.id_to_pfp(account_id, True))
                embed.set_image(url=f"http://img.rec.net/{latestfeed_img_name}")
            except:
                print(f"{ctx.command} > {account_id}, {username}, latestfeed not found!")
                embed = functions.error_msg(ctx, f"User `{username}` isn't tagged in any post!")
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
            account_id = account["account_id"]
            username = account["username"]
            
            cheer_data = functions.id_to_cheer_stats(account_id)
            print(cheer_data)
            total_cheers = cheer_data["total_cheers"]
            image_name = cheer_data["most_cheered"]["ImageName"]
            most_cheered_cheers = cheer_data["most_cheered"]["CheerCount"]
            most_cheered_link = "https://rec.net/image/"+str(cheer_data["most_cheered"]["Id"])
            
            if total_cheers > 0:
                most_cheered_post_text = f"\n<:CheerSport:803244185447956490> [Most Cheered Post:]({most_cheered_link}) (<:CheerGeneral:803244099510861885> `{most_cheered_cheers}`)"
            else:
                most_cheered_post_text = ""

            embed=discord.Embed(
                colour=discord.Colour.orange(),
                title = f"{username}'s cheer statistics",
                description=f"<:CheerGeneral:803244099510861885> Total Cheers: `{total_cheers}`{most_cheered_post_text}"
            )
            print("set image")
            embed.set_image(url=f"https://img.rec.net/{image_name}?width=720")
            embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=functions.id_to_pfp(account_id, True))
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
            account_id = account["account_id"]
            username = account["username"]
            
            comment_data = functions.id_to_comment_stats(account_id)
            print(comment_data)
            total_comments = comment_data["total_comments"]
            image_name = comment_data["most_commented"]["ImageName"]
            most_commented_comment_count = comment_data["most_commented"]["CommentCount"]
            most_commented_link = "https://rec.net/image/"+str(comment_data["most_commented"]["Id"])
            
            if total_comments > 0:
                most_commented_post_text = f"\n<:CheerSport:803244185447956490> [Most Commented Post:]({most_commented_link}) (💬 `{most_commented_comment_count}`)"
            else:
                most_commented_post_text = ""

            embed=discord.Embed(
                colour=discord.Colour.orange(),
                title = f"{username}'s comment statistics",
                description=f"💬 Total Comments: `{total_comments}`{most_commented_post_text}"
            )
            print("set image")
            embed.set_image(url=f"https://img.rec.net/{image_name}?width=720")
            embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=functions.id_to_pfp(account_id, True))
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
            account_id = account["account_id"]
            username = account["username"]
            photos = functions.id_to_photos(account_id)
            total_pictures = len(photos)

            all_cheers = functions.id_to_all_cheers(account_id)
            pictures_cheered = total_pictures - all_cheers.count(0)

            all_comments = functions.id_to_all_comments(account_id)
            pictures_commented = total_pictures - all_comments.count(0)

            embed=discord.Embed(
                colour=discord.Colour.orange(),
                title = f"{username} has shared {total_pictures} pictures!",
                description = f"<:CheerGeneral:803244099510861885> `{pictures_cheered}` of them are cheered!\n💬 `{pictures_commented}` of them have been commented!"
            )
            embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=functions.id_to_pfp(account_id, True))
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
            account_id = account["account_id"]
            username = account["username"]
            photos = functions.id_to_photos(account_id)
            total_pictures = len(photos)
            if total_pictures == 0:
                embed = functions.error_msg(ctx, f"User `{username}` hasn't shared a single picture!")
            else: 
                latest = functions.id_to_latest_photo(account_id)
                latest_id = latest["Id"]
                #latest_cheers = latest["CheerCount"]
                #latest_comments = latest["CommentCount"]

                oldest = functions.id_to_oldest_photo(account_id)
                oldest_id = oldest["Id"]
                #oldest_cheers = oldest["CheerCount"]
                #oldest_comments = oldest["CommentCount"]

                latestfeed = functions.id_to_latest_feed(account_id)
                latestfeed_id = latestfeed["Id"]
                #latestfeed_cheers = latestfeed["CheerCount"]
                #latestfeed_comments = latestfeed["CommentCount"]

                oldestfeed = functions.id_to_oldest_feed(account_id)
                oldestfeed_id = oldestfeed["Id"]
                #oldestfeed_cheers = oldestfeed["CheerCount"]
                #oldestfeed_comments = oldestfeed["CommentCount"]

                all_cheers = functions.id_to_all_cheers(account_id)
                pictures_cheered = total_pictures - all_cheers.count(0)
                cheer_data = functions.id_to_cheer_stats(account_id)
                total_cheers = cheer_data["total_cheers"]
                most_cheered_img = cheer_data["most_cheered"]["Id"]
                most_cheered_cheer_count = cheer_data["most_cheered"]["CheerCount"]
                most_cheered_comment_count = cheer_data["most_cheered"]["CommentCount"]

                all_comments = functions.id_to_all_comments(account_id)
                pictures_commented = total_pictures - all_comments.count(0)
                comment_data = functions.id_to_comment_stats(account_id)
                total_comments = comment_data["total_comments"]
                most_commented_img = comment_data["most_commented"]["Id"]
                most_commented_cheer_count = comment_data["most_commented"]["CheerCount"]
                most_commented_comment_count = comment_data["most_commented"]["CommentCount"]


                embed=discord.Embed(
                    colour=discord.Colour.orange(),
                    title = f"RecNet Statistics for {username}!"
                )

                embed.add_field(name="Pictures shared", value=f"`{total_pictures}`\n", inline=False)

                embed.add_field(name="CHEER STATISTICS", value=f"Total Cheers: <:CheerGeneral:803244099510861885> `{total_cheers}`\nUser's posts cheered: `{pictures_cheered}`\n[**Most cheered post**](https://rec.net/image/{most_cheered_img})\n<:CheerGeneral:803244099510861885> `{most_cheered_cheer_count}` 💬 `{most_cheered_comment_count}`",inline=True)

                embed.add_field(name="COMMENT STATISTICS", value=f"Total Comments: 💬 `{total_comments}`\nUser's posts commented: `{pictures_commented}`\n[**Most commented post**](https://rec.net/image/{most_commented_img})\n<:CheerGeneral:803244099510861885> `{most_commented_cheer_count}` 💬 `{most_commented_comment_count}`\n\n",inline=True)

                embed.add_field(name="OTHER POSTS", value=f"[First post](https://rec.net/image/{oldest_id})\n[Latest post](https://rec.net/image/{latest_id})\n[First appearance](https://rec.net/image/{oldestfeed_id})\n[Latest appearance](https://rec.net/image/{latestfeed_id})", inline=False)

                embed.set_thumbnail(url=functions.id_to_pfp(account_id, True))

                embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=functions.id_to_pfp(account_id, True))
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