import functions
import httpx
import requests
import discord
import aiohttp
import operator
import random
import asyncio
from datetime import date
from discord.ext import tasks
from discord.ext import owoify
from discord.ext import commands
from discord.ext import menus
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType


def convert_platform_mask(i):
    chk_tuple = ('Steam', 'Oculus', 'PlayStation', 'Xbox', 'HeadlessBot', 'iOS', 'Android')
    output = []
    pos = 0
    while i:
        if i & 1:
            output.append(chk_tuple[pos])
        pos += 1
        i >>= 1
    return output


async def cheers_worker(isbn, account_id):
    limits = httpx.Limits(max_keepalive_connections=10, max_connections=100)
    async with httpx.AsyncClient(limits=limits) as client:
        for a, b in enumerate(isbn):
            response = await client.get(f"https://api.rec.net/api/images/v1/{b}/cheers")
            cheers = response.json()
            if account_id in cheers:
                global self_cheers
                self_cheers += 1
                if self_cheers == 1:
                    global latest_self_cheered
                    latest_self_cheered = httpx.get(f"https://api.rec.net/api/images/v4/{b}").json()
                print(self_cheers)


async def main(account_id, photos):
    global self_cheers
    global latest_self_cheered
    self_cheers = 0
    latest_self_cheered = ""
    photo_list = []

    for image in photos:
        if image['CheerCount'] > 0:
            photo_list.append(image['Id'])
    tasks = []
    ids = []

    for a, b in enumerate(photo_list):
        ids.append(b)
        if len(ids) > len(photo_list) / 200:
            tasks.append(cheers_worker(ids, account_id))
            ids = []
    tasks.append(cheers_worker(ids, account_id))
    await asyncio.gather(*tasks)

    print("return")
    return [self_cheers, latest_self_cheered]


class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.session_message = {}
        self.buttons = {
            "default": {
                "bio": [
                    [
                        Button(style=ButtonStyle.red, label="Owoify"),
                        Button(style=ButtonStyle.red, label="Check Cringe Rating")
                    ],
                ],
                "rinfo": [
                    [
                        Button(style=ButtonStyle.red, label="Roles"),
                        Button(style=ButtonStyle.red, label="Rooms by Creator")
                    ]
                ],
                "stats": [
                    [
                        Button(style=ButtonStyle.red, label="Self-Cheers"),
                        Button(style=ButtonStyle.red, label="Bookmarked")
                    ]
                ],
                "profile": [
                    [
                        Button(style=ButtonStyle.red, label="Stats")
                    ]
                ],
                "creatorstats": [
                    [
                        Button(style=ButtonStyle.red, label="Profile")
                    ]
                ],
                "roomsby": [
                    [
                        Button(style=ButtonStyle.red, label="Profile")
                    ]
                ],
                "pfp": [
                    [
                        Button(style=ButtonStyle.red, label="Profile")
                    ]
                ],
                "banner": [
                    [
                        Button(style=ButtonStyle.red, label="Profile")
                    ]
                ],
                "junior": [
                    [
                        Button(style=ButtonStyle.red, label="Profile")
                    ]
                ],
                "date": [
                    [
                        Button(style=ButtonStyle.red, label="Profile")
                    ]
                ],
                "nickname": [
                    [
                        Button(style=ButtonStyle.red, label="Profile")
                    ]
                ]
            },
            "disabled": {
                "bio": [
                    [
                        Button(style=ButtonStyle.red, label="Owoify", disabled=True),
                        Button(style=ButtonStyle.red, label="Check Cringe Rating", disabled=True)
                    ]
                ],
                "rinfo": [
                    [
                        Button(style=ButtonStyle.red, label="Roles", disabled=True),
                        Button(style=ButtonStyle.red, label="Rooms by Creator", disabled=True)
                    ]
                ],
                "stats": [
                    [
                        Button(style=ButtonStyle.red, label="Self-Cheers", disabled=True),
                        Button(style=ButtonStyle.red, label="Bookmarked", disabled=True)
                    ]
                ],
                "profile": [
                    [
                        Button(style=ButtonStyle.red, label="Stats", disabled=True)
                    ]
                ],
                "creatorstats": [
                    [
                        Button(style=ButtonStyle.red, label="Profile", disabled=True)
                    ]
                ],
                "roomsby": [
                    [
                        Button(style=ButtonStyle.red, label="Profile", disabled=True)
                    ]
                ],
                "pfp": [
                    [
                        Button(style=ButtonStyle.red, label="Profile", disabled=True)
                    ]
                ],
                "banner": [
                    [
                        Button(style=ButtonStyle.red, label="Profile", disabled=True)
                    ]
                ],
                "junior": [
                    [
                        Button(style=ButtonStyle.red, label="Profile", disabled=True)
                    ]
                ],
                "date": [
                    [
                        Button(style=ButtonStyle.red, label="Profile", disabled=True)
                    ]
                ],
                "nickname": [
                    [
                        Button(style=ButtonStyle.red, label="Profile", disabled=True)
                    ]
                ]
            }
        }
        self.session_message = {}
        DiscordComponents(client)

    # UTILITY COMMANDS

    # CMD-TRACKROOM
    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.check(functions.is_it_me)
    async def trackroom(self, ctx, room_name, channel: discord.TextChannel = None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        if not channel:
            channel = ctx.channel

        room = functions.get_room_json(room_name)
        if not room:
            embed = functions.error_msg(ctx, f"Room `^{room_name}` doesn't exist or is private!")
            embed = functions.embed_footer(ctx, embed)
            return await ctx.send(embed=embed)

        em = discord.Embed(
            title="Track Room Statistics",
            description=f"This will automatically send room statistics for [`^{room['Name']}`](https://rec.net/rooms/{room['Name']}) in <#{channel.id}> every day for 7 days.\nConfirm?",
            colour=discord.Colour.orange()
        )
        confirm = await Confirm(em).prompt(ctx)
        if confirm:
            self.trackroomtask.start(ctx, room_name)

    @tasks.loop(hours=24, count=7)
    async def trackroomtask(self, ctx, room):
        room_embed = functions.room_embed_stats(room, False, ctx)
        functions.embed_footer(ctx, room_embed)
        date_ = str(date.today())
        await ctx.send(f"{date_[8:10]}. {functions.months[date_[5:7]]} {date_[0:4]}", embed=room_embed)

    @trackroom.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.CheckFailure):
            embed = functions.error_msg(ctx, "You must be an administrator to use this command.")

            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in a room!")

            await ctx.send(embed=embed)
        else:
            raise error

    """
    Cringe bio check is here just to make my life easier. yayayayayayayayayayay
    """

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

            embed = functions.default_embed()
            embed.add_field(name=f"{account['username']}'s bio:", value=f"```{bio}```")

            flags = ""
            cringe_check_list = requests.get(
                "https://raw.githubusercontent.com/Jegarde/RecNetBotV2/master/cringe_word_list.json")
            if cringe_check_list.ok:
                cringe_check_list = cringe_check_list.json()
            else:
                cringe_check_list = functions.load("cringe_word_list.json")
            cringe_score = 0
            cringe_rating_dict = {
                0: "Not cringe!",
                1: "A little cringe!",
                2: "Cringe!",
                3: "Very cringe!",
                4: "Yikes..!",
                5: "Radically cringe!",
                6: "Super cringe!",
                7: "Mega cringe!",
                8: "Ultra cringe!",
                9: "THE CRINGIEST!",
                10: "All hope for humanity has been lost!"
            }

            if bio:
                split_bio = bio.split(" ")
                for word in split_bio:
                    for flag in cringe_check_list:
                        if flag.casefold() in word.casefold():
                            cringe_score += 1
                            flags += f"`{flag}`, "

                if cringe_score > len(cringe_rating_dict) - 1:
                    cringe_rating = cringe_rating_dict[len(cringe_rating_dict) - 1]
                else:
                    cringe_rating = cringe_rating_dict[cringe_score]

                embed.add_field(name="Cringe score", value=f"`{cringe_score}` ({cringe_rating})",
                                inline=False)

                if flags:
                    embed.add_field(name="Flags",
                                    value=f"||{flags}||\nThis command is just for fun, and not meant to shame anybody!",
                                    inline=False)

            embed.set_author(name=f"🔗 {account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}", icon_url=pfp)
            """
            if cringe_score >= 5:
                bios = functions.load("cringe_bios.json")
                i = 0
                for item in bios:
                    if str(item[0]) == str(account['account_id']):
                        bios.pop(i)
                        break
                    i += 1

                bios.append([account['account_id'], bio])

                functions.save("cringe_bios.json", bios)
            """
        else:
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(embed=embed)

    @cringebiocheck.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")

            await ctx.send(embed=embed)
        else:
            raise error

    # CMD-OWOIFY
    @commands.command(aliases=["owo"])
    @commands.check(functions.beta_tester)
    async def owoify(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if account:
            bio = functions.get_bio(account['account_id'])
            pfp = functions.id_to_pfp(account['account_id'], True)

            print(f"{ctx.command} > {account['account_id']}, {account['username']}, {bio}, {pfp}")

            embed = functions.default_embed()
            embed.add_field(name=f"{account['username']}'s owofied bio:", value=f"```{owoify.owoify(bio)}```")

            embed.set_author(name=f"🔗 {account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}", icon_url=pfp)
        else:
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(embed=embed)

    @owoify.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")

            await ctx.send(embed=embed)
        else:
            raise error

    @commands.command()
    @commands.check(functions.beta_tester)
    async def rectnet(self, ctx):
        cheers = functions.cheers_in_room()
        await ctx.send(
            f"<@{ctx.author.id}>\n**Cheers:** `{cheers['cheers']}`\n**Images taken:** `{cheers['image_count']}`\n\n**On frontpage: ** `{cheers['frontpage_count']}` (top 100)")

    # CMD-PLATFORMS
    @commands.command(aliases=["pf", "platform", "device", "devices"])
    async def platforms(self, ctx, username):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(username)
        if account:
            platform_icons = {
                "Steam": "<:Steam:841761616193257474>",
                "Oculus": "<:Oculus:841761615682469890>",
                "PlayStation": "<:PlayStation:841761615514697800>",
                "Xbox": "<:Xbox:841761617129242674>",
                "iOS": "<:iOS:841761614734688297>",
                "Android": "<:android:870734160585703424>"
            }

            platform_str = "`Unknown!`"
            platforms = account['platforms']
            if platforms:
                platform_str = ""
                platform_list = convert_platform_mask(platforms)
                for platform in platform_list:
                    platform_str += f"{platform_icons[platform]} `{platform}`, "
                platform_str = platform_str[:-2]

            embed = discord.Embed(
                title=f"@{account['username']}'s platform(s)!",
                description=platform_str + "\n*Note: This might be inaccurate!*",
                colour=discord.Colour.orange()
            )

            embed = functions.embed_footer(ctx, embed)
            embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}",
                             icon_url=functions.id_to_pfp(account['account_id']))
            await ctx.send(embed=embed)
        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{username}` doesn't exist!")
            await ctx.send(embed=embed)

    @platforms.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")

            await ctx.send(embed=embed)
        else:
            raise error

    # CMD-LEVEL
    @commands.command(aliases=["lvl"])
    async def level(self, ctx, username):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(username)
        if account:
            prog = functions.id_to_progression(account['account_id'])
            if not prog:
                embed = functions.error_msg(ctx, f"Couldn't fetch `@{username}`'s level!")
                return await ctx.send(embed=embed)

            embed = discord.Embed(
                title=f"@{account['username']}'s level!",
                description=f"Level: `{prog['Level']}`\nXP: `{prog['XP']}`",
                colour=discord.Colour.orange()
            )

            embed = functions.embed_footer(ctx, embed)
            embed.set_author(name=f"{account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}",
                             icon_url=functions.id_to_pfp(account['account_id']))
            await ctx.send(embed=embed)
        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{username}` doesn't exist!")
            await ctx.send(embed=embed)

    @level.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")

            await ctx.send(embed=embed)
        else:
            raise error

    # CMD-ROLES
    @commands.command()
    async def roles(self, ctx, room):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        response = functions.get_room_json(room)
        if response:
            room_data = response
            roles_data = room_data['Roles']

            role_stats = {
                "255": 0,
                "30": 0,
                "31": 0,
                "20": 0,
                "10": 0,
                "0": 0
            }

            i = 0
            users = []
            user_bulk = "https://accounts.rec.net/account/bulk?"
            for user in roles_data:
                if not user['Role']:
                    continue
                user_bulk += F"&id={user['AccountId']}"
                print(str(user['Role']))
                role_stats[str(user['Role'])] += 1
                i += 1
                if i >= 100:
                    print("Over hunna!")
                    i = 0
                    response = requests.get(user_bulk)
                    users = users + response.json()
                    user_bulk = "https://accounts.rec.net/account/bulk?"

            if user_bulk != "https://accounts.rec.net/account/bulk?":
                print("left overs!")
                response = requests.get(user_bulk)
                users = users + response.json()

            users = sorted(users, key=lambda k: k['displayName'])

            i = 0
            msg = ""
            for user in users:
                role_dict = {
                    255: "**Owner**",
                    31: "Unknown!",
                    30: "`Co-Owner`",
                    20: "*Moderator*",
                    10: "Host",
                    0: "Unknown!!"
                }

                role = "UNKNOWN"
                for roled in roles_data:
                    if roled['AccountId'] == user['accountId']:
                        role = role_dict[roled['Role']]

                msg += f"[{user['displayName']}](https://rec.net/user/{user['username']}): {role}\n"
                if len(msg) > 1800:
                    embed = discord.Embed(
                        title=f"Users with a role in ^{room_data['Name']}",
                        colour=discord.Colour.orange(),
                        description=msg
                    )
                    embed = functions.embed_footer(ctx, embed)
                    await ctx.send(embed=embed)
                    msg = ""

            if msg:
                embed = discord.Embed(
                    title=f"Users with a role in ^{room_data['Name']}",
                    colour=discord.Colour.orange(),
                    description=msg
                )
                embed = functions.embed_footer(ctx, embed)
                await ctx.send(embed=embed)

            embed = discord.Embed(
                title=f"Conclusion ({room_data['Name']})",
                description=f"**Users with a role:** `{len(roles_data)}`\nCo-Owners: `{role_stats['30']}`\nModerators: `{role_stats['20']}`\nHosts: `{role_stats['10']}`",
                colour=discord.Colour.orange(),
                url=f"https://rec.net/room/{room_data['Name']}",
            )
            embed.set_thumbnail(url=f"https://img.rec.net/{room_data['ImageName']}?width=480")
            embed = functions.embed_footer(ctx, embed)
            return await ctx.send(embed=embed)
        else:
            room_embed = functions.error_msg(ctx, f"Room `^{room}` doesn't exist!")
            functions.embed_footer(ctx, room_embed)
            return await ctx.send(embed=room_embed)

    @roles.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in a room!")

            await ctx.send(embed=embed)
        else:
            raise error

    # CMD-SELFCHEERS
    @commands.command(aliases=["selfc"])
    async def selfcheers(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        author = f"<@{ctx.author.id}>"

        self_cheers = 0
        latest_self_cheered = ""

        print("check account")  # REMOVETHIS
        account = functions.check_account_existence_and_return(profile)
        if account:
            print("embed")  # REMOVETHIS
            embed = discord.Embed(
                title=f"<a:spinning:804022054822346823> Getting @{account['username']}'s self-cheered posts...",
                description="This shouldn't take too long.",
                colour=discord.Colour.orange()
            )

            print("send embed loading")  # REMOVETHIS
            functions.embed_footer(ctx, embed)
            loading = await ctx.send(embed=embed)

            photos = httpx.get(f"https://api.rec.net/api/images/v4/player/{account['account_id']}?take=10000000").json()

            # ye
            self_cheer_data = await main(account['account_id'], photos)
            self_cheers = self_cheer_data[0]
            latest_self_cheer = self_cheer_data[1]
            print(f"returned: {self_cheers}")

            pfp = functions.id_to_pfp(account['account_id'])
            if self_cheers:
                percentage = round(self_cheers / len(photos) * 100, 2)
                result_string = f"Self cheered: `{self_cheers}`\n*That's `{percentage}%` of their posts!*\n\n[Latest self-cheered post](https://rec.net/image/{latest_self_cheer['Id']})"

                embed = discord.Embed(
                    title=f"@{account['username']}'s self-cheered posts!",
                    description=result_string,
                    colour=discord.Colour.orange()
                )
                embed.set_author(name=f"{account['username']}'s profile",
                                 url=f"https://rec.net/user/{account['username']}", icon_url=pfp)
                embed.set_image(url=f"https://img.rec.net/{latest_self_cheer['ImageName']}?width=720")
            else:
                result_string = f"No self cheers, `@{account['username']}` is pure! <:CheerSport:803244185447956490>"
                embed = functions.error_msg(ctx, result_string)
                embed.set_author(name=f"{account['username']}'s profile",
                                 url=f"https://rec.net/user/{account['username']}", icon_url=pfp)
                embed.set_thumbnail(url=pfp)

        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        try:
            await loading.delete()
            pfp = functions.id_to_pfp(account['account_id'], True)
            embed.set_author(name=f"{account['username']}'s profile", url=f"https://rec.net/user/{account['username']}",
                             icon_url=pfp)
            embed.set_thumbnail(url=pfp)
        except:
            pass
        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(author, embed=embed)

    @selfcheers.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")

            await ctx.send(embed=embed)
        else:
            pass

    # CMD-INFRONTPAGE
    @commands.command(aliases=['IFP', 'BL', 'BLACKLISTED'])
    @commands.check(functions.beta_tester)
    async def infrontpage(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        account = functions.check_account_existence_and_return(profile)
        if account:
            latest_comment = ""
            blacklisted = True
            post_ = None
            frontpage = requests.get("https://api.rec.net/api/images/v3/feed/global?take=500").json()
            count = 1
            for post in frontpage:
                count += 1
                if post['PlayerId'] == account['account_id']:
                    blacklisted = False
                    post_ = post
                    break

            if blacklisted:
                title_string = f"@{account['username']} is not in front page!"
                description = f"No `@{account['username']}`'s post was found in [RecNet](https://rec.net)'s front page!"
            else:
                response = requests.get(f"https://api.rec.net/api/images/v1/{post['Id']}/comments")
                if response.ok:
                    comments = response.json()
                    if comments:
                        latest_comment = {"user": functions.id_to_username(comments[-1]['PlayerId']),
                                          "comment": comments[-1]['Comment']}
                    else:
                        latest_comment = ""
                else:
                    latest_comment = ""

                title_string = f"@{account['username']} is in front page!"
                description = f"Their [post](https://rec.net/image/{post['Id']}) appears in `#{count - 1}`.\n<:CheerGeneral:803244099510861885> `{post['CheerCount']}` 💬 `{post['CommentCount']}`"

            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title=title_string,
                description=description
            )

            if latest_comment:
                embed.add_field(name="Latest Comment",
                                value=f"[`@{latest_comment['user']}`](https://rec.net/user/{latest_comment['user']}): {latest_comment['comment']}",
                                inline=False)

            if not blacklisted:
                embed.set_image(url=f"https://img.rec.net/{post['ImageName']}?width=720")

            pfp = functions.id_to_pfp(account['account_id'])
            embed.set_author(name=f"🔗 {account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}", icon_url=pfp)

        else:
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        if not blacklisted:
            await ctx.send(embed=embed, components=[
                Button(style=ButtonStyle.URL, label="Post", url=f"https://rec.net/image/{post['Id']}")])
        else:
            await ctx.send(embed=embed)

    @infrontpage.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")

            await ctx.send(embed=embed)
        else:
            raise error

    # CMD-BIO
    @commands.command()
    @commands.check(functions.beta_tester)
    async def bio(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        account = functions.check_account_existence_and_return(profile)
        if account:
            bio = functions.get_bio(account['account_id'])
            pfp = functions.id_to_pfp(account['account_id'], True)

            print(f"{ctx.command} > {account['account_id']}, {account['username']}, {bio}, {pfp}")

            embed = functions.default_embed()
            embed.add_field(name=f"{account['username']}'s bio:", value=f"```{bio}```")
            embed.set_author(name=f"🔗 {account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}", icon_url=pfp)
        else:
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        m = await ctx.send(
            embed=embed,
            components=self.buttons['default']['bio']
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[
                ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled']['bio'])

        if res.component.label == "Check Cringe Rating":
            await m.edit(
                components=self.buttons['disabled']['bio']
            )
            await self.cringebiocheck(ctx, profile)
        elif res.component.label == "Owoify":
            await m.edit(
                components=self.buttons['disabled']['bio']
            )
            await self.owoify(ctx, profile)

    @bio.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")

            await ctx.send(embed=embed)
        else:
            raise error

    # CMD-PFP
    @commands.command()
    @commands.check(functions.beta_tester)
    async def pfp(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        success = False
        account = functions.check_account_existence_and_return(profile)
        if account:
            pfp = functions.id_to_pfp(account['account_id'], False)
            link = functions.id_to_pfp(account['account_id'], False, False)
            print(f"{ctx.command} > {account['account_id']}, {account['username']}, {pfp}")

            embed = discord.Embed(
                colour=discord.Colour.orange(),
                description=f"[{account['username']}'s profile picture](https://rec.net/image/{link})"
            )
            embed.set_author(name=f"🔗 {account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}",
                             icon_url=functions.id_to_pfp(account['account_id'], True))
            embed.set_image(url=pfp)
            success = True
        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        if success:
            m = await ctx.send(
                embed=embed,
                components=[
                    [
                        Button(style=ButtonStyle.URL, label="Post", url=f"https://rec.net/image/{link}"),
                        Button(style=ButtonStyle.URL, label="Direct Link", url=f"https://img.rec.net/{link}"),
                        self.buttons['default']['pfp'][0][0]
                    ]
                ]
            )
        else:
            return await ctx.send(
                embed=embed
            )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[
                ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(
                components=[
                    [
                        Button(style=ButtonStyle.URL, label="Post", url=f"https://rec.net/image/{link}"),
                        Button(style=ButtonStyle.URL, label="Direct Link", url=f"https://img.rec.net/{link}"),
                        self.buttons['disabled']['pfp'][0][0]
                    ]
                ]
            )

        if res.component.label == "Profile":
            await m.edit(
                components=[
                    [
                        Button(style=ButtonStyle.URL, label="Post", url=f"https://rec.net/image/{link}"),
                        Button(style=ButtonStyle.URL, label="Direct Link", url=f"https://img.rec.net/{link}"),
                        self.buttons['disabled']['pfp'][0][0]
                    ]
                ]
            )
            await self.profile(ctx, profile)

    @pfp.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")

            await ctx.send(embed=embed)
        else:
            raise error

    # CMD-TOPSUBSCRIBED
    @commands.command(aliases=['ts'])
    @commands.check(functions.beta_tester)
    async def topsubscribed(self, ctx, username=None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        leaderboard_take = 10
        account = None
        if username:
            account = functions.check_account_existence_and_return(username)
            if account:
                leaderboard_take = 10000

        response = requests.get(f"https://clubs.rec.net/subscription/top/creators?take={leaderboard_take}")
        if response.ok:
            top_creators = response.json()
        else:
            return await ctx.send(f"Error {response.status_code} while requesting top creators!")

        print(top_creators)

        creators = {}
        embed = discord.Embed(
            title="Subscriber leaderboard",
            colour=discord.Colour.orange(),
            url="https://rec.net/top/creators"
        )
        bulk = "https://accounts.rec.net/account/bulk?"

        count = 0
        for user in top_creators:
            count += 1
            if count > 10:
                break
            creators[str(user['accountId'])] = {"username": None, "display_name": None,
                                                "subscribers": user['subscriberCount']}
            bulk += f"&id={user['accountId']}"

        print(creators)
        response = requests.get(bulk)

        if response.ok:
            creator_account_data = response.json()
        else:
            return await ctx.send(f"Error {response.status_code} while requesting creator data!")

        for user in creator_account_data:
            creators[str(user['accountId'])]['display_name'] = user['displayName']
            creators[str(user['accountId'])]['username'] = user['username']

        highlighted_in_list = False
        index = 0
        for user in top_creators:  # Makes sure everyone's in the right order
            index += 1
            if index > 10:
                break
            rank = f"{index}."
            display_name = creators[str(user['accountId'])]['display_name']

            if index == 1:
                embed.set_thumbnail(url=functions.id_to_pfp(user['accountId']))
                rank = "🥇"
            elif index == 2:
                rank = "🥈"
            elif index == 3:
                rank = "🥉"

            if account and account['account_id'] == user['accountId']:
                embed.add_field(name=f"{rank} {display_name} 🔎",
                                value=f"`{creators[str(user['accountId'])]['subscribers']:,}`\n[Profile](https://rec.net/user/{creators[str(user['accountId'])]['username']})",
                                inline=False)
                highlighted_in_list = True
            else:
                embed.add_field(name=f"{rank} {display_name}",
                                value=f"`{creators[str(user['accountId'])]['subscribers']:,}`\n[Profile](https://rec.net/user/{creators[str(user['accountId'])]['username']})",
                                inline=False)

        if account and not highlighted_in_list:
            found = False
            index = 0
            for user in top_creators:
                index += 1
                if user['accountId'] == account['account_id']:
                    embed.add_field(name=f"{index}. {account['display_name']} 🔎",
                                    value=f"`{user['subscriberCount']:,}`\n[Profile](https://rec.net/user/{account['username']})",
                                    inline=False)
                    found = True
                    break

            if not found:
                embed.add_field(name=f"User @{username} doesn't appear on the leaderboards!",
                                value="`.ts <username>`", inline=False)

        else:
            embed.add_field(name="Check someone's placement by including in their username!", value="`.ts <username>`",
                            inline=False)

        embed.add_field(name="This leaderboard is based on subscribers!",
                        value="For a more accurate *creator* leaderboard, do `.tc`!", inline=False)

        embed = functions.embed_footer(ctx, embed)
        await ctx.send(embed=embed)

    # CMD-TOPCREATORS
    @commands.command(aliases=['tc'])
    @commands.check(functions.beta_tester)
    async def topcreators(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        leaderboard_take = 100
        response = requests.get(f"https://clubs.rec.net/subscription/top/creators?take={leaderboard_take}")
        if response.ok:
            top_creators = response.json()
        else:
            return await ctx.send(f"Error {response.status_code} while requesting top creators!")

        print(top_creators)

        creators = []
        embed = discord.Embed(
            title="Creator leaderboard",
            colour=discord.Colour.orange()
        )
        bulk = "https://accounts.rec.net/account/bulk?"

        creator_score = 0

        async with aiohttp.ClientSession() as session:
            for user in top_creators:
                async with session.get(url=f"https://rooms.rec.net/rooms/ownedby/{user['accountId']}") as resp:
                    account_rooms = await resp.json()
                    if account_rooms:
                        room_count = 0
                        cheers = 0
                        favorites = 0
                        visitors = 0
                        visits = 0
                        creator_score = 0

                        for room in account_rooms:
                            if room['Name'] == "RecCenter":
                                continue
                            cheers += room['Stats']['CheerCount']
                            favorites += room['Stats']['FavoriteCount']
                            visitors += room['Stats']['VisitorCount']
                            visits += room['Stats']['VisitCount']

                            temp_room_stats_sum = room['Stats']['CheerCount'] + room['Stats']['FavoriteCount'] + \
                                                  room['Stats'][
                                                      'VisitorCount'] + room['Stats']['VisitCount']

                            room_count += 1
                            creator_score += round((cheers + favorites) / visitors * visits)

                    creators.append({"account_id": user['accountId'], "username": None, "display_name": None,
                                     "subscribers": user['subscriberCount'], "creator_score": creator_score})

                    bulk += f"&id={user['accountId']}"

        print(creators)
        response = requests.get(bulk)

        if response.ok:
            creator_account_data = response.json()
        else:
            return await ctx.send(f"Error {response.status_code} while requesting creator data!")

        for user in creator_account_data:
            index = 0
            for creator in creators:
                if creator['account_id'] == user['accountId']:
                    creator['display_name'] = user['displayName']
                    creator['username'] = user['username']
                    break
                index += 1

        def sort_by_score(list_):
            return list_['creator_score']

        creators.sort(reverse=True, key=sort_by_score)

        index = 0
        for user in creators:
            index += 1
            if index > 10:
                break
            rank = f"{index}."
            display_name = user['display_name']

            if index == 1:
                embed.set_thumbnail(url=functions.id_to_pfp(user['account_id']))
                rank = "🥇"
            elif index == 2:
                rank = "🥈"
            elif index == 3:
                rank = "🥉"

            embed.add_field(name=f"{rank} {display_name}",
                            value=f"`{user['creator_score']:,}`\n[Profile](https://rec.net/user/{user['username']})",
                            inline=False)

        embed.add_field(name="Based on my creator score algorithm!",
                        value="Calculated with total room statistics!\n||`(cheers+favorites) / visitors * visits`||\nFor the official leaderboard, do `.ts`.",
                        inline=False)

        embed = functions.embed_footer(ctx, embed)
        await ctx.send(embed=embed)

    @topcreators.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        raise error

    # CMD-BANNER
    @commands.command()
    @commands.check(functions.beta_tester)
    async def banner(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        success = False
        account = functions.check_account_existence_and_return(profile)
        if account:
            banner = functions.id_to_banner(account['account_id'], True)
            link = functions.id_to_banner(account['account_id'], False)
            print(f"{ctx.command} > {account['account_id']}, {account['username']}, {banner}")

            if not banner:
                embed = discord.Embed(
                    colour=discord.Colour.orange(),
                    description=f"{account['username']}'s banner"
                )
                banner = "https://cdn.rec.net/static/banners/default_player.png"  # replace with default banner
            else:
                embed = discord.Embed(
                    colour=discord.Colour.orange(),
                    description=f"[{account['username']}'s banner](https://rec.net/image/{link})"
                )
            embed.set_author(name=f"🔗 {account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}",
                             icon_url=functions.id_to_pfp(account['account_id']))
            embed.set_image(url=banner)
            success = True
        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        if success:
            m = await ctx.send(
                embed=embed,
                components=[
                    [
                        Button(style=ButtonStyle.URL, label="Post", url=f"https://rec.net/image/{link}"),
                        Button(style=ButtonStyle.URL, label="Direct Link", url=f"https://img.rec.net/{link}"),
                        self.buttons['default']['banner'][0][0]
                    ]
                ]
            )
        else:
            return await ctx.send(
                embed=embed
            )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[
                ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(
                components=[
                    [
                        Button(style=ButtonStyle.URL, label="Post", url=f"https://rec.net/image/{link}"),
                        Button(style=ButtonStyle.URL, label="Direct Link", url=f"https://img.rec.net/{link}"),
                        self.buttons['disabled']['banner'][0][0]
                    ]
                ]
            )

        if res.component.label == "Profile":
            await m.edit(
                components=[
                    [
                        Button(style=ButtonStyle.URL, label="Post", url=f"https://rec.net/image/{link}"),
                        Button(style=ButtonStyle.URL, label="Direct Link", url=f"https://img.rec.net/{link}"),
                        self.buttons['disabled']['banner'][0][0]
                    ]
                ]
            )
            await self.profile(ctx, profile)

    @banner.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
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
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        account = functions.check_account_existence_and_return(profile)
        if account:
            pfp = functions.id_to_pfp(account['account_id'], False)
            bio = functions.get_bio(account['account_id'])

            jr_status = "🧔 Adult account!"
            if account['junior']:
                jr_status = "🍼 Junior account!"

            embed = discord.Embed(
                colour=discord.Colour.orange(),
                description=f"**{account['display_name']}** | *@{account['username']}*\n🏅 Level: `{functions.id_to_progression(account['account_id'])['Level']}`\n```{bio}```\n{jr_status}\n📆 Joined `{functions.months[account['created_at'][5:7]]} {account['created_at'][8:10]}. {account['created_at'][0:4]}`"
            )
            embed.set_author(name=f"🔗 {account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}",
                             icon_url=functions.id_to_pfp(account['account_id'], True))
            embed.set_image(url=pfp)
        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        msg = ""
        if not account['is_username']:
            msg = f"`@{profile}` doesn't exist, this was the closest hit."

        m = await ctx.send(
            msg,
            embed=embed,
            components=[
                Button(style=ButtonStyle.URL, label="Profile", url=f"https://rec.net/user/{account['username']}"),
                self.buttons['default']['profile'][0]]
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[
                ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=[
                Button(style=ButtonStyle.URL, label="Profile", url=f"https://rec.net/user/{account['username']}"),
                self.buttons['disabled']['profile'][0]])

        if res.component.label == "Stats":
            await m.edit(
                components=[
                    Button(style=ButtonStyle.URL, label="Profile", url=f"https://rec.net/user/{account['username']}"),
                    self.buttons['disabled']['profile'][0]]
            )
            await self.stats(ctx, profile)

    @profile.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")

            await ctx.send(embed=embed)
        else:
            raise error

    # CMD-OLDER
    @commands.command()
    @commands.check(functions.beta_tester)
    async def older(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        success = False
        account = functions.check_account_existence_and_return(profile)
        if account:
            older = 100 - ((account['account_id'] / 30000000) * 100)
            created_at = account['created_at']

            embed = discord.Embed(
                colour=discord.Colour.orange(),
                description=f"This account is older than `{round(older, 2)}%` of other accounts.\n*Creation date:* `{created_at[8:10]}. {functions.months[created_at[5:7]]} {created_at[0:4]}`"
            )
            embed.set_author(name=f"🔗 {account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}",
                             icon_url=functions.id_to_pfp(account['account_id'], True))
            success = True
        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        return await ctx.send(embed=embed)

    @older.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")

            await ctx.send(embed=embed)
        else:
            raise error

    # CMD-JUNIOR
    @commands.command(aliases=['jr'])
    @commands.check(functions.beta_tester)
    async def junior(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        success = False
        account = functions.check_account_existence_and_return(profile)
        if account:
            is_junior = functions.id_to_is_junior(account['account_id'])

            print(f"{ctx.command} > {account['account_id']}, {account['username']}, {is_junior}")

            if is_junior:
                title = f"{account['username']} is a junior! 🧒"
            else:
                title = f"{account['username']} is not junior! 🧔"

            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title=title
            )
            embed.set_author(name=f"🔗 {account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}",
                             icon_url=functions.id_to_pfp(account['account_id'], True))
            success = True
        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        if success:
            m = await ctx.send(
                embed=embed,
                components=self.buttons['default']['junior']
            )
        else:
            return await ctx.send(
                embed=embed
            )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[
                ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(
                components=self.buttons['disabled']['junior']
            )

        if res.component.label == "Profile":
            await m.edit(
                components=self.buttons['disabled']['junior']
            )
            await self.profile(ctx, profile)

    @junior.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
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
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        success = False
        account = functions.check_account_existence_and_return(profile)
        if account:
            created_at = str(functions.id_to_creation_date(account['account_id']))
            today = str(date.today())
            d0 = date(int(created_at[0:4]), int(created_at[5:7]), int(created_at[8:10]))
            d1 = date(int(today[0:4]), int(today[5:7]), int(today[8:10]))
            delta = d1 - d0

            print(f"{ctx.command} > {account['account_id']}, {account['username']}, {created_at}")

            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title=f"{account['username']}'s account was created at",
                description=f"📆 `{created_at[8:10]}. {functions.months[created_at[5:7]]} {created_at[0:4]}` | `{delta.days}` days ago\n⏰ `{created_at[11:16]} UTC`"
            )
            embed.set_author(name=f"🔗 {account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}",
                             icon_url=functions.id_to_pfp(account['account_id'], True))
            success = True
        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        if success:
            m = await ctx.send(
                embed=embed,
                components=self.buttons['default']['date']
            )
        else:
            return await ctx.send(
                embed=embed
            )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[
                ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(
                components=self.buttons['disabled']['date']
            )

        if res.component.label == "Profile":
            await m.edit(
                components=self.buttons['disabled']['date']
            )
            await self.profile(ctx, profile)

    @date.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")

            await ctx.send(embed=embed)
        else:
            raise error

    # CMD-NICKNAME
    @commands.command(aliases=['displayname'])
    @commands.check(functions.beta_tester)
    async def nickname(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        success = False
        account = functions.check_account_existence_and_return(profile)
        if account:
            display_name = functions.id_to_display_name(account['account_id'])

            print(f"{ctx.command} > {account['account_id']}, {account['username']}, {display_name}")

            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title=f"{account['username']}'s display name is",
                description=f"`{display_name}`"
            )
            embed.set_author(name=f"🔗 {account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}",
                             icon_url=functions.id_to_pfp(account['account_id'], True))
            success = True
        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        if success:
            m = await ctx.send(
                embed=embed,
                components=self.buttons['default']['nickname']
            )
        else:
            return await ctx.send(
                embed=embed
            )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[
                ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(
                components=self.buttons['disabled']['nickname']
            )

        if res.component.label == "Profile":
            await m.edit(
                components=self.buttons['disabled']['nickname']
            )
            await self.profile(ctx, profile)

    @nickname.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
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
                return await ctx.send(embed=embed)
        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(
            f"Latest from `@{account['username']}`",
            embed=embed,
            components=[
                [
                    Button(style=ButtonStyle.URL, label="Post", url=f"https://rec.net/image/{latest['Id']}"),
                    Button(style=ButtonStyle.URL, label="Direct Link", url=f"https://img.rec.net/{latest['ImageName']}")
                ]
            ]
        )

    @latest.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")

            await ctx.send(embed=embed)
        else:
            raise error

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
                return await ctx.send(embed=embed)
        else:
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(f"Oldest from `@{account['username']}`", embed=embed,
                       components=[
                           [
                               Button(style=ButtonStyle.URL, label="Post", url=f"https://rec.net/image/{oldest['Id']}"),
                               Button(style=ButtonStyle.URL, label="Direct Link",
                                      url=f"https://img.rec.net/{oldest['ImageName']}")
                           ]
                       ])

    @oldest.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")

            await ctx.send(embed=embed)
        else:
            raise error

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
        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(f"Oldest feed from `@{account['username']}`", embed=embed,
                       components=[
                           [
                               Button(style=ButtonStyle.URL, label="Post",
                                      url=f"https://rec.net/image/{oldestfeed['Id']}"),
                               Button(style=ButtonStyle.URL, label="Direct Link",
                                      url=f"https://img.rec.net/{oldestfeed['ImageName']}")
                           ]
                       ])

    @oldestfeed.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
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
                return await ctx.send(embed=embed)
        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(f"Latest feed from `@{account['username']}`", embed=embed,
                       components=[
                           [
                               Button(style=ButtonStyle.URL, label="Post",
                                      url=f"https://rec.net/image/{latestfeed['Id']}"),
                               Button(style=ButtonStyle.URL, label="Direct Link",
                                      url=f"https://img.rec.net/{latestfeed['ImageName']}")
                           ]
                       ])

    @latestfeed.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
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

            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title=f"{account['username']}'s cheer statistics",
                description=f"<:CheerGeneral:803244099510861885> Total Cheers: `{cheer_data['total_cheers']}`{most_cheered_post_text}"
            )
            print("set image")
            embed.set_image(url=f"https://img.rec.net/{cheer_data['most_cheered']['ImageName']}?width=720")
            embed.set_author(name=f"🔗 {account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}",
                             icon_url=functions.id_to_pfp(account['account_id'], True))
        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(embed=embed)

    @cheers.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
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

            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title=f"{account['username']}'s comment statistics",
                description=f"💬 Total Comments: `{comment_data['total_comments']}`{most_commented_post_text}"
            )
            print("set image")
            embed.set_image(url=f"https://img.rec.net/{comment_data['most_commented']['ImageName']}?width=720")
            embed.set_author(name=f"🔗 {account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}",
                             icon_url=functions.id_to_pfp(account['account_id'], True))
        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(embed=embed)

    @comments.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
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

            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title=f"{account['username']} has shared {total_pictures:,} pictures!",
                description=f"<:CheerGeneral:803244099510861885> `{pictures_cheered:,}` of them are cheered!\n💬 `{pictures_commented:,}` of them have been commented!"
            )
            embed.set_author(name=f"🔗 {account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}",
                             icon_url=functions.id_to_pfp(account['account_id'], True))
        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(embed=embed)

    @photostats.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
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
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        account = functions.check_account_existence_and_return(profile)

        successful = False
        if account:
            photos = functions.id_to_photos(account['account_id'])
            feed = functions.id_to_feed(account['account_id'])
            total_pictures = len(photos)
            total_feed = len(feed)
            if not total_pictures:
                embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single picture!")
                return await ctx.send(embed=embed)

            all_cheers = functions.id_to_all_cheers(account['account_id'])
            pictures_cheered = total_pictures - all_cheers.count(0)
            cheer_data = functions.id_to_cheer_stats(account['account_id'])
            all_comments = functions.id_to_all_comments(account['account_id'])
            pictures_commented = total_pictures - all_comments.count(0)
            comment_data = functions.id_to_comment_stats(account['account_id'])

            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title=f"RecNet Statistics for {account['username']}!",
                description=f"Pictures shared: `{total_pictures:,}`\nPictures tagged in: `{total_feed:,}`"
            )

            # embed.add_field(name="Pictures shared", value=f"`{total_pictures}`\n", inline=True)
            # embed.add_field(name="Pictures tagged in", value=f"`{total_feed}`\n", inline=True)
            # embed.add_field(name="‎⠀", value=f"‎⠀", inline=False)

            if pictures_cheered:
                embed.add_field(name="CHEER STATISTICS",
                                value=f"Total Cheers: <:CheerGeneral:803244099510861885> `{cheer_data['total_cheers']:,}`\nUser's posts cheered: `{pictures_cheered:,}`\n[**Most cheered post**](https://rec.net/image/{cheer_data['most_cheered']['Id']})\n<:CheerGeneral:803244099510861885> `{cheer_data['most_cheered']['CheerCount']:,}` 💬 `{cheer_data['most_cheered']['CommentCount']:,}`",
                                inline=True)

            if pictures_commented:
                embed.add_field(name="COMMENT STATISTICS",
                                value=f"Total Comments: 💬 `{comment_data['total_comments']:,}`\nUser's posts commented: `{pictures_commented:,}`\n[**Most commented post**](https://rec.net/image/{comment_data['most_commented']['Id']})\n<:CheerGeneral:803244099510861885> `{comment_data['most_commented']['CheerCount']:,}` 💬 `{comment_data['most_commented']['CommentCount']:,}`\n\n",
                                inline=True)

            oldest_text = ""
            oldest = photos[-1]
            print(oldest)
            if oldest:
                oldest_text = f"[First post](https://rec.net/image/{oldest['Id']})\n"

            latest_text = ""
            latest = photos[0]
            print(latest)
            if latest:
                latest_text = f"[Latest post](https://rec.net/image/{latest['Id']})\n"

            oldestfeed_text = ""
            oldestfeed = feed[-1]
            print(oldestfeed)
            if oldestfeed:
                oldestfeed_text = f"[First appearance](https://rec.net/image/{oldestfeed['Id']})\n"

            latestfeed_text = ""
            latestfeed = feed[0]
            print(latestfeed)
            if latestfeed:
                latestfeed_text = f"[Latest appearance](https://rec.net/image/{latestfeed['Id']})"

            embed.add_field(name="OTHER POSTS",
                            value=f"{oldest_text}{latest_text}{oldestfeed_text}{latestfeed_text}", inline=False)

            pfp = functions.id_to_pfp(account['account_id'], True)
            embed.set_thumbnail(url=pfp)

            embed.set_author(name=f"🔗 {account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}",
                             icon_url=pfp)
            successful = True
        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function

        if successful:
            m = await ctx.send(
                embed=embed,
                components=self.buttons['default']['stats']
            )
        else:
            return await ctx.send(embed=embed)

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[
                ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled']['stats'])

        if res.component.label == "Self-Cheers":
            await m.edit(
                components=self.buttons['disabled']['stats']
            )
            await self.selfcheers(ctx, profile)
        elif res.component.label == "Bookmarked":
            await m.edit(
                components=self.buttons['disabled']['stats']
            )
            await self.bookmarked(ctx, profile)

    @stats.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")

            await ctx.send(embed=embed)
        else:
            pass

    # CMD-ROOM
    @commands.command(aliases=["rinfo", "roominfo"])
    @commands.check(functions.beta_tester)
    async def room(self, ctx, room_name):
        return
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        author = f"<@{ctx.author.id}>"

        embed = discord.Embed(
            description=f"<a:spinning:804022054822346823>  Getting statistics for the room `^{room_name}`...",
            colour=discord.Colour.orange()
        )
        functions.embed_footer(ctx, embed)
        loading = await ctx.send(embed=embed)

        print("Get room json")
        successful = False
        try:
            room_embed = functions.room_embed(room_name, False, ctx)
            functions.embed_footer(ctx, room_embed)
            m = await ctx.send(
                embed=room_embed,
                components=self.buttons['default']['rinfo']
            )
            successful = True
            await loading.delete()
        except:
            await loading.delete()
            room_embed = functions.error_msg(ctx, f"Room `^{room_name}` doesn't exist or is private!")
            functions.embed_footer(ctx, room_embed)
            return await ctx.send(embed=room_embed)

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[
                ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled']['rinfo'])

        if res.component.label == "Roles":
            await m.edit(
                components=self.buttons['disabled']['rinfo']
            )
            await self.roles(ctx, room_name)
        elif res.component.label == "Rooms by Creator":
            await m.edit(
                components=self.buttons['disabled']['rinfo']
            )
            await self.roomsby(ctx, functions.id_to_username(functions.get_room_json(room_name)['CreatorAccountId']))

    @room.error
    async def clear_error(self, ctx, error):
        return
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in a room!")
            await ctx.send(embed=embed)

        else:
            raise error

    # CMD-APICHECK
    @commands.command(aliases=['apicheck', "ac", "apihealth", "health"])
    @commands.check(functions.beta_tester)
    async def apistatus(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        embed = discord.Embed(
            title="API call results!",
            colour=discord.Colour.orange()
        )

        async with aiohttp.ClientSession() as session:
            async with session.get('https://ns.rec.net/') as r:
                if r.status == 200:
                    endpoints = await r.json()
                else:
                    embed = functions.error_msg(ctx, "Name server down! This isn't good, lamo.")
                    return await ctx.send(embed=embed)

            checked = 0
            healthy = 0
            for endpoint in endpoints:
                if endpoint == "CDN":
                    continue
                checked += 1
                async with session.get(endpoints[endpoint] + "/health") as r:
                    if r.status == 200:
                        health = await r.text()
                        if health == "Healthy":
                            emoji = "✅"
                            healthy += 1
                        else:
                            emoji = "❌"
                    else:
                        health = "Down!"
                        emoji = "❌"

                    embed.add_field(name=endpoint, value=f"{emoji} `{health}`")

        embed.description = f"Healthy: `{healthy}/{checked}`"
        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(embed=embed)

    @apistatus.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        raise error

    # CMD-SHORTCUTS
    @commands.command(aliases=['sc'])
    @commands.check(functions.beta_tester)
    async def shortcuts(self, ctx, username=None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        author = f"<@{ctx.author.id}>"

        embed = discord.Embed(
            title="Shortcuts for RecNet",
            colour=discord.Colour.orange()
        )

        embed.add_field(name="Rec.net", value="[Link](https://rec.net/)", inline=True)
        embed.add_field(name="Rooms", value="[Link](https://rec.net/room/browse)", inline=True)
        embed.add_field(name="Events", value="[Link](https://rec.net/event/browse)", inline=True)

        if not username:
            embed.add_field(name="LINKS TO YOUR PROFILE",
                            value="If nothing shows up below this, you didn't enter your username. `.shortcuts <username>`",
                            inline=False)
            embed.set_footer(text="Shortcuts for -")
        else:
            old_username = username
            try:
                username = functions.check_account_existence_and_return(username)["username"]
                embed.add_field(name="LINKS TO YOUR PROFILE", value=f"Account: `@{username}`", inline=False)
            except:
                embed.add_field(name="LINKS TO YOUR PROFILE", value=f"Account: `@{old_username}`", inline=False)
            embed.add_field(name="Profile", value=f"[Link](https://rec.net/user/{username})", inline=True)
            embed.add_field(name="Photos", value=f"[Link](https://rec.net/user/{username}/photos)", inline=True)
            embed.add_field(name="Rooms", value=f"[Link](https://rec.net/user/{username}/rooms)", inline=True)
            embed.add_field(name="Events", value=f"[Link](https://rec.net/user/{username}/events)", inline=True)
            embed.add_field(name="Settings", value=f"[Link](https://rec.net/user/{username}/settings)", inline=True)
            embed.add_field(name="Friends", value=f"[Link](https://rec.net/user/{username}/friends)", inline=True)
            embed.add_field(name="Subscribers", value=f"[Link](https://rec.net/user/{username}/subscribers)",
                            inline=True)
            embed.add_field(name="Subscriptions", value=f"[Link](https://rec.net/user/{username}/subscriptions)",
                            inline=True)
            embed.add_field(name="Seller stats", value="[Link](https://rec.net/seller-stats)", inline=True)
            embed.set_footer(text=f"Shortcuts for @{username}")

        functions.embed_footer(ctx, embed)
        await ctx.send(author, embed=embed)

    # CMD-PLACEMENT
    @commands.command()
    @commands.check(functions.beta_tester)
    async def placement(self, ctx, room, *tags_arg):
        if tags_arg:
            tags = " %23" + ' %23'.join(tags_arg)
        else:
            tags = None
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        room_json = functions.get_room_json(room)
        if room_json:
            placement = functions.get_room_placement(room, tags)
            print(placement)
            if not placement:
                embed = discord.Embed(
                    title=f"{room_json['Name']}'s placement on hot",
                    description=f"Room couldn't be found with tags!\nTags: `{', '.join(tags_arg)}`",
                    url=f"https://rec.net/room/{room_json['Name']}",
                    colour=discord.Colour.orange()
                )
            else:
                if not tags:
                    embed = discord.Embed(
                        title=f"{room_json['Name']}'s placement on hot",
                        description=f"🔥 `#{placement}`\nYou can include tags to filter out rooms!\n`.placement Paintball pvp 4v4`",
                        url=f"https://rec.net/room/{room_json['Name']}",
                        colour=discord.Colour.orange()
                    )
                else:
                    embed = discord.Embed(
                        title=f"{room_json['Name']}'s placement on hot",
                        description=f"🔥 `#{placement}`\nTags: `{', '.join(tags_arg)}`",
                        url=f"https://rec.net/room/{room_json['Name']}",
                        colour=discord.Colour.orange()
                    )
            embed.set_thumbnail(url=f"https://img.rec.net/{room_json['ImageName']}?width=720")
        else:
            embed = functions.error_msg(ctx, f"Room `{room}` doesn't exist!")

        functions.embed_footer(ctx, embed)
        await ctx.send(embed=embed)

    @placement.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in a room and optional tags!")

            await ctx.send(embed=embed)
        else:
            raise error

    # CMD-FEATURED
    @commands.command()
    @commands.check(functions.beta_tester)
    async def featured(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        author = f"<@{ctx.author.id}>"

        featured_rooms = functions.get_featured_rooms()
        featured_reset = requests.get("https://rooms.rec.net/featuredrooms/current").json()["EndAt"]
        today = str(date.today())
        d0 = date(int(featured_reset[0:4]), int(featured_reset[5:7]), int(featured_reset[8:10]))
        d1 = date(int(today[0:4]), int(today[5:7]), int(today[8:10]))
        delta = d0 - d1

        embed = discord.Embed(
            colour=discord.Colour.orange(),
            description="<a:spinning:804022054822346823> Getting featured rooms and their statistics..."
        )
        functions.embed_footer(ctx, embed)
        loading = await ctx.send(embed=embed)

        embed = discord.Embed(
            colour=discord.Colour.orange(),
            title="Featured rooms",
            description=f"Next rotation: `{delta.days}` days"
        )

        count = 0
        for room in featured_rooms:
            count += 1
            embed.add_field(
                name=f"{count}. ^{room['RoomName']}",
                value=f"[🔗 RecNet link](https://rec.net/room/{room['RoomName']})\nHot placement: `#{functions.get_room_placement(room['RoomName'])}`",
                inline=False
            )

        functions.embed_footer(ctx, embed)
        await loading.delete()
        await ctx.send(embed=embed)

    # CMD-TAKENINBY
    @commands.command(aliases=['ti', 'tib', 'takeninby'])
    @commands.check(functions.beta_tester)
    async def takenin(self, ctx, room, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        room_data = functions.get_room_json(room)
        if room_data:  # if room exists
            account = functions.check_account_existence_and_return(profile)
            if account:  # if account exists
                photos = functions.id_to_photos(account['account_id'])
                if photos:  # if user has posted anything
                    images = []
                    for post in photos:
                        if post['RoomId'] == room_data['RoomId']:
                            images.append(post)

                    if images:
                        pages = menus.MenuPages(source=ImageMenu(range(1, len(images) + 1), images),
                                                clear_reactions_after=True)
                        await pages.start(ctx)

                    else:  # not found
                        embed = functions.error_msg(ctx,
                                                    f"User `@{account['username']}` hasn't shared a single picture in `^{room_data['Name']}`!")
                        await ctx.send(embed=embed)
                else:
                    embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single picture!")
                    await ctx.send(embed=embed)
            else:
                embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
                await ctx.send(embed=embed)

        else:  # room doesn't exist
            embed = functions.error_msg(ctx, f"Room `^{room}` doesn't exist!")
            await ctx.send(embed=embed)

    @takenin.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in a room and an user! Usage: `.takenin <room> <user>`")

            await ctx.send(embed=embed)
        else:
            pass

    # CMD-TAKENOFBY
    @commands.command(aliases=['to', 'tob', 'takenofby'])
    @commands.check(functions.beta_tester)
    async def takenof(self, ctx, of_user, by_user):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        of_user_account = functions.check_account_existence_and_return(of_user)
        by_user_account = functions.check_account_existence_and_return(by_user)
        if of_user_account and by_user_account:  # if both exist
            of_user_feed = functions.id_to_feed(of_user_account['account_id'])
            if of_user_feed:  # if user appears anywhere
                images = []
                for post in of_user_feed:
                    if by_user_account['account_id'] == post['PlayerId']:
                        images.append(post)

                if images:
                    pages = menus.MenuPages(source=ImageMenu(range(1, len(images) + 1), images),
                                            clear_reactions_after=True)
                    await pages.start(ctx)

                else:  # not found
                    embed = functions.error_msg(ctx,
                                                f"Couldn't find any picture taken by `@{by_user_account['username']}`, that features `@{of_user_account['username']}`")
                    await ctx.send(embed=embed)
            else:
                embed = functions.error_msg(ctx, f"User `@{of_user_account['username']}` isn't tagged in any post!")
                await ctx.send(embed=embed)

        else:  # either doesn't exist
            embed = functions.error_msg(ctx, f"Either `@{of_user}` or `@{by_user}` don't exist!")
            await ctx.send(embed=embed)

    @takenof.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
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

        if of_user_account:  # if both exist
            if room_data:
                of_user_feed = functions.id_to_feed(of_user_account['account_id'])
                if of_user_feed:  # if user appears anywhere
                    images = []
                    for post in of_user_feed:
                        if room_data['RoomId'] == post['RoomId']:
                            images.append(post)

                    if images:
                        pages = menus.MenuPages(source=ImageMenu(range(1, len(images) + 1), images),
                                                clear_reactions_after=True)
                        await pages.start(ctx)

                    else:  # not found
                        embed = functions.error_msg(ctx,
                                                    f"Couldn't find any picture taken of `@{of_user_account['username']}` in `^{room_data['Name']}`!")
                        await ctx.send(embed=embed)
            else:
                embed = functions.error_msg(ctx, f"Room `^{room}` doesn't exist!")
                await ctx.send(embed=embed)

        else:  # either doesn't exist
            embed = functions.error_msg(ctx, f"User `@{of_user}` doesn't exist!")
            await ctx.send(embed=embed)

    @takenofin.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
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
        if user1_account and user2_account:  # if both exist
            user1_feed = functions.id_to_feed(user1_account['account_id'])
            if user1_feed:  # if user appears anywhere
                images = functions.together(user1_account['account_id'], user2_account['account_id'])
                if images:
                    pages = menus.MenuPages(source=ImageMenu(range(1, len(images) + 1), images),
                                            clear_reactions_after=True)
                    await pages.start(ctx)
                else:  # not found
                    embed = functions.error_msg(ctx,
                                                f"Couldn't find any post that features both `@{user1_account['username']}` and `@{user2_account['username']}`!")
                    return await ctx.send(embed=embed)
            else:
                embed = functions.error_msg(ctx,
                                            f"Couldn't find any post that features both `@{user1_account['username']}` and `@{user2_account['username']}`!")
                return await ctx.send(embed=embed)

        else:  # either doesn't exist
            embed = functions.error_msg(ctx, f"Either `@{user1}` or `@{user2}` don't exist!")
            return await ctx.send(embed=embed)

    @together.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
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
                    images = sorted(photos, key=mode, reverse=reverse_sort)

                    pages = menus.MenuPages(source=ImageMenu(range(1, len(images) + 1), images),
                                            clear_reactions_after=True)
                    await pages.start(ctx)
                else:
                    embed = functions.error_msg(ctx, "Invalid mode! Modes are `cheers`, `comments`, `latest`, `oldest`")
            else:
                embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single picture!")
                return await ctx.send(embed=embed)
        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(embed=embed)

    @sortby.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx,
                                        "Please include in an username and mode! \nUsage: `.sortby <user> <latest|oldest|cheers|comments>`")

            await ctx.send(embed=embed)
        else:
            raise error

    # CMD-ROOMSBY
    @commands.command()
    @commands.check(functions.beta_tester)
    async def roomsby(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        account = functions.check_account_existence_and_return(profile)

        success = False
        if account:
            account_rooms = functions.id_to_rooms(account['account_id'])
            if account_rooms:
                embed = discord.Embed(
                    colour=discord.Colour.orange(),
                    title=f"@{account['username']}'s (max) 10 latest rooms"
                )
                count = 0
                for room in account_rooms:
                    count += 1
                    embed.add_field(name=f"{count}. ^{room['Name']}",
                                    value=f"**Description:** ```{room['Description']}```\n**Statistics**\n<:CheerGeneral:803244099510861885> `{room['Stats']['CheerCount']:,}` *(CHEERS)*\n⭐ `{room['Stats']['FavoriteCount']:,}` *(FAVORITES)*\n👤 `{room['Stats']['VisitorCount']:,}` *(VISITORS)*\n👥 `{room['Stats']['VisitCount']:,}` *(ROOM VISITS)*",
                                    inline=False)
                    if count == 10:
                        break

                pfp = functions.id_to_pfp(account['account_id'], True)
                embed.set_author(name=f"🔗 {account['username']}'s profile",
                                 url=f"https://rec.net/user/{account['username']}", icon_url=pfp)
                success = True
            else:
                embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single room!")
                return await ctx.send(embed=embed)
        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        if success:
            m = await ctx.send(
                embed=embed,
                components=self.buttons['default']['roomsby']
            )
        else:
            return await ctx.send(
                embed=embed
            )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[
                ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled']['roomsby'])

        if res.component.label == "Profile":
            await m.edit(
                components=self.buttons['disabled']['roomsby']
            )
            await self.profile(ctx, profile)

    @roomsby.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
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
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        account = functions.check_account_existence_and_return(profile)

        success = False
        if account:
            account_rooms = functions.id_to_rooms_owned(account['account_id'])
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
                    if room['Name'] == "RecCenter":
                        continue
                    cheers += room['Stats']['CheerCount']
                    favorites += room['Stats']['FavoriteCount']
                    visitors += room['Stats']['VisitorCount']
                    visits += room['Stats']['VisitCount']
                    room_count += 1

                    temp_room_stats_sum = room['Stats']['CheerCount'] + room['Stats']['FavoriteCount'] + room['Stats'][
                        'VisitorCount'] + room['Stats']['VisitCount']
                    creator_score += round((cheers + favorites) / visitors * visits)

                    if room_count == 1:
                        best_room = room
                        best_room['RoomStatsSum'] = temp_room_stats_sum

                        worst_room = room
                        worst_room['RoomStatsSum'] = temp_room_stats_sum
                    else:
                        # print(f"BestRoom {best_room['Name']}: {best_room['RoomStatsSum']} vs {room['Name']}: {temp_room_stats_sum}")
                        # print(f"WorstRoom {worst_room['Name']}: {worst_room['RoomStatsSum']} vs {room['Name']}: {temp_room_stats_sum}")
                        if best_room['RoomStatsSum'] < temp_room_stats_sum:
                            best_room = room
                            best_room['RoomStatsSum'] = temp_room_stats_sum
                        elif worst_room['RoomStatsSum'] > temp_room_stats_sum:
                            worst_room = room
                            worst_room['RoomStatsSum'] = temp_room_stats_sum

                embed = discord.Embed(
                    colour=discord.Colour.orange(),
                    title=f"@{account['username']}'s creator statistics",
                    description=f"Rooms published: `{room_count}`\nCreator Score: `{creator_score:,}`"
                )

                embed.add_field(
                    name="Total Room Statistics",
                    value=f"<:CheerGeneral:803244099510861885> `{cheers:,}` *(CHEERS)*\n⭐ `{favorites:,}` *(FAVORITES)*\n👤 `{visitors:,}` *(VISITORS)*\n👥 `{visits:,}` *(VISITS)*",
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
                embed.set_author(name=f"🔗 {account['username']}'s profile",
                                 url=f"https://rec.net/user/{account['username']}", icon_url=pfp)
                success = True

            else:
                embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single room!")
                return await ctx.send(embed=embed)
        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        if success:
            m = await ctx.send(
                embed=embed,
                components=self.buttons['default']['roomsby']
            )
        else:
            return await ctx.send(
                embed=embed
            )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[
                ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled']['roomsby'])

        if res.component.label == "Profile":
            await m.edit(
                components=self.buttons['disabled']['roomsby']
            )
            await self.profile(ctx, profile)

    @creatorstats.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        raise error

    @roomsby.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")

            await ctx.send(embed=embed)
        else:
            raise error

    # CMD-BOOKMARKED
    @commands.command(aliases=["bookmark", "favorites", "favorite", "bm"])
    @commands.check(functions.beta_tester)
    async def bookmarked(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        author = f"<@{ctx.author.id}>"

        account = functions.check_account_existence_and_return(profile)

        if account:
            embed = discord.Embed(
                colour=discord.Colour.orange(),
                description=f"<a:spinning:804022054822346823> Looking for `@{account['username']}`'s bookmarked posts..."
            )
            functions.embed_footer(ctx, embed)
            loading = await ctx.send(embed=embed)

            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title=f"@{account['username']}'s bookmarked photos 📌",
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
                                if comment['PlayerId'] == account['account_id'] and "bookmark" in comment[
                                    'Comment'].lower():
                                    print("BOOKMARKED!!!")
                                    found_bookmarked = True
                                    count += 1
                                    if count > 25:
                                        break
                                    desc = comment['Comment'].replace('bookmark', '')
                                    print(desc)
                                    if len(desc) > 256:
                                        desc = desc[0:200] + " ..."
                                    embed.add_field(name=f"{count}. \"{desc}\"",
                                                    value=f"https://rec.net/image/{comment['SavedImageId']}",
                                                    inline=False)

            pfp = functions.id_to_pfp(account['account_id'], True)
            embed.set_author(name=f"🔗 {account['username']}'s profile",
                             url=f"https://rec.net/user/{account['username']}", icon_url=pfp)

        else:  # account doesn't exist
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        functions.embed_footer(ctx, embed)  # get default footer from function
        await loading.delete()
        if not found_bookmarked:
            embed.add_field(name="None!",
                            value="You can bookmark your own posts by commenting\n`bookmark <text>`\non a post of yours! The text you type in is there just to remind you of what the bookmarked image is, however, it's not necessary.",
                            inline=False)
        await ctx.send(f"{author}\n**Bookmarked:** `{count}/25`", embed=embed)

    @bookmarked.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")

            await ctx.send(embed=embed)
        else:
            pass

    # CMD-LATESTINBY
    @commands.command(aliases=["latestin"])
    @commands.check(functions.beta_tester)
    async def latestinby(self, ctx, room, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if account:
            total_photos = len(functions.id_to_photos(account['account_id']))
            if total_photos:
                print("get photos in")  # REMOVEME
                photosin = functions.id_to_photos_in(account['account_id'], room)
                if photosin:
                    print("latestin")  # REMOVEME
                    latestin = photosin[0]

                    embed = functions.image_embed(latestin)
                else:
                    embed = functions.error_msg(ctx,
                                                f"User `@{account['username']}` hasn't shared a single picture in `^{room}`!")
            else:
                embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single picture!")
                return await ctx.send(embed=embed)
        else:
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        print("send")  # REMOVEME
        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(f"Latest by `@{account['username']}`, in `^{room}`", embed=embed, components=[
            [
                Button(style=ButtonStyle.URL, label="Post", url=f"https://rec.net/image/{latestin['Id']}"),
                Button(style=ButtonStyle.URL, label="Direct Link", url=f"https://img.rec.net/{latestin['ImageName']}")
            ]
        ])

    @latestinby.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in a room and an user! Usage: `.latestinby <room> <user>`")

            await ctx.send(embed=embed)
        else:
            raise error

    # CMD-OLDESTINBY
    @commands.command(aliases=["oldestin"])
    @commands.check(functions.beta_tester)
    async def oldestinby(self, ctx, room, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if account:
            total_photos = len(functions.id_to_photos(account['account_id']))
            if total_photos:
                print("get photos in")  # REMOVEME
                photosin = functions.id_to_photos_in(account['account_id'], room)
                if photosin:
                    print("oldestin")  # REMOVEME
                    oldestin = photosin[len(photosin) - 1]

                    embed = functions.image_embed(oldestin)
                else:
                    embed = functions.error_msg(ctx,
                                                f"User `@{account['username']}` hasn't shared a single picture in `^{room}`!")
                    return await ctx.send(embed=embed)
            else:
                embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single picture!")
                return await ctx.send(embed=embed)
        else:
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)

        print("send")  # REMOVEME
        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(f"Oldest by `@{account['username']}`, in `^{room}`", embed=embed, components=[
            [
                Button(style=ButtonStyle.URL, label="Post", url=f"https://rec.net/image/{oldestin['Id']}"),
                Button(style=ButtonStyle.URL, label="Direct Link", url=f"https://img.rec.net/{oldestin['ImageName']}")
            ]
        ])

    @oldestinby.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
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
                print("get photos with")  # REMOVEME
                photoswith = functions.together(user1_account['account_id'], user2_account['account_id'])
                if photoswith:
                    print("latestwith")  # REMOVEME
                    latestwith = photoswith[0]

                    embed = functions.image_embed(latestwith)
                else:
                    embed = functions.error_msg(ctx,
                                                f"Couldn't find any post that features both `@{user1_account['username']}` and `@{user2_account['username']}`!")
            else:
                embed = functions.error_msg(ctx,
                                            f"Couldn't find any post that features both `@{user1_account['username']}` and `@{user2_account['username']}`!")
        else:
            embed = functions.error_msg(ctx, f"Either `@{user1}` or `@{user2}` don't exist!")

        print("send")  # REMOVEME
        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(f"Latest with both `@{user1_account['username']}` and `@{user2_account['username']}`",
                       embed=embed, components=[
                [
                    Button(style=ButtonStyle.URL, label="Post", url=f"https://rec.net/image/{latestwith['Id']}"),
                    Button(style=ButtonStyle.URL, label="Direct Link",
                           url=f"https://img.rec.net/{latestwith['ImageName']}")
                ]
            ])

    @latestwith.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
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
                print("get photos with")  # REMOVEME
                photoswith = functions.together(user1_account['account_id'], user2_account['account_id'])
                if photoswith:
                    print("oldestwith")  # REMOVEME
                    oldestwith = photoswith[len(photoswith) - 1]

                    embed = functions.image_embed(oldestwith)
                else:
                    embed = functions.error_msg(ctx,
                                                f"Couldn't find any post that features both `@{user1_account['username']}` and `@{user2_account['username']}`!")
            else:
                embed = functions.error_msg(ctx,
                                            f"Couldn't find any post that features both `@{user1_account['username']}` and `@{user2_account['username']}`!")
        else:
            embed = functions.error_msg(ctx, f"Either `@{user1}` or `@{user2}` don't exist!")

        print("send")  # REMOVEME
        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(f"Oldest with both `@{user1_account['username']}` and `@{user2_account['username']}`",
                       embed=embed, components=[
                [
                    Button(style=ButtonStyle.URL, label="Post", url=f"https://rec.net/image/{oldestwith['Id']}"),
                    Button(style=ButtonStyle.URL, label="Direct Link",
                           url=f"https://img.rec.net/{oldestwith['ImageName']}")
                ]
            ])

    @oldestwith.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
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
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            await ctx.send(embed=embed)
        else:
            pass

    # CMD-FRONTPAGE
    @commands.command()
    @commands.check(functions.beta_tester)
    async def frontpage(self, ctx):
        images = requests.get("https://api.rec.net/api/images/v3/feed/global?take=51").json()
        pages = menus.MenuPages(source=ImageMenu(range(1, 51), images), clear_reactions_after=True)
        await pages.start(ctx)

    # CMD-FEED
    @commands.command()
    @commands.check(functions.beta_tester)
    async def feed(self, ctx, username):
        account = functions.check_account_existence_and_return(username)

        if account:
            images = requests.get(
                f"https://api.rec.net/api/images/v3/feed/player/{account['account_id']}?take=9999999").json()
            if images:
                pages = menus.MenuPages(source=ImageMenu(range(1, len(images) + 1), images), clear_reactions_after=True)
                await pages.start(ctx)
            else:
                embed = functions.error_msg(ctx, f"User `@{username}` isn't tagged in a single picture!")
                await ctx.send(embed=embed)

        else:
            embed = functions.error_msg(ctx, f"User `@{username}` doesn't exist!")
            await ctx.send(embed=embed)

    @feed.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            await ctx.send(embed=embed)
        else:
            pass

    # CMD-PHOTOS
    @commands.command()
    @commands.check(functions.beta_tester)
    async def photos(self, ctx, username):
        account = functions.check_account_existence_and_return(username)

        if account:
            images = requests.get(
                f"https://api.rec.net/api/images/v4/player/{account['account_id']}?take=9999999").json()
            if images:
                pages = menus.MenuPages(source=ImageMenu(range(1, len(images) + 1), images), clear_reactions_after=True)
                await pages.start(ctx)
            else:
                embed = functions.error_msg(ctx, f"User `@{username}` hasn't shared a single picture!")
                await ctx.send(embed=embed)

        else:
            embed = functions.error_msg(ctx, f"User `@{username}` doesn't exist!")
            await ctx.send(embed=embed)

    @photos.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            await ctx.send(embed=embed)
        else:
            pass

    # CMD-EVENTSEARCH
    @commands.command(aliases=["es"])
    @commands.check(functions.beta_tester)
    async def eventsearch(self, ctx, word):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        keyword = str(word)
        if len(keyword) < 2:
            embed = functions.error_msg(ctx, "Keyword must be at least 2 characters long!")
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                colour=discord.Colour.orange(),
                title=f"Events found with keyword \"{keyword}\"",
                description="*Max. 15*"
            )

            events_found = functions.event_search(keyword)
            if not events_found:
                embed = functions.error_msg(ctx, f"No events found with the keyword `{word}`!")
                return await ctx.send(embed=embed)

            room_bulk = "https://rooms.rec.net/rooms/bulk?"
            acc_bulk = "https://accounts.rec.net/account/bulk?"
            for event in events_found:
                room_bulk += f"&id={event['RoomId']}"
                acc_bulk += f"&id={event['CreatorPlayerId']}"

            rooms = requests.get(room_bulk).json()
            accs = requests.get(acc_bulk).json()

            for event in events_found:
                if not " " + word in event['Name'].casefold():
                    continue

                if len(embed.fields) >= 15:
                    break

                embed = functions.event_embed_field(embed, event, rooms, accs)

            functions.embed_footer(ctx, embed)  # get default footer from function
            await ctx.send(embed=embed)

    @eventsearch.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in a word to search!")

            await ctx.send(embed=embed)
        else:
            raise error

    # CMD-EVENTSBY
    @commands.command(aliases=["eb"])
    @commands.check(functions.beta_tester)
    async def eventsby(self, ctx, user):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        username = str(user)
        account = functions.check_account_existence_and_return(username)
        if not account:
            embed = functions.error_msg(ctx, f"User `@{username}` doesn't exist!")
            return await ctx.send(embed=embed)

        events_found = functions.events_by(None, account['account_id'])
        if not events_found:
            embed = functions.error_msg(ctx, f"No events found that were made by `@{account['username']}`!")
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            colour=discord.Colour.orange(),
            title=f"Events made by @{account['username']}",
            description=f"\nTotal Count: `{len(events_found)}`\n*Max. 15 displayed*"
        )

        room_bulk = "https://rooms.rec.net/rooms/bulk?"
        acc_bulk = "https://accounts.rec.net/account/bulk?"
        for event in events_found:
            room_bulk += f"&id={event['RoomId']}"
            acc_bulk += f"&id={event['CreatorPlayerId']}"

        rooms = requests.get(room_bulk).json()
        accs = requests.get(acc_bulk).json()

        for event in events_found:
            if len(embed.fields) >= 15:
                break

            embed = functions.event_embed_field(embed, event, rooms, accs)

        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(
            embed=embed,
            components=[
                Button(style=ButtonStyle.URL, label="User Events",
                       url=f"https://rec.net/user/{account['username']}/events")
            ]
        )

    @eventsby.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")

            await ctx.send(embed=embed)
        else:
            raise error

    # CMD-EVENTSIN
    @commands.command(aliases=["ebi"])
    @commands.check(functions.beta_tester)
    async def eventsbyin(self, ctx, user, room):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        username = str(user)
        account = functions.check_account_existence_and_return(username)
        if not account:
            embed = functions.error_msg(ctx, f"User `@{username}` doesn't exist!")
            return await ctx.send(embed=embed)

        room_data = functions.get_room_json(room)
        if not room_data:
            embed = functions.error_msg(ctx, f"Room `^{room}` doesn't exist or is private!")
            return await ctx.send(embed=embed)

        events_found = functions.events_by(None, account['account_id'])
        if not events_found:
            embed = functions.error_msg(ctx,
                                        f"No events found that were made by `@{account['username']}` in `^{room_data['Name']}`!")
            return await ctx.send(embed=embed)

        events_in_room = []
        for event in events_found:
            if event['RoomId'] != room_data['RoomId']:
                continue

            events_in_room.append(event)

        embed = discord.Embed(
            colour=discord.Colour.orange(),
            title=f"Events made by @{account['username']} in ^{room_data['Name']}",
            description=f"Total Count: `{len(events_in_room)}`\n*Max. 15 displayed*"
        )

        room_bulk = "https://rooms.rec.net/rooms/bulk?"
        acc_bulk = "https://accounts.rec.net/account/bulk?"
        for event in events_found:
            room_bulk += f"&id={event['RoomId']}"
            acc_bulk += f"&id={event['CreatorPlayerId']}"

        rooms = requests.get(room_bulk).json()
        accs = requests.get(acc_bulk).json()

        for event in events_in_room:
            if len(embed.fields) >= 15:
                break

            embed = functions.event_embed_field(embed, event, rooms, accs)

        functions.embed_footer(ctx, embed)  # get default footer from function

        if not embed.fields:
            embed = functions.error_msg(ctx,
                                        f"No events found made by `@{account['username']}` in `^{room_data['Name']}`!")
            return await ctx.send(embed=embed)

        await ctx.send(
            embed=embed,
            components=[
                Button(style=ButtonStyle.URL, label="User Events",
                       url=f"https://rec.net/user/{account['username']}/events")
            ]
        )

    @eventsbyin.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx,
                                        "Please include in an username and room!\nExample: `.eventsbyin <username> <room>`")

            await ctx.send(embed=embed)
        else:
            raise error

    # CMD-EVENTSIN
    @commands.command(aliases=["ei"])
    @commands.check(functions.beta_tester)
    async def eventsin(self, ctx, room):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        room = str(room)

        events_found = functions.events_in(room)
        if not events_found:
            embed = functions.error_msg(ctx, f"No events found that were made by `^{room}`!")
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            colour=discord.Colour.orange(),
            title=f"Events made in ^{room}",
            description=f"\nTotal Count: `{len(events_found)}`\n*Max. 15 displayed*"
        )

        room_bulk = "https://rooms.rec.net/rooms/bulk?"
        acc_bulk = "https://accounts.rec.net/account/bulk?"
        for event in events_found:
            room_bulk += f"&id={event['RoomId']}"
            acc_bulk += f"&id={event['CreatorPlayerId']}"

        rooms = requests.get(room_bulk).json()
        accs = requests.get(acc_bulk).json()

        for event in events_found:
            if len(embed.fields) >= 15:
                break

            embed = functions.event_embed_field(embed, event, rooms, accs)

        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(
            embed=embed,
            components=[
                Button(style=ButtonStyle.URL, label="Room Events", url=f"https://rec.net/room/{room}/events")
            ]
        )

    @eventsin.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in a room!")

            await ctx.send(embed=embed)
        else:
            raise error

    # CMD-LATESTEVENTS
    @commands.command(aliases=["le"])
    @commands.check(functions.beta_tester)
    async def latestevents(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        embed = discord.Embed(
            colour=discord.Colour.orange(),
            title=f"Latest events made",
            description="*Max. 15*"
        )

        events_found = functions.latest_events()
        if not events_found:
            embed = functions.error_msg(ctx, f"No events were found!")
            return await ctx.send(embed=embed)

        room_bulk = "https://rooms.rec.net/rooms/bulk?"
        acc_bulk = "https://accounts.rec.net/account/bulk?"
        for event in events_found:
            room_bulk += f"&id={event['RoomId']}"
            acc_bulk += f"&id={event['CreatorPlayerId']}"

        rooms = requests.get(room_bulk).json()
        accs = requests.get(acc_bulk).json()

        for event in events_found:
            if len(embed.fields) >= 15:
                break

            embed = functions.event_embed_field(embed, event, rooms, accs)

        functions.embed_footer(ctx, embed)  # get default footer from function
        await ctx.send(embed=embed)

    @latestevents.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        raise error

    # CMD-gap
    @commands.command()
    @commands.check(functions.beta_tester)
    async def gap(self, ctx, profile, mode):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if not account:
            embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")
            return await ctx.send(embed=embed)
        if mode.lower() == "photos":
            photos = functions.id_to_photos(account['account_id'])
        elif mode.lower() == "feed":
            photos = functions.id_to_feed(account['account_id'])
        else:
            embed = functions.error_msg(ctx, f"Choose a mode! \n`.gap <username> <photos|feed>`")
            return await ctx.send(embed=embed)
        if not photos:
            embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared any pictures!")
            return await ctx.send(embed=embed)
        if len(photos) < 2:
            embed = functions.error_msg(ctx,
                                        f"User `@{account['username']}` hasn't shared/appeared in enough pictures!")
            return await ctx.send(embed=embed)

        acc_creation_date = account['created_at'].split("T")[0].split("-")
        acc_date = date(int(acc_creation_date[0]), int(acc_creation_date[1]), int(acc_creation_date[2]))
        share_date = date(2017, 7, 21)
        acc_created_after_sharing = acc_date > share_date and account['account_id'] != 8  # Cloud lol

        # photos.reverse()

        def group_photos(grouped_photos, photo_group, extra=None):
            photo_group.reverse()
            today = str(date.today())[0:10].split("-")
            if extra:
                photo_group = [
                    extra,
                    grouped_photos[-1][2],
                ]
            d0_date = photo_group[0]['CreatedAt'][0:10].split("-")
            d1_date = photo_group[1]['CreatedAt'][0:10].split("-")
            d0 = date(int(d0_date[0]), int(d0_date[1]), int(d0_date[2]))
            d1 = date(int(d1_date[0]), int(d1_date[1]), int(d1_date[2]))
            delta = d1 - d0
            delta = delta.days
            photo_group.insert(0, delta)
            grouped_photos.append(photo_group)
            return grouped_photos

        grouped_photos = []
        photo_group = []
        if not acc_created_after_sharing:
            photos.append({"Id": 1, "ImageName": "pNNQlbqMyUa7ialKQVviXw", "CreatedAt": "2017-07-22T02:33:40.9233333Z"})
        for post in photos:
            if len(photo_group) == 2:
                grouped_photos = group_photos(grouped_photos, photo_group)
                photo_group = []

            photo_group.append(post)

        if photo_group:
            grouped_photos = group_photos(grouped_photos, photo_group, photos[-1])

        grouped_photos = sorted(grouped_photos, key=lambda x: x[0], reverse=True)

        #for post in grouped_photos:
            #print(post[0], post[1]['Id'], post[2]['Id'])


        # print(len(grouped_photos))
        if not acc_created_after_sharing and grouped_photos[0][1]['Id'] == 1:
            await ctx.send(
                f"Longest gap between photos (`@{account['username']}`)\nMode: `{mode.lower().capitalize()}`\nGap: `{grouped_photos[0][0]} days`\nSince image sharing was introduced (`July 21st 2017`)\nhttps://rec.net/image/{grouped_photos[0][2]['Id']} (`{grouped_photos[0][2]['CreatedAt'][8:10]}. {functions.months[grouped_photos[0][2]['CreatedAt'][5:7]]} {grouped_photos[0][2]['CreatedAt'][0:4]}`)",
                components=[
                    [
                        Button(style=ButtonStyle.URL, label="Profile Link",
                               url=f"https://rec.net/user/{profile}"),
                        Button(style=ButtonStyle.URL, label="2nd Post Link",
                               url=f"https://rec.net/image/{grouped_photos[0][2]['Id']}")
                    ]
                ]
            )
        else:
            await ctx.send(
                f"Longest gap between photos (`@{account['username']}`)\nMode: `{mode.lower().capitalize()}`\nGap: `{grouped_photos[0][0]} days`\nhttps://rec.net/image/{grouped_photos[0][1]['Id']} (`{grouped_photos[0][1]['CreatedAt'][8:10]}. {functions.months[grouped_photos[0][1]['CreatedAt'][5:7]]} {grouped_photos[0][1]['CreatedAt'][0:4]}`)\nhttps://rec.net/image/{grouped_photos[0][2]['Id']} (`{grouped_photos[0][2]['CreatedAt'][8:10]}. {functions.months[grouped_photos[0][2]['CreatedAt'][5:7]]} {grouped_photos[0][2]['CreatedAt'][0:4]}`)",
                components=[
                    [
                        Button(style=ButtonStyle.URL, label="Profile Link",
                               url=f"https://rec.net/user/{profile}"),
                        Button(style=ButtonStyle.URL, label="1st Post Link",
                               url=f"https://rec.net/image/{grouped_photos[0][1]['Id']}"),
                        Button(style=ButtonStyle.URL, label="2nd Post Link",
                               url=f"https://rec.net/image/{grouped_photos[0][2]['Id']}")
                    ]
                ]
            )

    @gap.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx,
                                        "Shows the longest gap between images.\nPlease include in a username and mode!\n`.gap <usename> <photos|feed>`")

            await ctx.send(embed=embed)
        else:
            raise error


class ImageMenu(menus.ListPageSource):
    def __init__(self, data, images):
        super().__init__(data, per_page=1)
        self.images = images

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        post = self.images[offset]

        tagged = functions.get_tagged_accounts_string(post)

        self_cheer_string = ""
        cheers = requests.get(f"https://api.rec.net/api/images/v1/{post['Id']}/cheers").json()
        if post['PlayerId'] in cheers:
            self_cheer_string = "\n*SELF CHEERED!*"

        room_name = functions.id_to_room_name(post['RoomId'])
        embed = discord.Embed(
            colour=discord.Colour.orange(),
            title=f"🔗 Post {offset + 1}/{len(self.images)}",
            description=f"🚪 [`^{room_name}`](https://rec.net/room/{room_name})\n<:CheerGeneral:803244099510861885> `{post['CheerCount']}` 💬 `{post['CommentCount']}`{self_cheer_string}\n📆 `{post['CreatedAt'][8:10]}. {functions.months[post['CreatedAt'][5:7]]} {post['CreatedAt'][0:4]}`  ⏰ `{post['CreatedAt'][11:16]} UTC`\n{tagged}\n",
            url=f"https://rec.net/image/{post['Id']}"
        )

        comments = ""
        if post['CommentCount']:
            comment_json = requests.get(f"https://api.rec.net/api/images/v1/{post['Id']}/comments").json()

            bulk = "https://accounts.rec.net/account/bulk?"

            comment_section = {}
            comments = "💬 **Comments:**\n\n"
            for comment in comment_json:
                # commentor = functions.id_to_username(comment['PlayerId'])
                bulk += f"&id={comment['PlayerId']}"
                comment_section[comment['PlayerId']] = comment['Comment']

            bulk_account_call = requests.get(bulk).json()

            old_count = 0
            count = 0
            for account in bulk_account_call:
                # comments += f"👤 [`@{account['username']}`](https://rec.net/user/{account['username']})\n💬 `{comment_json[count]['Comment']}` \n\n"
                comments += f"[`@{account['username']}`](https://rec.net/user/{account['username']})\n`{comment_section[account['accountId']]}`\n\n"
                count += 1
                if len(comments) < 800:
                    embed.add_field(name="⠀", value=comments, inline=True)
                    comments = ""
                    old_count = count
            if count > old_count:
                embed.add_field(name="⠀", value=comments, inline=True)

        poster_username = functions.id_to_username(post['PlayerId'])
        embed.set_author(name=f"🔗 {poster_username}'s profile", url=f"https://rec.net/user/{poster_username}",
                         icon_url=functions.id_to_pfp(post['PlayerId'], True))
        embed.set_image(url=f"http://img.rec.net/{post['ImageName']}?width=720")

        return embed


class Confirm(menus.Menu):
    def __init__(self, embed):
        super().__init__(timeout=30.0, delete_message_after=True)
        self.embed = embed
        self.result = None

    async def send_initial_message(self, ctx, channel):
        return await channel.send(embed=self.embed)

    @menus.button('\N{WHITE HEAVY CHECK MARK}')
    async def do_confirm(self, payload):
        self.result = True
        self.stop()

    @menus.button('\N{CROSS MARK}')
    async def do_deny(self, payload):
        self.result = False
        self.stop()

    async def prompt(self, ctx):
        await self.start(ctx, wait=True)
        return self.result


def setup(client):
    client.add_cog(Utility(client))
