import functions
import requests
import discord
from discord.ext import commands
from discord.ext import menus

class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client

    # UTILITY COMMANDS

    @commands.command()
    @commands.check(functions.beta_tester)
    async def rectnet(self, ctx):
        cheers = functions.cheers_in_room()
        await ctx.send(f"<@{ctx.author.id}>\n**Cheers:** `{cheers['cheers']}`\n**Images taken:** `{cheers['image_count']}`\n\n**On frontpage: ** `{cheers['frontpage_count']}` (top 100)")

    # CMD-BLACKLISTED
    @commands.command(aliases=['bl'])
    @commands.check(functions.beta_tester)
    async def blacklisted(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if account:
            blacklisted = True
            frontpage = requests.get("https://api.rec.net/api/images/v3/feed/global?take=500").json()
            count = 1
            for post in frontpage:
                count += 1
                if post['PlayerId'] == account['account_id']:
                    blacklisted = False
                    break

            if blacklisted:
                title_string = f"@{account['username']} may be blacklisted!"
                description = "For this to be accurate, please take a fresh picture in-game, share it, self-cheer it, and wait about 5-10 minutes."
            else:
                title_string = f"@{account['username']} is not blacklisted!"
                description = f"Your picture appears in `#{count}`."

            embed=discord.Embed(
                colour=discord.Colour.orange(),
                title = title_string,
                description = description
            )
            pfp = functions.id_to_pfp(account['account_id'])
            embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=pfp)

        else:
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @blacklisted.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass

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
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @bio.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass

    # CMD-CRINGEBIOCHECK
    @commands.command(aliases=["cbc"])
    @commands.check(functions.beta_tester)
    async def cringebiocheck(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if account:
            bio = functions.get_bio(account['account_id'])
            pfp = functions.id_to_pfp(account['account_id'], True)

            print(f"{ctx.command} > {account['account_id']}, {account['username']}, {bio}, {pfp}")

            embed=functions.default_embed()
            embed.add_field(name=f"{account['username']}'s bio:", value=f"```{bio}```")

            cringe_check_list = functions.load("cringe_word_list.json")

            maybe_cringe = False

            if bio:
                #cringe_check = any(val in bio for val in cringe_check_list)
                cringe_check_words = [ele for ele in cringe_check_list if(f" {ele.casefold()}" in bio.casefold())]
                
                if not bool(cringe_check_words):
                    cringe_check_words = [ele for ele in cringe_check_list if(ele.casefold() in bio.casefold())]
                    if bool(cringe_check_words):
                        if len(cringe_check_words) > 1:
                            maybe_cringe = False
                        else:
                            maybe_cringe = True

                if len(cringe_check_words) < 2:
                    maybe_cringe = True

                cringe_check = bool(cringe_check_words)
            else:
                cringe_check = True
                cringe_check_words = "no bio......"

            if cringe_check:
                if maybe_cringe:
                    cringe_check = f"**MAYBE CRINGE?** 🤔\nFlag(s): ||{cringe_check_words}||\n"
                else:
                    cringe_check = f"**CRINGE!** 😬\nFlag(s): ||{cringe_check_words}||\n"
            else:
                cringe_check = "**NOT CRINGE!** <:wholesome:796100757354053653>\n"

            if cringe_check and bio:
                embed.add_field(name=cringe_check, value="||Based on my cringe keyword list! Result may not be accurate.||", inline=False)
            else:
                embed.add_field(name=cringe_check, value="||no bio = cringe 🙂||", inline=False)

            embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=pfp)
        else:
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @cringebiocheck.error
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
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")

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
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
        
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
    @commands.command(aliases=['p'])
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
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")

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
    @commands.command(aliases=['jr'])
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
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")

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
    @commands.command(aliases=['createdat'])
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
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")

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
    @commands.command(aliases=['displayname'])
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
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")

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
    @commands.command(aliases=['newest'])
    @commands.check(functions.beta_tester)
    async def latest(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if account:
            latest = functions.id_to_latest_photo(account['account_id'])
            if latest:
                embed = functions.image_embed(latest)
            else:
                print(f"{ctx.command} > {account['account_id']}, {account['username']}, Latest not found!")
                embed = functions.error_msg(ctx, f"User `{account['username']}` hasn't shared any pictures!")
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(f"Latest from `@{account['username']}`", embed=embed)

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
                embed = functions.image_embed(oldest)
            else:
                print(f"{ctx.command} > {account['account_id']}, {account['username']}, Oldest not found!")
                embed = functions.error_msg(ctx, f"User `{account['username']}` hasn't shared any pictures!")
        else:
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(f"Oldest from `@{account['username']}`",embed=embed)

    @oldest.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass

    # CMD-OLDESTFEED
    @commands.command(aliases=['oldestappearance'])
    @commands.check(functions.beta_tester)
    async def oldestfeed(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)

        if account:
            oldestfeed = functions.id_to_oldest_feed(account['account_id'])
            if oldestfeed:
                embed = functions.image_embed(oldestfeed)
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!") 

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(f"Oldest feed from `@{account['username']}`",embed=embed)

    @oldestfeed.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass

    # CMD-LATESTFEED
    @commands.command(aliases=['appearance'])
    @commands.check(functions.beta_tester)
    async def latestfeed(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)

        if account:
            latestfeed = functions.id_to_latest_feed(account['account_id'])
            if latestfeed:
                embed = functions.image_embed(latestfeed)
            else:
                print(f"{ctx.command} > {account['account_id']}, {account['username']}, latestfeed not found!")
                embed = functions.error_msg(ctx, f"User `{account['username']}` isn't tagged in any post!")
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!") 

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(f"Latest feed from `@{account['username']}`",embed=embed)

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
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!") 

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
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!") 

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @comments.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass

    # CMD-PHOTOSTATS
    @commands.command()
    @commands.check(functions.beta_tester)
    async def photostats(self, ctx, profile):
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
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!") 

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @photostats.error
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
            feed = functions.id_to_feed(account['account_id'])
            total_pictures = len(photos)
            total_feed = len(feed)
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
                    title = f"RecNet Statistics for {account['username']}!",
                    description = f"Pictures shared: `{total_pictures}`\nPictures tagged in: `{total_feed}`"
                )

               # embed.add_field(name="Pictures shared", value=f"`{total_pictures}`\n", inline=True)
                #embed.add_field(name="Pictures tagged in", value=f"`{total_feed}`\n", inline=True)
                #embed.add_field(name="‎⠀", value=f"‎⠀", inline=False)

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
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!") 

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

        author = f"<@{ctx.author.id}>"

        embed = discord.Embed(
            description = f"<a:spinning:804022054822346823>  Getting statistics for the room `^{room_name}`...",
            colour = discord.Colour.orange()
        )
        functions.embed_footer(ctx, embed)
        loading = await ctx.send(embed=embed)

        print("Get room json")
        try:
            room_embed = functions.room_embed(room_name, False, ctx)
            functions.embed_footer(ctx, room_embed)
            await ctx.send(author, embed=room_embed)
        except:
            room_embed = functions.error_msg(ctx, f"Room `^{room_name}` doesn't exist!") 
            functions.embed_footer(ctx, room_embed)
            await ctx.send(embed=room_embed)
        
        await loading.delete()

    @roominfo.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in a room!")
            
            await ctx.send(embed=embed)
        else:
            pass


    # CMD-APICHECK
    @commands.command(aliases=['apicheck', "ac"])
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
    @commands.command(aliases=['sc'])
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


    # CMD-TAKENIN
    @commands.command(aliases=['ti'])
    @commands.check(functions.beta_tester)
    async def takenin(self, ctx, room, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        room_data = functions.get_room_json(room)
        if room_data: #if room exists
            account = functions.check_account_existence_and_return(profile)
            if account: # if account exists
                photos = functions.id_to_photos(account['account_id'])
                if photos: # if user has posted anything
                    global images
                    images = []
                    for post in photos:
                        if post['RoomId'] == room_data['RoomId']:
                            images.append(post)

                    if images:
                        pages = menus.MenuPages(source=ImageMenu(range(1, len(images)+1)), clear_reactions_after=True)
                        await pages.start(ctx)
                        
                    else: # not found
                        embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single picture in `^{room_data['Name']}`!")
                        await ctx.send(embed=embed)
                else:
                    embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single picture!")
                    await ctx.send(embed=embed)
            else:
                embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
                await ctx.send(embed=embed)

        else: # room doesn't exist
            embed = functions.error_msg(ctx, f"Room `^{room}` doesn't exist!")
            await ctx.send(embed=embed)

    @takenin.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in a room and an user! Usage: `.takenin <room> <user>`")
            
            await ctx.send(embed=embed)
        else:
            pass


    # CMD-TAKENOF
    @commands.command(aliases=['to'])
    @commands.check(functions.beta_tester)
    async def takenof(self, ctx, of_user, by_user):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        of_user_account = functions.check_account_existence_and_return(of_user)
        by_user_account = functions.check_account_existence_and_return(by_user)
        if of_user_account and by_user_account: #if both exist
            of_user_feed = functions.id_to_feed(of_user_account['account_id'])
            if of_user_feed: # if user appears anywhere
                global images
                images = []
                for post in of_user_feed:
                    if by_user_account['account_id'] == post['PlayerId']:
                        images.append(post)

                if images:
                    pages = menus.MenuPages(source=ImageMenu(range(1, len(images)+1)), clear_reactions_after=True)
                    await pages.start(ctx)

                else: # not found
                    embed = functions.error_msg(ctx, f"Couldn't find any picture taken by `@{by_user_account['username']}`, that features `@{of_user_account['username']}`")
                    await ctx.send(embed=embed)
            else:
                embed = functions.error_msg(ctx, f"User `@{of_user_account['username']}` isn't tagged in any post!")
                await ctx.send(embed=embed)

        else: # either doesn't exist
            embed = functions.error_msg(ctx, f"Either `@{of_user}` or `@{by_user}` don't exist!")
            await ctx.send(embed=embed)

    @takenof.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in 2 users! Usage: `.takenof <of_user> <by_user>`")
            
            await ctx.send(embed=embed)
        else:
            pass

    # CMD-TAKENOFIN
    @commands.command(aliases=['toi'])
    @commands.check(functions.beta_tester)
    async def takenofin(self, ctx, of_user, room):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        of_user_account = functions.check_account_existence_and_return(of_user)
        room_data = functions.get_room_json(room)
        
        if of_user_account:#if both exist
            if room_data:
                of_user_feed = functions.id_to_feed(of_user_account['account_id'])
                if of_user_feed: # if user appears anywhere
                    global images
                    images = []
                    for post in of_user_feed:
                        if room_data['RoomId'] == post['RoomId']:
                            images.append(post)

                    if images:
                        pages = menus.MenuPages(source=ImageMenu(range(1, len(images)+1)), clear_reactions_after=True)
                        await pages.start(ctx)
                    
                    else: # not found
                        embed = functions.error_msg(ctx, f"Couldn't find any picture taken of `@{of_user_account['username']}` in `^{room_data['Name']}`!")
                        await ctx.send(embed=embed)
            else:
                embed = functions.error_msg(ctx, f"Room `^{room}` doesn't exist!")
                await ctx.send(embed=embed)

        else: # either doesn't exist
            embed = functions.error_msg(ctx, f"User `@{of_user}` doesn't exist!")
            await ctx.send(embed=embed)

    @takenofin.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an user and a room! Usage: `.takenofin <user> <room>`")
            
            await ctx.send(embed=embed)
        else:
            pass


    # CMD-TOGETHER
    @commands.command()
    @commands.check(functions.beta_tester)
    async def together(self, ctx, user1, user2):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        user1_account = functions.check_account_existence_and_return(user1)
        user2_account = functions.check_account_existence_and_return(user2)
        if user1_account and user2_account: #if both exist
            user1_feed = functions.id_to_feed(user1_account['account_id'])
            if user1_feed: # if user appears anywhere
                global images
                images = functions.together(user1_account['account_id'], user2_account['account_id'])
                if images:
                    pages = menus.MenuPages(source=ImageMenu(range(1, len(images)+1)), clear_reactions_after=True)
                    await pages.start(ctx)
                else: # not found
                    embed = functions.error_msg(ctx, f"Couldn't find any post that features both `@{user1_account['username']}` and `@{user2_account['username']}`!")
                await ctx.send(embed=embed)
            else:
                embed = functions.error_msg(ctx, f"Couldn't find any post that features both `@{user1_account['username']}` and `@{user2_account['username']}`!")
                await ctx.send(embed=embed)

        else: # either doesn't exist
            embed = functions.error_msg(ctx, f"Either `@{user1}` or `@{user2}` don't exist!")
            await ctx.send(embed=embed)

    @together.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in 2 users! Usage: `.together <user1> <user2>`")
            
            await ctx.send(embed=embed)
        else:
            pass


    # CMD-SORTBY
    @commands.command()
    @commands.check(functions.beta_tester)
    async def sortby(self, ctx, profile, mode):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)

        if account:
            photos = functions.id_to_photos(account['account_id'])
            if photos:
                mode = mode.lower()
                reverse_sort = True
                if mode == "cheers":
                    mode = lambda i: i["CheerCount"]
                    reverse_sort = True
                elif mode == "comments":
                    mode = lambda i: i["CommentCount"]
                    reverse_sort = True
                elif mode == "oldest":
                    mode = lambda i: i["CreatedAt"]
                    reverse_sort = False
                elif mode == "latest":
                    mode = lambda i: i["CreatedAt"]
                    reverse_sort = True
                else:
                    mode = None
                
                if mode:
                    global images
                    images = sorted(photos, key = mode, reverse = reverse_sort)

                    pages = menus.MenuPages(source=ImageMenu(range(1, len(images)+1)), clear_reactions_after=True)
                    await pages.start(ctx)
                else:
                    embed = functions.error_msg(ctx, "Invalid mode! Modes are `cheers`, `comments`, `latest`, `oldest`") 
            else:
                embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single picture!") 
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!") 

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @sortby.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username and mode! \nUsage: `.sortby <user> <latest|oldest|cheers|comments>`")
            
            await ctx.send(embed=embed)
        else:
            pass


    # CMD-ROOMSBY
    @commands.command()
    @commands.check(functions.beta_tester)
    async def roomsby(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)

        if account:
            account_rooms = functions.id_to_rooms(account['account_id'])
            if account_rooms:
                embed=discord.Embed(
                    colour=discord.Colour.orange(),
                    title = f"@{account['username']}'s (max) 10 latest rooms"
                )
                count = 0
                for room in account_rooms:
                    count += 1
                    embed.add_field(name=f"{count}. ^{room['Name']}", value=f"**Description:** ```{room['Description']}```\n**Statistics**\n<:CheerGeneral:803244099510861885> `{room['Stats']['CheerCount']}` *(CHEERS)*\n⭐ `{room['Stats']['FavoriteCount']}` *(FAVORITES)*\n👤 `{room['Stats']['VisitorCount']}` *(VISITORS)*\n👥 `{room['Stats']['VisitCount']}` *(ROOM VISITS)*", inline=False)
                    if count == 10:
                        break
                        
                pfp = functions.id_to_pfp(account['account_id'], True)
                embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=pfp)
                
            else:
                embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single room!") 
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!") 

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @roomsby.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass


    # CMD-CREATORSTATS
    @commands.command(aliases=['cs'])
    @commands.check(functions.beta_tester)
    async def creatorstats(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)

        if account:
            account_rooms = functions.id_to_rooms(account['account_id'])
            if account_rooms:
                best_room = {}
                worst_room = {}
                room_count = 0
                cheers = 0
                favorites = 0
                visitors = 0
                visits = 0
                creator_score = 0

                for room in account_rooms:
                    cheers += room['Stats']['CheerCount']
                    favorites += room['Stats']['FavoriteCount']
                    visitors += room['Stats']['VisitorCount']
                    visits += room['Stats']['VisitCount']
                    
                    temp_room_stats_sum = room['Stats']['CheerCount'] + room['Stats']['FavoriteCount'] + room['Stats']['VisitorCount'] + room['Stats']['VisitCount']
                    creator_score += round((temp_room_stats_sum + room_count*1000) / 5)

                    room_count += 1
                    if room_count == 1:
                        best_room = room
                        best_room['RoomStatsSum'] = temp_room_stats_sum

                        worst_room = room
                        worst_room['RoomStatsSum'] = temp_room_stats_sum
                    else:
                        #print(f"BestRoom {best_room['Name']}: {best_room['RoomStatsSum']} vs {room['Name']}: {temp_room_stats_sum}")
                        #print(f"WorstRoom {worst_room['Name']}: {worst_room['RoomStatsSum']} vs {room['Name']}: {temp_room_stats_sum}")
                        if best_room['RoomStatsSum'] < temp_room_stats_sum:
                            best_room = room
                            best_room['RoomStatsSum'] = temp_room_stats_sum
                        elif worst_room['RoomStatsSum'] > temp_room_stats_sum:
                            worst_room = room
                            worst_room['RoomStatsSum'] = temp_room_stats_sum
                
                embed=discord.Embed(
                    colour=discord.Colour.orange(),
                    title = f"@{account['username']}'s creator statistics",
                    description = f"Rooms published: `{room_count}`\nCreator Score: `{creator_score}`"
                )

                embed.add_field(
                    name="Total Room Statistics",value=f"<:CheerGeneral:803244099510861885> `{cheers}` *(CHEERS)*\n⭐ `{favorites}` *(FAVORITES)*\n👤 `{visitors}` *(VISITORS)*\n👥 `{visits}` *(VISITS)*",
                    inline=False
                )
                embed.add_field(
                    name="Best Room",
                    value=f"🚪 [^{best_room['Name']}](https://rec.net/room/{best_room['Name']})",
                    inline=True
                )
                embed.add_field(
                    name="Worst Room",
                    value=f"🚪 [^{worst_room['Name']}](https://rec.net/room/{worst_room['Name']})",
                    inline=True
                )
                        
                pfp = functions.id_to_pfp(account['account_id'], True)
                embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=pfp)

            else:
                embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single room!") 
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!") 

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @roomsby.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass


    # CMD-BOOKMARKED
    @commands.command(aliases=["bookmark", "favorites", "favorite"])
    @commands.check(functions.beta_tester)
    async def bookmarked(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        author = f"<@{ctx.author.id}>"

        account = functions.check_account_existence_and_return(profile)

        if account:  
            embed=discord.Embed(
                colour=discord.Colour.orange(),
                description = f"<a:spinning:804022054822346823> Looking for `@{account['username']}`'s bookmarked posts..."
            )
            functions.embed_footer(ctx, embed)
            loading = await ctx.send(embed=embed)

            embed=discord.Embed(
                colour=discord.Colour.orange(),
                title = f"@{account['username']}'s bookmarked photos 📌",
            )

            photos = functions.id_to_photos(account['account_id'])
            print(f"photos: {bool(photos)}")
            found_bookmarked = False
            if photos:
                comment_count = len(functions.id_to_all_comments(account['account_id']))
                if comment_count > 0:
                    count = 0
                    for photo in photos:
                        if photo['CommentCount'] > 0:
                            print(f"comments over 0 - {photo['Id']}")
                            comments = functions.get_photo_comments(photo['Id'])
                            for comment in comments:
                                if comment['PlayerId'] == account['account_id'] and "bookmark" in comment['Comment'].lower():
                                    print("BOOKMARKED!!!")
                                    found_bookmarked = True
                                    count += 1
                                    if count > 25:
                                        break
                                    embed.add_field(name=f"{count}. \"{comment['Comment'].replace('bookmark', '')}\"", value=f"https://rec.net/image/{comment['SavedImageId']}", inline=False)
            
            pfp = functions.id_to_pfp(account['account_id'], True)
            embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=pfp)
                
        else: # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!") 

        functions.embed_footer(ctx, embed) # get default footer from function
        await loading.delete()
        if not found_bookmarked:
            embed.add_field(name="None!", value="You can bookmark your own posts by commenting\n`bookmark <text>`\non a post of yours! The text you type in is there just to remind you of what the bookmarked image is, however, it's not necessary.", inline=False)
        await ctx.send(f"{author}\n**Bookmarked:** `{count}/25`", embed=embed)

    @bookmarked.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass


    #CMD-LATESTEVENTS
    @commands.command()
    @commands.check(functions.beta_tester)
    async def latestevents(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        events_found = functions.latest_events()
        event_string = ""

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title = "Latest events",
            description = event_string
        )

        if events_found:
            for event in events_found:
                event_string = ""
                description = event['Description']
                if not description:
                    description = "None"

                event_string += f"**[\"{event['Name']}\"](https://rec.net/event/{event['PlayerEventId']})** | [`{functions.id_to_display_name(event['CreatorPlayerId'])}`](https://rec.net/user/{functions.id_to_username(event['CreatorPlayerId'])})```{description}```👥 Attending: `{event['AttendeeCount']}`\n\n"
                
                embed.add_field(name=event['Name'], value=event_string, inline=False)

        if not event_string:
            event_string = "None! <:dunno:796100756653604897>"
            
        

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)


    # CMD-LATESTINBY
    @commands.command()
    @commands.check(functions.beta_tester)
    async def latestinby(self, ctx, room, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        
        account = functions.check_account_existence_and_return(profile)
        if account:
            total_photos = len(functions.id_to_photos(account['account_id']))
            if total_photos:
                print("get photos in") # REMOVEME
                photosin = functions.id_to_photos_in(account['account_id'], room)
                if photosin:
                    print("latestin") # REMOVEME
                    latestin = photosin[0]
                    
                    embed = functions.image_embed(latestin)
                else:
                    embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single picture in `^{room}`!")
            else:
                embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single picture!")
        else:
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")

        print("send") # REMOVEME
        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(f"Latest by `@{account['username']}`, in `^{room}`", embed=embed)

    @latestinby.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in a room and an user! Usage: `.latestinby <room> <user>`")
            
            await ctx.send(embed=embed)
        else:
            pass


    # CMD-OLDESTINBY
    @commands.command()
    @commands.check(functions.beta_tester)
    async def oldestinby(self, ctx, room, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        
        account = functions.check_account_existence_and_return(profile)
        if account:
            total_photos = len(functions.id_to_photos(account['account_id']))
            if total_photos:
                print("get photos in") # REMOVEME
                photosin = functions.id_to_photos_in(account['account_id'], room)
                if photosin:
                    print("oldestin") # REMOVEME
                    oldestin = photosin[len(photosin)-1]

                    embed = functions.image_embed(oldestin)
                else:
                    embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single picture in `^{room}`!")
            else:
                embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single picture!")
        else:
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")

        print("send") # REMOVEME
        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(f"Oldest by `@{account['username']}`, in `^{room}`",embed=embed)

    @oldestinby.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in a room and an user! Usage: `.oldestinby <room> <user>`")
            
            await ctx.send(embed=embed)
        else:
            pass

    
    # CMD-LATESTWITH
    @commands.command()
    @commands.check(functions.beta_tester)
    async def latestwith(self, ctx, user1, user2):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        
        user1_account = functions.check_account_existence_and_return(user1)
        user2_account = functions.check_account_existence_and_return(user2)
        if user1_account and user2_account:
            user1_feed = len(functions.id_to_feed(user1_account['account_id']))
            if user1_feed:
                print("get photos with") # REMOVEME
                photoswith = functions.together(user1_account['account_id'], user2_account['account_id'])
                if photoswith:
                    print("latestwith") # REMOVEME
                    latestwith = photoswith[0]
                    
                    embed = functions.image_embed(latestwith)
                else:
                    embed = functions.error_msg(ctx, f"Couldn't find any post that features both `@{user1_account['username']}` and `@{user2_account['username']}`!")
            else:
                embed = functions.error_msg(ctx, f"Couldn't find any post that features both `@{user1_account['username']}` and `@{user2_account['username']}`!")
        else:
            embed = functions.error_msg(ctx, f"Either `@{user1}` or `@{user2}` don't exist!")

        print("send") # REMOVEME
        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(f"Latest with both `@{user1_account['username']}` and `@{user2_account['username']}`", embed=embed)

    @latestwith.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in two users! Usage: `.latestwith <user1> <user2>`")
            
            await ctx.send(embed=embed)
        else:
            pass


    # CMD-OLDESTWITH
    @commands.command()
    @commands.check(functions.beta_tester)
    async def oldestwith(self, ctx, user1, user2):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        
        user1_account = functions.check_account_existence_and_return(user1)
        user2_account = functions.check_account_existence_and_return(user2)
        if user1_account and user2_account:
            user1_feed = len(functions.id_to_feed(user1_account['account_id']))
            if user1_feed:
                print("get photos with") # REMOVEME
                photoswith = functions.together(user1_account['account_id'], user2_account['account_id'])
                if photoswith:
                    print("oldestwith") # REMOVEME
                    oldestwith = photoswith[len(photoswith)-1]

                    embed = functions.image_embed(oldestwith)
                else:
                    embed = functions.error_msg(ctx, f"Couldn't find any post that features both `@{user1_account['username']}` and `@{user2_account['username']}`!")
            else:
                embed = functions.error_msg(ctx, f"Couldn't find any post that features both `@{user1_account['username']}` and `@{user2_account['username']}`!")
        else:
            embed = functions.error_msg(ctx, f"Either `@{user1}` or `@{user2}` don't exist!")

        print("send") # REMOVEME
        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(f"Oldest with both `@{user1_account['username']}` and `@{user2_account['username']}`", embed=embed)

    @oldestwith.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in two users! Usage: `.oldestwith <user1> <user2>`")
            
            await ctx.send(embed=embed)
        else:
            pass

    
    # CMD-ANNIVERSARY
    @commands.command()
    @commands.check(functions.beta_tester)
    async def anniversary(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        await ctx.send("trol")

    @anniversary.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            await ctx.send(embed=embed)
        else:
            pass


    #CMD-FRONTPAGE
    @commands.command()
    @commands.check(functions.beta_tester)
    async def frontpage(self, ctx):
        global images
        images = requests.get("https://api.rec.net/api/images/v3/feed/global?take=51").json()
        pages = menus.MenuPages(source=ImageMenu(range(1, 51)), clear_reactions_after=True)
        await pages.start(ctx)


    #CMD-FEED
    @commands.command()
    @commands.check(functions.beta_tester)
    async def feed(self, ctx, username):
        account = functions.check_account_existence_and_return(username)

        if account:
            global images
            images = requests.get(f"https://api.rec.net/api/images/v3/feed/player/{account['account_id']}?take=9999999").json()
            if images:
                pages = menus.MenuPages(source=ImageMenu(range(1, len(images)+1)), clear_reactions_after=True)
                await pages.start(ctx)
            else:
                embed = functions.error_msg(ctx, f"User `@{username}` isn't tagged in a single picture!")
                await ctx.send(embed=embed)

        else:
            embed = functions.error_msg(ctx, f"User `@{username}` doesn't exist!")
            await ctx.send(embed=embed)

    @feed.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            await ctx.send(embed=embed)
        else:
            pass


    #CMD-PHOTOS
    @commands.command()
    @commands.check(functions.beta_tester)
    async def photos(self, ctx, username):
        account = functions.check_account_existence_and_return(username)

        if account:
            global images
            images = requests.get(f"https://api.rec.net/api/images/v4/player/{account['account_id']}?take=9999999").json()
            if images:
                pages = menus.MenuPages(source=ImageMenu(range(1, len(images)+1)), clear_reactions_after=True)
                await pages.start(ctx)
            else:
                embed = functions.error_msg(ctx, f"User `@{username}` hasn't shared a single picture!")
                await ctx.send(embed=embed)

        else:
            embed = functions.error_msg(ctx, f"User `@{username}` doesn't exist!")
            await ctx.send(embed=embed)

    @photos.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            await ctx.send(embed=embed)
        else:
            pass

class FeedMenu(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, entries):
        global feed
        offset = menu.current_page * self.per_page

        post = feed[offset]
        
        tagged = functions.get_tagged_accounts_string(post)
        
        self_cheer_string = ""
        cheers = requests.get(f"https://api.rec.net/api/images/v1/{post['Id']}/cheers").json()
        if post['PlayerId'] in cheers:
            self_cheer_string = "\n*SELF CHEERED!*"

        room_name = functions.id_to_room_name(post['RoomId'])
        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title=f"🔗 Feed post #{offset+1}",
            description=f"🚪 [`^{room_name}`](https://rec.net/room/{room_name})\n<:CheerGeneral:803244099510861885> `{post['CheerCount']}` 💬 `{post['CommentCount']}`{self_cheer_string}\n📆 `{post['CreatedAt'][:10]}` ⏰ `{post['CreatedAt'][11:16]} UTX`\n{tagged}\n",
            url=f"https://rec.net/image/{post['Id']}"
        )

        comments = ""
        if post['CommentCount']:
            comment_json = requests.get(f"https://api.rec.net/api/images/v1/{post['Id']}/comments").json()

            bulk = "https://accounts.rec.net/account/bulk?"

            comment_section = {}
            comments = "💬 **Comments:**\n\n"
            for comment in comment_json:
                #commentor = functions.id_to_username(comment['PlayerId'])
                bulk += f"&id={comment['PlayerId']}"
                comment_section[comment['PlayerId']] = comment['Comment']

            bulk_account_call = requests.get(bulk).json()

            old_count = 0
            count = 0
            for account in bulk_account_call:
                #comments += f"👤 [`@{account['username']}`](https://rec.net/user/{account['username']})\n💬 `{comment_json[count]['Comment']}` \n\n"
                comments += f"[`@{account['username']}`](https://rec.net/user/{account['username']})\n`{comment_section[account['accountId']]}`\n\n"
                count += 1
                if len(comments) < 800:
                    embed.add_field(name="⠀", value=comments, inline=True)
                    comments = ""
                    old_count = count
            if count > old_count:
                embed.add_field(name="⠀", value=comments, inline=True)

        poster_username = functions.id_to_username(post['PlayerId'])
        embed.set_author(name=f"{poster_username}'s profile", url=f"https://rec.net/user/{poster_username}", icon_url=functions.id_to_pfp(post['PlayerId'], True))
        embed.set_image(url=f"http://img.rec.net/{post['ImageName']}?width=720")

        return embed

class PhotosMenu(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)

    async def format_page(self, menu, entries):
        global photos
        offset = menu.current_page * self.per_page

        post = photos[offset]
        
        tagged = functions.get_tagged_accounts_string(post)
        
        self_cheer_string = ""
        cheers = requests.get(f"https://api.rec.net/api/images/v1/{post['Id']}/cheers").json()
        if post['PlayerId'] in cheers:
            self_cheer_string = "\n*SELF CHEERED!*"

        room_name = functions.id_to_room_name(post['RoomId'])
        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title=f"🔗 Photo post #{offset+1}",
            description=f"🚪 [`^{room_name}`](https://rec.net/room/{room_name})\n<:CheerGeneral:803244099510861885> `{post['CheerCount']}` 💬 `{post['CommentCount']}`{self_cheer_string}\n📆 `{post['CreatedAt'][:10]}` ⏰ `{post['CreatedAt'][11:16]} UTX`\n{tagged}\n",
            url=f"https://rec.net/image/{post['Id']}"
        )

        comments = ""
        if post['CommentCount']:
            comment_json = requests.get(f"https://api.rec.net/api/images/v1/{post['Id']}/comments").json()

            bulk = "https://accounts.rec.net/account/bulk?"

            comment_section = {}
            comments = "💬 **Comments:**\n\n"
            for comment in comment_json:
                #commentor = functions.id_to_username(comment['PlayerId'])
                bulk += f"&id={comment['PlayerId']}"
                comment_section[comment['PlayerId']] = comment['Comment']

            bulk_account_call = requests.get(bulk).json()

            old_count = 0
            count = 0
            for account in bulk_account_call:
                #comments += f"👤 [`@{account['username']}`](https://rec.net/user/{account['username']})\n💬 `{comment_json[count]['Comment']}` \n\n"
                comments += f"[`@{account['username']}`](https://rec.net/user/{account['username']})\n`{comment_section[account['accountId']]}`\n\n"
                count += 1
                if len(comments) < 800:
                    embed.add_field(name="⠀", value=comments, inline=True)
                    comments = ""
                    old_count = count
            if count > old_count:
                embed.add_field(name="⠀", value=comments, inline=True)

        poster_username = functions.id_to_username(post['PlayerId'])
        embed.set_author(name=f"{poster_username}'s profile", url=f"https://rec.net/user/{poster_username}", icon_url=functions.id_to_pfp(post['PlayerId'], True))
        embed.set_image(url=f"http://img.rec.net/{post['ImageName']}?width=720")

        return embed

class ImageMenu(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=1)
        

    async def format_page(self, menu, entries):
        global images
        offset = menu.current_page * self.per_page

        post = images[offset]
        
        tagged = functions.get_tagged_accounts_string(post)
        
        self_cheer_string = ""
        cheers = requests.get(f"https://api.rec.net/api/images/v1/{post['Id']}/cheers").json()
        if post['PlayerId'] in cheers:
            self_cheer_string = "\n*SELF CHEERED!*"

        room_name = functions.id_to_room_name(post['RoomId'])
        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title=f"🔗 Post #{offset+1}",
            description=f"🚪 [`^{room_name}`](https://rec.net/room/{room_name})\n<:CheerGeneral:803244099510861885> `{post['CheerCount']}` 💬 `{post['CommentCount']}`{self_cheer_string}\n📆 `{post['CreatedAt'][:10]}` ⏰ `{post['CreatedAt'][11:16]} UTX`\n{tagged}\n",
            url=f"https://rec.net/image/{post['Id']}"
        )

        comments = ""
        if post['CommentCount']:
            comment_json = requests.get(f"https://api.rec.net/api/images/v1/{post['Id']}/comments").json()

            bulk = "https://accounts.rec.net/account/bulk?"

            comment_section = {}
            comments = "💬 **Comments:**\n\n"
            for comment in comment_json:
                #commentor = functions.id_to_username(comment['PlayerId'])
                bulk += f"&id={comment['PlayerId']}"
                comment_section[comment['PlayerId']] = comment['Comment']

            bulk_account_call = requests.get(bulk).json()

            old_count = 0
            count = 0
            for account in bulk_account_call:
                #comments += f"👤 [`@{account['username']}`](https://rec.net/user/{account['username']})\n💬 `{comment_json[count]['Comment']}` \n\n"
                comments += f"[`@{account['username']}`](https://rec.net/user/{account['username']})\n`{comment_section[account['accountId']]}`\n\n"
                count += 1
                if len(comments) < 800:
                    embed.add_field(name="⠀", value=comments, inline=True)
                    comments = ""
                    old_count = count
            if count > old_count:
                embed.add_field(name="⠀", value=comments, inline=True)

        poster_username = functions.id_to_username(post['PlayerId'])
        embed.set_author(name=f"{poster_username}'s profile", url=f"https://rec.net/user/{poster_username}", icon_url=functions.id_to_pfp(post['PlayerId'], True))
        embed.set_image(url=f"http://img.rec.net/{post['ImageName']}?width=720")

        return embed

def setup(client):
    client.add_cog(Utility(client))