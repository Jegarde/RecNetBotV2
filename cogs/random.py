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
            description = f"<a:spinning:804022054822346823> Searching for {amount} random bio(s)..."
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
            description = f"<a:spinning:804022054822346823> Searching for {amount} random image(s)..."
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
            description = f"<a:spinning:804022054822346823> Searching for a random room..."
        )
        functions.embed_footer(ctx, embed)
        loading = await ctx.send(embed=embed)

        room = functions.find_random_room()
        room_embed = functions.room_embed(room, True)

        functions.embed_footer(ctx, room_embed) # get default footer from function

        await loading.delete()
        await ctx.send(author, embed=room_embed)


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


    # CMD-RANDOMIMGOF
    @commands.command(aliases=["rimgof", "rio"])
    @commands.check(functions.beta_tester)
    async def randomimgof(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if account:
            feed = functions.id_to_feed(account['account_id'])
            
            if feed:
                random_feed = feed[random.randint(0, len(feed)-1)]
                username = functions.id_to_username(account['account_id'])
                tagged = ""
                if random_feed['TaggedPlayerIds']:
                    tagged = "👥 "
                    for account_id in random_feed['TaggedPlayerIds']:
                        tagged_username = functions.id_to_username(account_id)
                        tagged += f"[`@{tagged_username}`](https://rec.net/user/{tagged_username}) "
                
                room_name = functions.id_to_room_name(random_feed['RoomId'])
                embed=discord.Embed(
                    colour=discord.Colour.orange(),
                    title=f"Random image of @{username}, taken by @{functions.id_to_username(random_feed['PlayerId'])}",
                    description=f"🔗 **[RecNet post](https://rec.net/image/{random_feed['Id']})**\n🚪 [`^{room_name}`](https://rec.net/room/{room_name})\n<:CheerGeneral:803244099510861885> `{random_feed['CheerCount']}` 💬 `{random_feed['CommentCount']}`\n📆 `{random_feed['CreatedAt'][:10]}` ⏰ `{random_feed['CreatedAt'][11:16]} UTX`\n{tagged}"
                )
                embed.set_image(url=f"https://img.rec.net/{random_feed['ImageName']}")
                embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=functions.id_to_pfp(account['account_id']))
            else:
                embed = functions.error_msg(ctx, f"User `{profile}` doesn't appear in any post!")
        else:
            embed = functions.error_msg(ctx, f"User `{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @randomimgof.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass


    # CMD-RANDOMIMGBY
    @commands.command(aliases=["rimgby", "rib"])
    @commands.check(functions.beta_tester)
    async def randomimgby(self, ctx, profile):
        functions.log(ctx.guild.name, ctx.author, ctx.command)

        account = functions.check_account_existence_and_return(profile)
        if account:
            photos = functions.id_to_photos(account['account_id'])
            
            if photos:
                random_photos = photos[random.randint(0, len(photos)-1)]
                username = functions.id_to_username(account['account_id'])
                tagged = ""
                if random_photos['TaggedPlayerIds']:
                    tagged = "👥 "
                    for account_id in random_photos['TaggedPlayerIds']:
                        tagged_username = functions.id_to_username(account_id)
                        tagged += f"[`@{tagged_username}`](https://rec.net/user/{tagged_username}) "
                
                room_name = functions.id_to_room_name(random_photos['RoomId'])
                embed=discord.Embed(
                    colour=discord.Colour.orange(),
                    title=f"Random image taken by @{username}",
                    description=f"🔗 **[RecNet post](https://rec.net/image/{random_photos['Id']})**\n🚪 [`^{room_name}`](https://rec.net/room/{room_name})\n<:CheerGeneral:803244099510861885> `{random_photos['CheerCount']}` 💬 `{random_photos['CommentCount']}`\n📆 `{random_photos['CreatedAt'][:10]}` ⏰ `{random_photos['CreatedAt'][11:16]} UTX`\n{tagged}"
                )
                embed.set_image(url=f"https://img.rec.net/{random_photos['ImageName']}")
                embed.set_author(name=f"{username}'s profile", url=f"https://rec.net/user/{username}", icon_url=functions.id_to_pfp(account['account_id']))
            else:
                embed = functions.error_msg(ctx, f"User `{profile}` hasn't shared a single post!")
        else:
            embed = functions.error_msg(ctx, f"User `{profile}` doesn't exist!")

        functions.embed_footer(ctx, embed) # get default footer from function
        await ctx.send(embed=embed)

    @randomimgof.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = functions.error_msg(ctx, "Please include in an username!")
            
            await ctx.send(embed=embed)
        else:
            pass

        
def setup(client):
    client.add_cog(Random(client))