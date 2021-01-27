import functions
import requests
import discord
import random
import json
from discord.ext import commands

class Random(commands.Cog):
    def __init__(self, client):
        self.client = client
    # RANDOM COMMANDS

    # CMD-RANDOMBIO
    @commands.command(aliases=["rb", "rbio"])
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


    # CMD-RANDOMACCOUNT
    @commands.command(aliases=["raccount"])
    @commands.check(functions.beta_tester)
    async def randomaccount(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        
        author = f"<@{ctx.author.id}>"

        account = functions.find_random_account()
        account_id = account["accountId"]
        username = account["username"]
        display_name = account["displayName"]
        created_at = account["createdAt"][:10]
        junior = account["isJunior"]
        pfp = functions.id_to_pfp(account_id)

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title = f"Random account! @{username}",
        )
        embed.add_field(name="Display name", value=f"`{display_name}`", inline=True)
        embed.add_field(name="Created at", value=f"`{created_at}`", inline=True)
        embed.add_field(name="Is junior?", value=f"`{junior}`", inline=True)
        embed.add_field(name="Bio", value=f"```{functions.id_to_bio(account_id)}```")
        embed.set_image(url=pfp)
        embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=pfp)

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(author, embed=embed)


    # CMD-RANDOMPFP
    @commands.command(aliases=["rpfp"])
    @commands.check(functions.beta_tester)
    async def randompfp(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        
        author = f"<@{ctx.author.id}>"

        pfp = "DefaultProfileImage"
        while pfp == "DefaultProfileImage":
            account = functions.find_random_account()
            pfp = account["profileImage"]

        account_id = account["accountId"]
        username = account["username"]

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title = f"Random profile picture!",
            description = f"[🔗 RecNet post](https://rec.net/image/{pfp}) *(might not exist)*"
        )
        embed.set_image(url=f"https://img.rec.net/{pfp}")
        embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=functions.id_to_pfp(account_id))

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(author, embed=embed)


    # CMD-RANDOMLOADSCREEN
    @commands.command(aliases=["rls"])
    @commands.check(functions.beta_tester)
    async def randomloadscreen(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        
        author = f"<@{ctx.author.id}>"

        loading_screens = requests.get("https://cdn.rec.net/config/LoadingScreenTipData").json()
        load_screen = loading_screens[random.randint(0, len(loading_screens)-1)]
        load_screen_img = load_screen["ImageName"]
        load_screen_msg = load_screen["Message"]
        load_screen_created_at = load_screen["CreatedAt"]

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title = load_screen["Title"],
            description = f"{load_screen_msg}\n\n*Made in*\n📆 `{load_screen_created_at[:10]}`\n⏰ `{load_screen_created_at[11:16]} UTX`"
        )
        embed.set_image(url=f"https://img.rec.net/{load_screen_img}?width=720")

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(author, embed=embed)

    
    # CMD-RANDOMIMG
    @commands.command(aliases=["rimg"])
    @commands.check(functions.beta_tester)
    async def randomimg(self, ctx, amount=1):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        
        author = f"<@{ctx.author.id}>"

        if amount > 5:
            amount = 5
        elif amount < 1:
            amount = 1

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            description = f"<a:spinning:803586183895580672> Searching for {amount} random image(s)..."
        )
        functions.embed_footer(ctx, embed)
        loading = await ctx.send(embed=embed)

        img_string = ""
        for x in range(amount):
            random_img = functions.find_random_img()
            img_id = random_img["Id"]
            img_cheers = random_img["CheerCount"]
            img_comments = random_img["CommentCount"]
            img_username = functions.id_to_username(random_img["PlayerId"])
            img_string += f"https://rec.net/image/{img_id}\n**@{img_username}**\n<:CheerGeneral:803244099510861885> `{img_cheers}` 💬 `{img_comments}`\n\n"

        await loading.delete()
        await ctx.send(f"{author}\n{img_string}")

    # CMD-RANDOMROOM
    @commands.command(aliases=["rroom"])
    @commands.check(functions.beta_tester)
    async def randomroom(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        
        author = f"<@{ctx.author.id}>"

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            description = f"<a:spinning:803586183895580672> Searching for a random room..."
        )
        functions.embed_footer(ctx, embed)
        loading = await ctx.send(embed=embed)

        room = functions.find_random_room()
        r_name = room["Name"]
        
        # Roles
        owner_username = functions.id_to_username(room["CreatorAccountId"])
        owner_pfp = functions.id_to_pfp(room["CreatorAccountId"])
        role_count = len(room["Roles"])
        
        # Placement
        placement = functions.get_room_placement(r_name)
        if placement == None:
            placement = "<1000"

        # Stats
        cheers = room["Stats"]["CheerCount"]
        favorites = room["Stats"]["FavoriteCount"]
        visitor_count = room["Stats"]["VisitorCount"]
        visit_count = room["Stats"]["VisitCount"]

        visitor_cheer_ratio = round((cheers / visitor_count) * 100)
        visit_visitor_ratio = round((visitor_count / visit_count) * 100)
        
        # Subrooms
        subrooms = ""
        for i in room["SubRooms"]:
            subroom_name = i["Name"]
            subrooms += f"{subroom_name}, "

        # Other
        image_name = room["ImageName"]
        description = room["Description"]
        r_date = room["CreatedAt"][:10]

        # Warning
        custom_warning = room["CustomWarning"]
        if custom_warning:
            custom_warning = f"\n**Custom warning**\n```{custom_warning}```"
        else:
            custom_warning = ""
        supported = ""
        if room["SupportsWalkVR"]:
            supported += " 🏃‍♂️ "
        if room["SupportsTeleportVR"]:
            supported += " <:RRtele:803747393769570324> "
        if room["SupportsVRLow"]:
            supported += " <:OQ1:803932601768476672> "
        if room["SupportsQuest2"]:
            supported += " <:OQ2:803932151971577896> "
        if room["SupportsScreens"]:
            supported += " 🖥️ "
        if room["SupportsMobile"]:
            supported += " 📱 "
        if room["SupportsJuniors"]:
            supported += " 👶 "

        # Tags
        tags = ""
        for i in room["Tags"]:
            tags += "#" + str(i["Tag"]) + " "

        # Score
        avg_score = 0
        score_list = []
        for i in room["Scores"]:
            if not i["VisitType"] == 2:
                print(i)
                score_list.append(i["Score"])
                avg_score += i["Score"]
        print(len(score_list))
        print(avg_score)
        avg_score = round(avg_score / len(score_list), 5)

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title = f"Statistics for ^{r_name}, by @{owner_username}",
            description = f"[🔗 RecNet Page](https://rec.net/room/{r_name})\n\n**Description**\n```{description}```\n{custom_warning}**Information**\n:calendar: `{r_date}`\n<:CheerHost:803753879497998386> `{role_count}` *(USERS WITH A ROLE)*\n🚪 `{subrooms}`\n<:tag:803746052946919434> `{tags}`\n\n**Supported modes**\n{supported}\n\n**Statistics**\n<:CheerGeneral:803244099510861885> `{cheers}` *(CHEERS)*\n⭐ `{favorites}` *(FAVORITES)*\n👤 `{visitor_count}` *(VISITORS)*\n👥 `{visit_count}` *(ROOM VISITS)*\n🔥 `#{placement}` *(HOT PLACEMENT)*\n💯 `{avg_score}` *(AVG SCORE)*"
        )
        print("oimg")
        embed.set_image(url=f"https://img.rec.net/{image_name}?width=720")
        
        # description
        #embed.add_field(name="⠀",value=f"**Description**\n```{description}```:calendar: `{date}`\n\n**Statistics**\n<:CheerGeneral:803244099510861885> `{cheers}` ⭐ `{favorites}` 👤 `{visitor_count}` 👥 `{visit_count}`\nAvg score: `{avg_score}`")
        
        print("author")
        embed.set_author(name=f"{owner_username}'s profile", url=f"https://rec.net/user/{owner_username}", icon_url=owner_pfp)

        functions.embed_footer(ctx, embed) # get default footer from function

        await loading.delete()
        await ctx.send(author, embed=embed)


    # CMD-RANDOMEVENT
    @commands.command(aliases=["revent"])
    @commands.check(functions.beta_tester)
    async def randomevent(self, ctx):
        functions.log(ctx.guild.name, ctx.author, ctx.command)
        
        author = f"<@{ctx.author.id}>"

        event = functions.find_random_event()
        event_name = event["Name"] 
        event_creator = functions.id_to_username(event["CreatorPlayerId"])
        event_account_id = event["CreatorPlayerId"]
        event_id = event["PlayerEventId"]
        event_description = event["Description"]
        try:
            event_room = f"[^{functions.get_room_json(event['RoomId'], True)['Name']}](https://rec.net/room/{functions.get_room_json(event['RoomId'], True)['Name']})"
        except:
            event_room = "`Dorm room`"
        if not event["Description"]:
            event_description = "None"
        event_img = event["ImageName"]
        event_start = event["StartTime"]
        event_end = event["EndTime"]
        event_attendees = event["AttendeeCount"]

        embed=discord.Embed(
            colour=discord.Colour.orange(),
            title = f"{event_name}",
            description = f"**Description**```{event_description}```\n**Information**\n🚪 Room: {event_room}\n👥 Attendees: `{event_attendees}`\n📆 Start time: `{event_start[:10]}`, at ⏰ `{event_start[11:16]} UTX`\n🚷 End time: `{event_end[:10]}`, at ⏰ `{event_end[11:16]} UTX`",
            url=f"https://rec.net/event/{event_id}"
        )

        embed.set_author(name=f"{event_creator}'s profile", url=f"https://rec.net/user/{event_creator}", icon_url=functions.id_to_pfp(event_account_id))
        embed.set_image(url=f"https://img.rec.net/{event_img}?width=720")
        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(author, embed=embed)

        
def setup(client):
    client.add_cog(Random(client))