import functions
import requests
import discord
import random
import aiohttp
import json
from asyncio import TimeoutError, sleep
from discord.ext import commands
from discord.ext import menus
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType

class Random(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.session_message = {}
        self.buttons = {
            "default": [
                [
                    Button(style=ButtonStyle.red, label="Redo")
                ],
            ],
            "disabled": [
                [
                    Button(style=ButtonStyle.red, label="Redo", disabled=True)
                ]
            ]
        }
        DiscordComponents(client)
    # RANDOM COMMANDS

    @commands.command()
    async def waitforclick(self, ctx):
        text = str(random.randint(0, 100))

        m = await ctx.send(
            text,
            components=[
                Button(style=ButtonStyle.red, label="Click Me!"),
            ],
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=15)
            await m.delete()
            await self.waitforclick(ctx)

        except:
            await m.edit(
                "Prompt timed out!",
                components=[
                    Button(style=ButtonStyle.red, label="Timed out!", disabled=True),
                ],
            )

    # CMD-RANDOMBIO
    @commands.command(aliases=["rb", "rbio"])
    @commands.check(functions.beta_tester)
    async def randombio(self, ctx, amount=1):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session
        
        author = f"<@{ctx.author.id}>"

        if amount > 20:
            amount = 20
        elif amount < 1:
            amount = 1

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            description = f"<a:spinning:804022054822346823> Searching for {amount} random bio(s)..."
        )
        functions.embed_footer(ctx, embed)
        loading = await ctx.send(embed=embed)

        bio_list = []

        async with aiohttp.ClientSession() as session:
            for x in range(amount):
                bio = None
                while not bio:
                    account_id = random.randint(1, 20000000)
                    try:
                        async with session.get(url=f"https://accounts.rec.net/account/{account_id}/bio") as resp:
                            bio = await resp.json()
                            bio = bio["bio"]
                        if len(bio) < 5:
                            bio = None
                            continue
                    except:
                        continue
                bio_list.append({"account_id": account_id, "bio": bio})


        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title = "Random bio(s)"
        )

        # make fields for bios
        for x in bio_list:
            account_id = x["account_id"]
            username = functions.id_to_username(account_id)
            display_name = functions.id_to_display_name(account_id)
            bio = x["bio"]
            embed.add_field(name=f"👤 {display_name} @{username}", value=f"```{bio}```[🔗Profile](https://rec.net/user/{username})", inline=False)

        functions.embed_footer(ctx, embed) # get default footer from function
        await loading.delete()
        m = await ctx.send(
            embed=embed,
            components=self.buttons['default']
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled'])

        if res.component.label == "Redo":
            await m.edit(
                components=self.buttons['disabled']
            )
            await self.randombio(ctx, amount)


    # CMD-CRINGEBIO
    @commands.command(aliases=["cb", "cbio"])
    @commands.check(functions.beta_tester)
    async def cringebio(self, ctx, amount=1):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        if amount > 20:
            amount = 20
        elif amount < 1:
            amount = 1

        bio_list = []

        try:
            with open('cringe_bios.json') as data_file:
                cringe_bio_list = json.load(data_file)
                for x in range(amount):
                    random_bio = cringe_bio_list[random.randint(0, len(cringe_bio_list)-1)]
                    bio_list.append({"account_id": random_bio[0], "bio": random_bio[1]})
        except:
            return await ctx.send("Corrupted...........................")

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title = "Possible cringe bio(s)"
        )

        # make fields for bios
        for bio in bio_list:
            account_id = bio["account_id"]
            username = functions.id_to_username(account_id)
            display_name = functions.id_to_display_name(account_id)
            bio = bio["bio"]
            embed.add_field(name=f"👤 **{display_name}** @{username}", value=f"```{bio}```[🔗Profile](https://rec.net/user/{username})", inline=False)

        embed.add_field(name="CHECK IF SOMEONE'S BIO IS CRINGE!", value=f"`.cbc <username>`", inline=False)

        functions.embed_footer(ctx, embed) # get default footer from function
        m = await ctx.send(
            embed=embed,
            components=self.buttons['default']
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled'])

        if res.component.label == "Redo":
            await m.edit(
                components=self.buttons['disabled']
            )
            await self.cringebio(ctx, amount)

    # CMD-FASTRANDOMBIO
    @commands.command(aliases=["frb"])
    @commands.check(functions.beta_tester)
    async def fastrandombio(self, ctx, amount=1):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        if amount > 20:
            amount = 20
        elif amount < 1:
            amount = 1

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title = "Random bio(s)",
        )

        with open('randombio_list.json') as json_file: 
            data = json.load(json_file)
            for x in range(amount): 
                random_bio = random.randint(0, len(data)-1) 
                username = functions.id_to_username(data[random_bio]["account_id"])
                display_name = functions.id_to_display_name(data[random_bio]["account_id"])
                bio = data[random_bio]["bio"]
                embed.add_field(name=f"👤 **{display_name}** @{username}", value=f"```{bio}```[🔗Profile](https://rec.net/user/{username})", inline=False)

        functions.embed_footer(ctx, embed) # get default footer from function
        m = await ctx.send(
            embed=embed,
            components=self.buttons['default']
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled'])

        if res.component.label == "Redo":
            await m.edit(
                components=self.buttons['disabled']
            )
            await self.fastrandombio(ctx, amount)


    # CMD-RANDOMACCOUNT
    @commands.command(aliases=["raccount"])
    @commands.check(functions.beta_tester)
    async def randomaccount(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        account = functions.find_random_account()
        pfp = functions.id_to_pfp(account['accountId'])

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title = f"Random account! @{account['username']}",
        )
        embed.add_field(name="Display name", value=f"`{account['displayName']}`", inline=True)
        embed.add_field(name="Created at", value=f"`{account['createdAt'][:10]}`", inline=True)
        embed.add_field(name="Is junior?", value=f"`{account['isJunior']}`", inline=True)
        embed.add_field(name="Bio", value=f"```{functions.id_to_bio(account['accountId'])}```")
        embed.set_image(url=pfp)
        embed.set_author(name=f"🔗 {account['username']}'s profile", url=f"https://rec.net/user/{account['username']}", icon_url=pfp)

        functions.embed_footer(ctx, embed) # get default footer from function
        m = await ctx.send(
            embed=embed,
            components=self.buttons['default']
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled'])

        if res.component.label == "Redo":
            await m.edit(
                components=self.buttons['disabled']
            )
            await self.randomaccount(ctx)


    # CMD-RANDOMPFP
    @commands.command(aliases=["rpfp"])
    @commands.check(functions.beta_tester)
    async def randompfp(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        pfp = "DefaultProfileImage"
        while pfp == "DefaultProfileImage":
            account = functions.find_random_account()
            pfp = account["profileImage"]

        account_id = account["accountId"]
        username = account["username"]

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title = "Random profile picture!",
            description = f"[🔗 RecNet post](https://rec.net/image/{pfp}) *(might not exist)*"
        )
        embed.set_image(url=f"https://img.rec.net/{pfp}")
        embed.set_author(name=f"🔗 {username}'s profile", url=f"https://rec.net/user/{username}", icon_url=functions.id_to_pfp(account_id))

        functions.embed_footer(ctx, embed) # get default footer from function
        m = await ctx.send(
            embed=embed,
            components=self.buttons['default']
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled'])

        if res.component.label == "Redo":
            await m.edit(
                components=self.buttons['disabled']
            )
            await self.randompfp(ctx)


    # CMD-RANDOMLOADSCREEN
    @commands.command(aliases=["rls"])
    @commands.check(functions.beta_tester)
    async def randomloadscreen(self, ctx, loading_screens=None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        if not loading_screens:
            loading_screens = requests.get("https://cdn.rec.net/config/LoadingScreenTipData").json()
        load_screen = random.choice(loading_screens)
   
        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title = load_screen["Title"],
            description = f"{load_screen['Message']}\n\n*Made in*\n📆 `{load_screen['CreatedAt'][:10]}`\n⏰ `{load_screen['CreatedAt'][11:16]} UTC`"
        )
        embed.set_image(url=f"https://img.rec.net/{load_screen['ImageName']}?width=720")

        functions.embed_footer(ctx, embed) # get default footer from function
        m = await ctx.send(
            embed=embed,
            components=self.buttons['default']
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled'])

        if res.component.label == "Redo":
            await m.edit(
                components=self.buttons['disabled']
            )
            await self.randomloadscreen(ctx, loading_screens)


    # CMD-RANDOMIMG
    @commands.command(aliases=["rimg"])
    @commands.check(functions.beta_tester)
    async def randomimg(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session
        print(self.session_message)

        # LOADING
        embed=discord.Embed(
            colour=discord.Colour.orange(),
            description = f"<a:spinning:804022054822346823> Searching for a random image..."
        )
        functions.embed_footer(ctx, embed)
        loading = await ctx.send(embed=embed)

        random_img = functions.find_random_img()

        embed = functions.image_embed(random_img)

        await loading.delete()

        functions.embed_footer(ctx, embed)  # get default footer from function
        m = await ctx.send(
            f"Random image",
            embed=embed,
            components=self.buttons['default']
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled'])

        if res.component.label == "Redo":
            await m.edit(
                components=self.buttons['disabled']
            )
            await self.randomimg(ctx)


    # CMD-RANDOMROOM
    @commands.command(aliases=["rroom"])
    @commands.check(functions.beta_tester)
    async def randomroom(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            description = f"<a:spinning:804022054822346823> Searching for a random room..."
        )
        functions.embed_footer(ctx, embed)
        loading = await ctx.send(embed=embed)

        room = functions.find_random_room()
        room_embed = functions.room_embed(room, True)

        functions.embed_footer(ctx, room_embed)  # get default footer from function

        await loading.delete()
        m = await ctx.send(
            embed=room_embed,
            components=self.buttons['default']
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled'])

        if res.component.label == "Redo":
            await m.edit(
                components=self.buttons['disabled']
            )
            await self.randomroom(ctx)

    @randomroom.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        raise error


    # CMD-RANDOMEVENT
    @commands.command(aliases=["revent"])
    @commands.check(functions.beta_tester)
    async def randomevent(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        event = functions.find_random_event()
        event_creator = functions.id_to_username(event['CreatorPlayerId'])
        event_description = event['Description']
        try:
            event_room = f"[^{functions.get_room_json(event['RoomId'], True)['Name']}](https://rec.net/room/{functions.get_room_json(event['RoomId'], True)['Name']})"
        except:
            event_room = "`Dorm room`"
        if not event["Description"]:
            event_description = "None"

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title = f"{event['Name'] }",
            description = f"**Description**```{event_description}```\n**Information**\n🚪 Room: {event_room}\n👥 Attendees: `{event['AttendeeCount']}`\n📆 Start time: `{event['StartTime'][:10]}`, at ⏰ `{event['StartTime'][11:16]} UTC`\n🚷 End time: `{event['EndTime'][:10]}`, at ⏰ `{event['EndTime'][11:16]} UTC`",
            url=f"https://rec.net/event/{event['PlayerEventId']}"
        )

        embed.set_author(name=f"🔗 {event_creator}'s profile", url=f"https://rec.net/user/{event_creator}", icon_url=functions.id_to_pfp(event['CreatorPlayerId']))
        embed.set_image(url=f"https://img.rec.net/{event['ImageName']}?width=720")
        functions.embed_footer(ctx, embed) # get default footer from function
        m = await ctx.send(
            embed=embed,
            components=self.buttons['default']
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled'])

        if res.component.label == "Redo":
            await m.edit(
                components=self.buttons['disabled']
            )
            await self.randomevent(ctx)


    # CMD-RANDOMIMGOF
    @commands.command(aliases=["rimgof", "rio"])
    @commands.check(functions.beta_tester)
    async def randomimgof(self, ctx, profile, feed=None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        if feed:
            random_feed = random.choice(feed)
            embed = functions.image_embed(random_feed)
        else:
            account = functions.check_account_existence_and_return(profile)
            if account:
                profile = account['username']
                feed = functions.id_to_feed(account['account_id'])

                if feed:
                    random_feed = random.choice(feed)

                    embed = functions.image_embed(random_feed)
                else:
                    embed = functions.error_msg(ctx, f"User `@{profile}` doesn't appear in any post!")
            else:
                embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed)  # get default footer from function
        m = await ctx.send(
            f"Random image of `@{profile}`",
            embed=embed,
            components=self.buttons['default']
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled'])

        if res.component.label == "Redo":
            await m.edit(
                components=self.buttons['disabled']
            )
            await self.randomimgof(ctx, profile, feed)

    @randomimgof.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass

    # CMD-RANDOMIMGBY
    @commands.command(aliases=["rimgby", "rib"])
    @commands.check(functions.beta_tester)
    async def randomimgby(self, ctx, profile, photos=None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        if photos:
            random_photos = random.choice(photos)
            embed = functions.image_embed(random_photos)
        else:
            account = functions.check_account_existence_and_return(profile)
            if account:
                profile = account['username']
                photos = functions.id_to_photos(account['account_id'])

                if photos:
                    random_photos = random.choice(photos)
                    embed = functions.image_embed(random_photos)

                else:
                    embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single post!")
            else:
                embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed) # get default footer from function
        m = await ctx.send(
            f"Random image by `@{profile}`",
            embed=embed,
            components=self.buttons['default']
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled'])

        if res.component.label == "Redo":
            await m.edit(
                components=self.buttons['disabled']
            )
            await self.randomimgby(ctx, profile, photos)

    @randomimgby.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass
  
    # CMD-RANDOMIMGBYIN
    @commands.command(aliases=["rimgbyin", "ribi"])
    @commands.check(functions.beta_tester)
    async def randomimgbyin(self, ctx, profile, room_name, found_photos=None, room=None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        if found_photos:
            random_photos = random.choice(found_photos)

            embed = functions.image_embed(random_photos)
        else:
            account = functions.check_account_existence_and_return(profile)
            if account:
                profile = account['username']
                room = functions.get_room_json(room_name)
                if room:
                    photos = functions.id_to_photos(account['account_id'])

                    if photos:
                        found_photos = []
                        # find photos in room
                        for photo in photos:
                            if photo['RoomId'] == room['RoomId']:
                                found_photos.append(photo)

                        if found_photos:
                            random_photos = found_photos[random.randint(0, len(found_photos)-1)]

                            embed = functions.image_embed(random_photos)
                        else:
                            embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single post in `^{room['Name']}`!")
                    else:
                        embed = functions.error_msg(ctx, f"User `@{account['username']}` hasn't shared a single post!")
                else:
                    embed = functions.error_msg(ctx, f"Room `^{room_name}` doesn't exist!")
            else:
                embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed) # get default footer from function
        m = await ctx.send(
            f"Random image by `@{profile}`, in `^{room['Name']}`",
            embed=embed,
            components=self.buttons['default']
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled'])

        if res.component.label == "Redo":
            await m.edit(
                components=self.buttons['disabled']
            )
            await self.randomimgbyin(ctx, profile, room_name, found_photos, room)

    @randomimgbyin.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username and room!\nUsage: `.randomimgbyin <user> <room>`")
            
            await ctx.send(embed=embed)
        else:
            pass


    # CMD-RANDOMIMGOFIN
    @commands.command(aliases=["rimgofin", "rioi"])
    @commands.check(functions.beta_tester)
    async def randomimgofin(self, ctx, profile, room_name, found_photos=None, room=None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        if found_photos:
            random_photos = random.choice(found_photos)
            embed = functions.image_embed(random_photos)
        else:
            account = functions.check_account_existence_and_return(profile)
            if account:
                profile = account['username']
                room = functions.get_room_json(room_name)
                if room:
                    photos = functions.id_to_feed(account['account_id'])

                    if photos:
                        found_photos = []
                        # find photos in room
                        for photo in photos:
                            if photo['RoomId'] == room['RoomId']:
                                found_photos.append(photo)

                        if found_photos:
                            random_photos = random.choice(found_photos)

                            embed = functions.image_embed(random_photos)
                        else:
                            embed = functions.error_msg(ctx, f"User `@{account['username']}` doesn't appear in `^{room['Name']}`!")
                    else:
                        embed = functions.error_msg(ctx, f"User `@{profile}` doesn't appear in `^{room_name}` at all!")
                else:
                    embed = functions.error_msg(ctx, f"Room `^{room_name}` doesn't exist!")
            else:
                embed = functions.error_msg(ctx, f"User `@{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed) # get default footer from function
        m = await ctx.send(
            f"Random image of `@{profile}`, in `^{room['Name']}`",
            embed=embed,
            components=self.buttons['default']
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled'])

        if res.component.label == "Redo":
            await m.edit(
                components=self.buttons['disabled']
            )
            await self.randomimgofin(ctx, profile, room_name, found_photos, room)


    @randomimgofin.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username and room!\nUsage: `.randomimgofin <user> <room>`")
            
            await ctx.send(embed=embed)
        else:
            pass


    # CMD-RANDOMIMGIN
    @commands.command(aliases=["rimgin", "rii"])
    @commands.check(functions.beta_tester)
    async def randomimgin(self, ctx, room_name, room_photos=None, room=None):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        m_session = random.randint(0, 999999)
        self.session_message[ctx.author.id] = m_session

        if room_photos:
            random_photo = random.choice(room_photos)

            embed = functions.image_embed(random_photo)
        else:
            room = functions.get_room_json(room_name)
            if room:

                embed=discord.Embed(
                    colour=discord.Colour.orange(),
                    description = f"<a:spinning:804022054822346823> Loading >10,000 pictures taken in `^{room['Name']}`, and picking one randomly..."
                )
                functions.embed_footer(ctx, embed)
                loading = await ctx.send(embed=embed)

                room_photos = functions.get_photos_in_room(room_name)
                if room_photos:
                    random_photo = random.choice(room_photos)

                    embed = functions.image_embed(random_photo)
                else:
                    embed = functions.error_msg(ctx, f"Not a single picture has been taken in `^{room['Name']}`")
            else:
                embed = functions.error_msg(ctx, f"Room `^{room_name}` doesn't exist!")

        try:
            await loading.delete()
        except:
            pass
        functions.embed_footer(ctx, embed) # get default footer from function
        m = await ctx.send(
            f"Random image in `^{room['Name']}`",
            embed=embed,
            components=self.buttons['default']
        )

        def check(res):
            return ctx.author == res.user and res.channel == ctx.channel and self.session_message[ctx.author.id] == m_session

        try:
            res = await self.client.wait_for("button_click", check=check, timeout=30)
            await res.respond(type=6)
        except:
            return await m.edit(components=self.buttons['disabled'])

        if res.component.label == "Redo":
            await m.edit(
                components=self.buttons['disabled']
            )
            await self.randomimgin(ctx, room_name, room_photos, room)

    @randomimgin.error
    async def clear_error(self, ctx, error):
        await functions.report_error(ctx, error, self.client.get_channel(functions.error_channel))
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in a room!")
            
            await ctx.send(embed=embed)
        else:
            pass

        
def setup(client):
    client.add_cog(Random(client))